#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any, Sequence

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

# logger
LOG = logging.getLogger("shap_models_analysis")


# configure logging level
# verbose=True gives debug logs, otherwise normal info logs
def setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

# load input data
# csv files are expected to use semicolon separator
def read_table(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Data file does not exist: {path}")

    suffixes = "".join(path.suffixes).lower()
    LOG.info("Loading data from %s", path)

    if suffixes.endswith(".csv"):
        return pd.read_csv(path, sep=";")
    if suffixes.endswith(".csv.gz"):
        return pd.read_csv(path, sep=";", compression="gzip")
    if suffixes.endswith(".parquet"):
        return pd.read_parquet(path)
    if suffixes.endswith(".feather"):
        return pd.read_feather(path)

    raise ValueError(
        f"Unsupported file format for {path}. Use CSV, CSV.GZ, Parquet, or Feather."
    )

# create directory if it does not exist yet
def safe_mkdir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

# convert numpy / pandas objects to normal python objects before saving json
def stringify(obj: Any) -> Any:
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    if isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (pd.Series, pd.Index)):
        return obj.tolist()
    if isinstance(obj, Path):
        return str(obj)
    return obj


def save_json(data: dict[str, Any], path: str | Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=stringify)

# try to recover feature names from model / booster
def extract_feature_names_from_model(model: Any) -> list[str] | None:
    feature_names = getattr(model, "feature_names_in_", None)
    if feature_names is not None:
        return [str(x) for x in feature_names]

    get_booster = getattr(model, "get_booster", None)
    if callable(get_booster):
        try:
            booster = get_booster()
            booster_feature_names = getattr(booster, "feature_names", None)
            if booster_feature_names:
                return [str(x) for x in booster_feature_names]
        except Exception as exc:
            LOG.warning("Could not extract booster feature names: %s", exc)

    return None

# reorder dataframe columns to match model input features
# also catches missing columns early instead of failing later in model.predict()
def align_features_to_model(model: Any, df: pd.DataFrame) -> pd.DataFrame:
    feature_names = extract_feature_names_from_model(model)
    if feature_names is None:
        LOG.warning(
            "Model does not expose feature names. Using all provided columns from the input data."
        )
        return df.copy()

    missing = [c for c in feature_names if c not in df.columns]
    extras = [c for c in df.columns if c not in feature_names]

    if missing:
        raise ValueError(
            "Provided data is missing columns required by the model: "
            + ", ".join(missing[:25])
            + (" ..." if len(missing) > 25 else "")
        )

    if extras:
        LOG.info("Ignoring %d extra columns not used by the model.", len(extras))

    return df.loc[:, feature_names].copy()

# optionally sample rows for faster SHAP computation
def sample_frame(df: pd.DataFrame, sample_size: int | None, random_state: int) -> pd.DataFrame:
    if sample_size is None or sample_size <= 0:
        return df.copy()
    if len(df) <= sample_size:
        return df.copy()
    return df.sample(n=sample_size, random_state=random_state).copy()

# get model scores
# for classifiers use probability of positive class, otherwise fallback to predict()
def get_predictions(model: Any, X: pd.DataFrame) -> np.ndarray:
    predict_proba = getattr(model, "predict_proba", None)
    if callable(predict_proba):
        try:
            proba = predict_proba(X)
            if isinstance(proba, np.ndarray) and proba.ndim == 2 and proba.shape[1] >= 2:
                return proba[:, 1]
            return np.asarray(proba).reshape(-1)
        except Exception as exc:
            LOG.warning("predict_proba failed, falling back to predict(): %s", exc)

    pred = model.predict(X)
    pred = np.asarray(pred)
    if pred.ndim > 1:
        pred = pred[:, 0]
    return pred.reshape(-1)

# make SHAP output one-dimensional for binary / multi-output models
# if SHAP returns values for multiple classes, keep positive class output
def normalize_shap_output(explanation: shap.Explanation) -> shap.Explanation:
    values = explanation.values
    base_values = explanation.base_values
    data = explanation.data
    feature_names = explanation.feature_names

    if isinstance(values, np.ndarray) and values.ndim == 3:
        class_idx = 1 if values.shape[2] > 1 else 0
        LOG.warning(
            "SHAP values are multi-output with shape %s. Using output index %d.",
            values.shape,
            class_idx,
        )
        if isinstance(base_values, np.ndarray):
            if base_values.ndim == 2:
                base_values = base_values[:, class_idx]
            elif base_values.ndim == 1 and len(base_values) > class_idx:
                base_values = base_values[class_idx]
        return shap.Explanation(
            values=values[:, :, class_idx],
            base_values=base_values,
            data=data,
            feature_names=feature_names,
        )

    return explanation

# split sklearn pipeline into preprocessing and final model
def get_pipeline_parts(model: Any) -> tuple[Any, Any]:
    named_steps = getattr(model, "named_steps", None)
    if named_steps is None:
        raise ValueError("Expected a sklearn Pipeline with named_steps.")
    if "preprocessor" not in named_steps or "model" not in named_steps:
        raise ValueError("Pipeline must contain 'preprocessor' and 'model' steps.")
    return named_steps["preprocessor"], named_steps["model"]

# get names of transformed columns after preprocessing
# SHAP explains transformed features, not raw csv columns
def get_transformed_feature_names(preprocessor: Any) -> list[str]:
    get_names = getattr(preprocessor, "get_feature_names_out", None)
    if callable(get_names):
        return [str(x) for x in get_names()]
    raise ValueError("Preprocessor does not expose get_feature_names_out().")


# plot helper

# save current matplotlib figure and close it, so plots do not stack on each other
def save_current_figure(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches="tight")
    plt.close()

# global feature importance plot based on mean absolute SHAP values
def plot_bar(shap_values: shap.Explanation, path: Path, max_display: int) -> None:
    plt.figure(figsize=(10, 6))
    shap.plots.bar(shap_values, max_display=max_display, show=False)
    save_current_figure(path)

# beeswarm plot: shows both feature importance and direction of effect
def plot_beeswarm(shap_values: shap.Explanation, path: Path, max_display: int) -> None:
    plt.figure(figsize=(11, 7))
    shap.plots.beeswarm(shap_values, max_display=max_display, show=False)
    save_current_figure(path)

# violin plot: distribution of SHAP values per feature
def plot_violin(shap_values: shap.Explanation, path: Path, max_display: int) -> None:
    plt.figure(figsize=(11, 7))
    shap.plots.violin(shap_values, max_display=max_display, show=False)
    save_current_figure(path)

# waterfall plot for one row / one prediction
# useful to see why model gave low, median, or high score
def plot_waterfall(single_explanation: shap.Explanation, path: Path, max_display: int) -> None:
    plt.figure(figsize=(10, 7))
    shap.plots.waterfall(single_explanation, max_display=max_display, show=False)
    save_current_figure(path)

# dependence scatter plot for one feature
# optional color shows interaction with another feature
def plot_scatter(
    shap_values: shap.Explanation,
    feature_name: str,
    path: Path,
    color: shap.Explanation | str | None = None,
) -> None:
    plt.figure(figsize=(9, 6))
    if color is None:
        shap.plots.scatter(shap_values[:, feature_name], show=False)
    else:
        shap.plots.scatter(shap_values[:, feature_name], color=color, show=False)
    save_current_figure(path)


# analysis core
# build table with feature-level SHAP statistics
def build_feature_summary(shap_values: shap.Explanation, X: pd.DataFrame) -> pd.DataFrame:
    mean_abs = np.abs(shap_values.values).mean(axis=0)
    mean_raw = shap_values.values.mean(axis=0)
    std_raw = shap_values.values.std(axis=0)
    feature_mean = X.mean(axis=0).to_numpy()
    feature_std = X.std(axis=0).fillna(0.0).to_numpy()

    summary = pd.DataFrame(
        {
            "feature": X.columns,
            "mean_abs_shap": mean_abs,
            "mean_shap": mean_raw,
            "std_shap": std_raw,
            "feature_mean": feature_mean,
            "feature_std": feature_std,
        }
    ).sort_values("mean_abs_shap", ascending=False)

    total = summary["mean_abs_shap"].sum()
    summary["importance_share"] = 0.0 if total == 0 else summary["mean_abs_shap"] / total
    return summary.reset_index(drop=True)

# find approximate interaction partners for top features
def build_interaction_summary(
    shap_values: shap.Explanation,
    X: pd.DataFrame,
    top_features: Sequence[str],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for feature_name in top_features:
        feature_idx = X.columns.get_loc(feature_name)
        try:
            interaction_order = shap.utils.approximate_interactions(
                feature_idx,
                shap_values.values,
                X,
            )
            partners = [X.columns[int(i)] for i in interaction_order if int(i) != feature_idx]
            top_partner = partners[0] if partners else None
            rows.append(
                {
                    "feature": feature_name,
                    "top_interaction_feature": top_partner,
                    "top_3_interactions": partners[:3],
                }
            )
        except Exception as exc:
            LOG.warning("Could not compute interaction partner for %s: %s", feature_name, exc)
            rows.append(
                {
                    "feature": feature_name,
                    "top_interaction_feature": None,
                    "top_3_interactions": [],
                }
            )
    return pd.DataFrame(rows)

# choose examples for waterfall plots
# lowest, middle, and highest prediction give a nice spread of model behavior
def choose_waterfall_indices(preds: np.ndarray) -> dict[str, int]:
    order = np.argsort(preds)
    return {
        "lowest_prediction": int(order[0]),
        "median_prediction": int(order[len(order) // 2]),
        "highest_prediction": int(order[-1]),
    }

# run full SHAP analysis for one model directory
# loads model, prepares data, computes SHAP, saves plots/tables/report
def explain_model(
    model_dir: Path,
    data_path: Path,
    output_root: Path,
    sample_size: int,
    max_display: int,
    top_k_dependence: int,
    random_state: int,
    drop_columns: Sequence[str],
) -> dict[str, Any]:
    model_name = model_dir.name
    model_path = model_dir / "best_model.joblib"
    if not model_path.exists():
        raise FileNotFoundError(f"Missing model file: {model_path}")
    
    # create output folders for this model
    model_output_dir = safe_mkdir(output_root / model_name)
    plots_dir = safe_mkdir(model_output_dir / "plots")
    tables_dir = safe_mkdir(model_output_dir / "tables")

    # load fitted pipeline and split it into preprocessor + xgboost model
    LOG.info("Loading model: %s", model_path)
    pipeline = joblib.load(model_path)
    preprocessor, xgb_model = get_pipeline_parts(pipeline)

    # load input data and remove columns that are not model features
    raw_df = read_table(data_path)
    X_raw = raw_df.drop(columns=[c for c in drop_columns if c in raw_df.columns], errors="ignore").copy()
    X_raw = align_features_to_model(pipeline, X_raw)

    if X_raw.empty:
        raise ValueError(f"No usable input columns remain for model {model_name}.")

    # sample rows and calculate predictions for the sampled data
    X_sample_raw = sample_frame(X_raw, sample_size=sample_size, random_state=random_state)
    preds = get_predictions(pipeline, X_sample_raw)

    # transform raw columns into the exact matrix seen by the final model
    LOG.info("Transforming features for model %s ...", model_name)
    X_sample_transformed = preprocessor.transform(X_sample_raw)
    if hasattr(X_sample_transformed, "toarray"):
        X_sample_transformed = X_sample_transformed.toarray()

    feature_names = get_transformed_feature_names(preprocessor)
    X_transformed_df = pd.DataFrame(
        X_sample_transformed,
        columns=feature_names,
        index=X_sample_raw.index,
    )

    # compute SHAP values on transformed features
    LOG.info(
        "Explaining %s on %d rows and %d transformed features ...",
        model_name,
        len(X_sample_raw),
        X_transformed_df.shape[1],
    )
    explainer = shap.Explainer(xgb_model, X_transformed_df)
    shap_values = explainer(X_transformed_df)
    shap_values = normalize_shap_output(shap_values)

    # build feature importance table + approximate interaction info
    feature_summary = build_feature_summary(shap_values, X_transformed_df)
    top_features = feature_summary.head(top_k_dependence)["feature"].tolist()
    interaction_summary = build_interaction_summary(shap_values, X_transformed_df, top_features)
    feature_summary = feature_summary.merge(interaction_summary, on="feature", how="left")

    # keep sampled raw rows together with prediction scores
    sampled_with_preds = X_sample_raw.copy()
    sampled_with_preds["__prediction__"] = preds

    # save tables for later inspection / README / thesis tables
    feature_summary_path = tables_dir / "feature_summary.csv"
    sampled_preds_path = tables_dir / "sampled_predictions.csv"
    transformed_sample_path = tables_dir / "sampled_transformed_features.csv.gz"
    feature_summary.to_csv(feature_summary_path, index=False)
    sampled_with_preds.to_csv(sampled_preds_path, index=False)
    X_transformed_df.to_csv(transformed_sample_path, index=False, compression="gzip")

    # save global SHAP plots
    plot_bar(shap_values, plots_dir / "shap_bar.png", max_display=max_display)
    plot_beeswarm(shap_values, plots_dir / "shap_beeswarm.png", max_display=max_display)
    plot_violin(shap_values, plots_dir / "shap_violin.png", max_display=max_display)

    # save local explanation plots for low / median / high prediction examples
    wf_indices = choose_waterfall_indices(preds)
    for label, idx in wf_indices.items():
        plot_waterfall(
            shap_values[idx],
            plots_dir / f"waterfall_{label}.png",
            max_display=max_display,
        )

    # save dependence plots for top features
    for _, row in feature_summary.head(top_k_dependence).iterrows():
        feature_name = row["feature"]
        partner = row.get("top_interaction_feature")
        if isinstance(partner, str) and partner in X_transformed_df.columns:
            color_arg = shap_values[:, partner]
        else:
            color_arg = None
        safe_name = feature_name.replace("/", "_").replace(" ", "_")
        plot_scatter(
            shap_values,
            feature_name,
            plots_dir / f"scatter_{safe_name}.png",
            color=color_arg,
        )

    # summary of the run
    run_summary = {
        "model_name": model_name,
        "model_path": str(model_path),
        "data_path": str(data_path),
        "n_rows_input": int(len(raw_df)),
        "n_rows_used": int(len(X_sample_raw)),
        "n_features_used": int(X_transformed_df.shape[1]),
        "top_features": feature_summary.head(15)[["feature", "mean_abs_shap", "importance_share", "top_interaction_feature"]].to_dict(orient="records"),
        "waterfall_indices": wf_indices,
        "plots_dir": str(plots_dir),
        "tables_dir": str(tables_dir),
    }
    save_json(run_summary, model_output_dir / "run_summary.json")

    report_lines = [
        f"# SHAP report: {model_name}",
        "",
        f"- Model: `{model_path}`",
        f"- Data: `{data_path}`",
        f"- Input rows: **{len(raw_df)}**",
        f"- Rows explained: **{len(X_sample_raw)}**",
        f"- Features used after preprocessing: **{X_transformed_df.shape[1]}**",
        "",
        "## Top 15 features by mean |SHAP|",
        "",
        "| rank | feature | mean_abs_shap | share | top interaction |",
        "|---:|---|---:|---:|---|",
    ]
    for rank, (_, row) in enumerate(feature_summary.head(15).iterrows(), start=1):
        report_lines.append(
            "| {rank} | {feature} | {mean_abs_shap:.6f} | {share:.2%} | {partner} |".format(
                rank=rank,
                feature=row["feature"],
                mean_abs_shap=row["mean_abs_shap"],
                share=row["importance_share"],
                partner=row["top_interaction_feature"] if pd.notna(row["top_interaction_feature"]) else "-",
            )
        )

    report_lines.extend(
        [
            "",
            "## Generated files",
            "",
            "- `plots/shap_bar.png`",
            "- `plots/shap_beeswarm.png`",
            "- `plots/shap_violin.png`",
            "- `plots/waterfall_lowest_prediction.png`",
            "- `plots/waterfall_median_prediction.png`",
            "- `plots/waterfall_highest_prediction.png`",
            f"- `plots/scatter_<top_{top_k_dependence}_features>.png`",
            "- `tables/feature_summary.csv`",
            "- `tables/sampled_predictions.csv`",
            "- `tables/sampled_transformed_features.csv.gz`",
            "- `run_summary.json`",
        ]
    )
    (model_output_dir / "REPORT.md").write_text("\n".join(report_lines), encoding="utf-8")

    return {
        "model_name": model_name,
        "output_dir": str(model_output_dir),
        "feature_summary_path": str(feature_summary_path),
        "feature_summary": feature_summary,
        "report_path": str(model_output_dir / "REPORT.md"),
        "run_summary": run_summary,
    }

# compare SHAP results between models
# saves side-by-side feature importance table and short markdown summary
def compare_models(results: list[dict[str, Any]], output_root: Path, top_n: int) -> None:
    if len(results) < 2:
        return

    comparison_dir = safe_mkdir(output_root / "comparison")

    # prepare per-model feature importance columns
    merged_frames = []
    for result in results:
        df = result["feature_summary"].copy()
        model_name = result["model_name"]
        merged_frames.append(
            df[["feature", "mean_abs_shap", "importance_share", "top_interaction_feature"]].rename(
                columns={
                    "mean_abs_shap": f"{model_name}_mean_abs_shap",
                    "importance_share": f"{model_name}_importance_share",
                    "top_interaction_feature": f"{model_name}_top_interaction_feature",
                }
            )
        )

    # merge all models into one comparison table
    comparison = merged_frames[0]
    for frame in merged_frames[1:]:
        comparison = comparison.merge(frame, on="feature", how="outer")

    mean_abs_cols = [c for c in comparison.columns if c.endswith("_mean_abs_shap")]
    comparison["combined_mean_abs_shap"] = comparison[mean_abs_cols].fillna(0).sum(axis=1)
    comparison = comparison.sort_values("combined_mean_abs_shap", ascending=False).reset_index(drop=True)
    comparison.to_csv(comparison_dir / "feature_comparison.csv", index=False)

    # compare top features between models
    top_blocks = []
    for result in results:
        model_name = result["model_name"]
        top_feats = result["feature_summary"].head(top_n)["feature"].tolist()
        top_blocks.append((model_name, top_feats))

    overlap = set(top_blocks[0][1])
    for _, feats in top_blocks[1:]:
        overlap &= set(feats)

    # short markdown report with top feature overlap
    comparison_report = [
        "# Model comparison",
        "",
        "## Top feature overlap",
        "",
    ]
    for model_name, feats in top_blocks:
        comparison_report.append(f"- **{model_name}** top {top_n}: {', '.join(feats)}")
    comparison_report.append("")
    comparison_report.append(
        f"- **Shared top {top_n} features across all models**: {', '.join(sorted(overlap)) if overlap else 'None'}"
    )
    comparison_report.append("")
    comparison_report.append("See `feature_comparison.csv` for the full side-by-side table.")

    (comparison_dir / "COMPARISON.md").write_text("\n".join(comparison_report), encoding="utf-8")

    save_json(
        {
            "shared_top_features": sorted(overlap),
            "models": [result["model_name"] for result in results],
        },
        comparison_dir / "comparison_summary.json",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SHAP analysis for two XGBoost models.")
    parser.add_argument("--baseline-model-dir", required=True, type=Path)
    parser.add_argument("--embedding-model-dir", required=True, type=Path)
    parser.add_argument("--baseline-data", required=True, type=Path)
    parser.add_argument("--embedding-data", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--sample-size", type=int, default=0)
    parser.add_argument("--max-display", type=int, default=20)
    parser.add_argument("--top-k-dependence", type=int, default=8)
    parser.add_argument("--comparison-top-n", type=int, default=20)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument(
        "--drop-columns",
        nargs="*",
        default=["target", "label", "score", "user_id", "game_id", "split", "steamid", "appid", "owned", "name"],
        help="Columns to drop before matching features to the model.",
    )
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


# main script flow:
# - parse arguments
# - run SHAP for baseline model
# - run SHAP for embedding model
# - compare both models
def main() -> None:
    args = parse_args()
    setup_logging(args.verbose)

    output_root = safe_mkdir(args.output_dir)

    LOG.info("SHAP version: %s", shap.__version__)
    LOG.info("Output directory: %s", output_root)

    results: list[dict[str, Any]] = []
    for model_dir, data_path in [
        (args.baseline_model_dir, args.baseline_data),
        (args.embedding_model_dir, args.embedding_data),
    ]:
        result = explain_model(
            model_dir=model_dir,
            data_path=data_path,
            output_root=output_root,
            sample_size=args.sample_size,
            max_display=args.max_display,
            top_k_dependence=args.top_k_dependence,
            random_state=args.random_state,
            drop_columns=args.drop_columns,
        )
        results.append(result)

    compare_models(results, output_root, top_n=args.comparison_top_n)
    LOG.info("Analysis finished successfully.")


if __name__ == "__main__":
    main()
