from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.cluster.hierarchy import linkage
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[2]
PRESENTATION_DIR = ROOT / "presentation"
IMAGE_DIR = PRESENTATION_DIR / "images"
DATA_PATH = ROOT / "sample_data" / "student_learning_profiles.csv"

sys.path.insert(0, str(ROOT))

from utils.preprocessor import preprocess  # noqa: E402
from utils.plotting import (  # noqa: E402
    plot_correlation_heatmap,
    plot_dendrogram,
    plot_elbow_curve,
    plot_feature_importance,
    plot_feature_scales,
    plot_normalisation_comparison,
)


HCA_KMEANS_FEATURES = [
    "lecture_attendance_rate",
    "tutorial_attendance_rate",
    "tutorial_participation_score",
    "office_hours_visits",
    "lms_logins_per_week",
    "assignment_completion_rate",
    "avg_weekly_study_hours",
    "self_reported_stress_level",
    "extracurricular_hours_per_week",
    "part_time_work_hours",
]

RF_FEATURES = [
    "year_of_study",
    "socioeconomic_index",
    "parental_education_level",
    "scholarship_holder",
    "accommodation_type",
    "internet_access_quality",
    "lecture_attendance_rate",
    "tutorial_attendance_rate",
    "tutorial_participation_score",
    "office_hours_visits",
    "lms_logins_per_week",
    "assignment_completion_rate",
    "self_reported_stress_level",
    "avg_weekly_study_hours",
    "extracurricular_hours_per_week",
    "part_time_work_hours",
]

LABEL_ORDER = ["At-Risk", "Pass", "Merit", "Distinction"]


def save(fig, filename, dpi=150):
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(IMAGE_DIR / filename, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def pretty(name):
    return name.replace("_", " ").title()


def build_dataset_overview(df):
    numeric_cols = df.select_dtypes(include="number").columns
    categorical_cols = df.select_dtypes(exclude="number").columns

    fig = plt.figure(figsize=(12.9, 6.9))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.15], width_ratios=[0.95, 1.25])
    ax_counts = fig.add_subplot(gs[0, 0])
    ax_perf = fig.add_subplot(gs[1, 0])
    ax_table = fig.add_subplot(gs[:, 1])

    ax_counts.bar(
        ["Rows", "Numeric\ncolumns", "Categorical\ncolumns"],
        [len(df), len(numeric_cols), len(categorical_cols)],
        color=["#203653", "#2b9dcc", "#c97a1a"],
        edgecolor="white",
    )
    ax_counts.set_title("Dataset shape and mixed data types", fontsize=13, pad=10)
    ax_counts.set_ylabel("Count")
    for container in ax_counts.containers:
        ax_counts.bar_label(container, fmt="%d", padding=3, fontsize=10)
    ax_counts.spines[["top", "right"]].set_visible(False)

    band_counts = df["performance_band"].value_counts().reindex(LABEL_ORDER)
    ax_perf.bar(band_counts.index, band_counts.values, color="#415064", edgecolor="white")
    ax_perf.set_title("Target label distribution", fontsize=13, pad=10)
    ax_perf.set_ylabel("Students")
    ax_perf.tick_params(axis="x", rotation=20)
    for container in ax_perf.containers:
        ax_perf.bar_label(container, fmt="%d", padding=3, fontsize=10)
    ax_perf.spines[["top", "right"]].set_visible(False)

    ax_table.axis("off")
    groups = [
        ("Identifiers", "student_id"),
        ("Demographics", "age, gender, year_of_study, faculty"),
        ("Context", "scholarship, accommodation, internet quality"),
        ("Engagement", "attendance, participation, office_hours, LMS use"),
        ("Study and workload", "study_hours, work_hours, stress, extracurricular hours"),
        ("Assessment", "assignment, midterm, final_exam, avg_score"),
        ("Target", "performance_band"),
    ]
    table = ax_table.table(
        cellText=groups,
        colLabels=["Column group", "Examples"],
        loc="center",
        cellLoc="left",
        colLoc="left",
        colWidths=[0.32, 0.68],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9.5)
    table.scale(1, 1.55)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#d7dee8")
        if row == 0:
            cell.set_facecolor("#203653")
            cell.set_text_props(color="white", weight="bold")
        elif row % 2 == 0:
            cell.set_facecolor("#f2f6fb")
        else:
            cell.set_facecolor("white")
    ax_table.set_title("What the sample data now contains", fontsize=13, pad=16)
    fig.suptitle("Student Learning Profiles: 500 rows, 29 columns", fontsize=16, weight="bold")
    fig.tight_layout()
    return fig


def build_performance_distribution(df):
    counts = df["performance_band"].value_counts().reindex(LABEL_ORDER)
    fig, ax = plt.subplots(figsize=(6.9, 3.9))
    ax.bar(counts.index, counts.values, color=["#c97a1a", "#7aa6c2", "#2b9dcc", "#203653"], edgecolor="white")
    ax.set_title("Performance Band Distribution", fontsize=13)
    ax.set_xlabel("Performance band")
    ax.set_ylabel("Students")
    ax.tick_params(axis="x", rotation=20)
    for container in ax.containers:
        ax.bar_label(container, fmt="%d", padding=3, fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def build_categorical_encoding(df):
    cols = ["scholarship_holder", "accommodation_type", "internet_access_quality"]
    sample = df[cols].head(6).copy()
    label_encoded = sample.copy()
    for col in cols:
        label_encoded[col] = LabelEncoder().fit_transform(label_encoded[col].astype(str))
    onehot = pd.get_dummies(sample, columns=cols, dtype=int)
    onehot = onehot[
        [
            "scholarship_holder_No",
            "scholarship_holder_Yes",
            "accommodation_type_Family home",
            "accommodation_type_Off-campus",
            "accommodation_type_On-campus",
            "internet_access_quality_Poor",
            "internet_access_quality_Good",
            "internet_access_quality_Excellent",
        ]
    ]

    fig, axes = plt.subplots(1, 3, figsize=(13.9, 6.75))
    for ax in axes:
        ax.axis("off")

    tables = [
        ("Raw categorical values", sample),
        ("Label encoded", label_encoded),
        ("One-hot encoded excerpt", onehot),
    ]
    short_onehot_names = {
        "scholarship_holder_No": "Sch.\nNo",
        "scholarship_holder_Yes": "Sch.\nYes",
        "accommodation_type_Family home": "Home",
        "accommodation_type_Off-campus": "Off",
        "accommodation_type_On-campus": "On",
        "internet_access_quality_Poor": "Poor",
        "internet_access_quality_Good": "Good",
        "internet_access_quality_Excellent": "Excel.",
    }
    for ax, (title, data) in zip(axes, tables):
        display = data.copy()
        if "one-hot" in title.lower():
            display.columns = [short_onehot_names.get(c, c) for c in display.columns]
        else:
            display.columns = [
                c.replace("scholarship_holder", "Scholarship")
                .replace("accommodation_type", "Accommodation")
                .replace("internet_access_quality", "Internet")
                .replace("_", " ")
                for c in display.columns
            ]
        table = ax.table(
            cellText=display.astype(str).values,
            colLabels=display.columns,
            rowLabels=[str(i) for i in display.index],
            bbox=[0.0, 0.08, 1.0, 0.78],
            cellLoc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8.2)
        for (row, col), cell in table.get_celld().items():
            cell.set_edgecolor("#d7dee8")
            if row == 0:
                cell.set_facecolor("#203653")
                cell.set_text_props(color="white", weight="bold")
            elif row % 2 == 0:
                cell.set_facecolor("#f2f6fb")
        ax.set_title(title, fontsize=13, pad=16)

    fig.suptitle("Categorical features must be converted before modelling", fontsize=16, weight="bold")
    fig.tight_layout()
    return fig


def build_scaling_before_after(df, features):
    raw = df[features].select_dtypes(include="number")
    scaled = pd.DataFrame(StandardScaler().fit_transform(raw), columns=raw.columns)
    raw_ranges = (raw.max() - raw.min()).sort_values()
    scaled_ranges = (scaled.max() - scaled.min()).reindex(raw_ranges.index)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6.75), sharey=True)
    axes[0].barh([pretty(c) for c in raw_ranges.index], raw_ranges.values, color="#c97a1a", edgecolor="white")
    axes[1].barh([pretty(c) for c in scaled_ranges.index], scaled_ranges.values, color="#2b9dcc", edgecolor="white")
    axes[0].set_title("Before scaling: raw value ranges", fontsize=13)
    axes[1].set_title("After StandardScaler: comparable ranges", fontsize=13)
    axes[0].set_xlabel("Max - min")
    axes[1].set_xlabel("Max - min after scaling")
    for ax in axes:
        ax.grid(axis="x", alpha=0.22)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="y", labelsize=9)
    fig.suptitle("Distance-based models are sensitive to feature scale", fontsize=16, weight="bold")
    fig.tight_layout()
    return fig


def build_kmeans_vs_bands(df, X_scaled):
    labels = KMeans(n_clusters=4, random_state=42, n_init=20).fit_predict(X_scaled)
    comparison = pd.crosstab(
        pd.Series(labels + 1, name="K-Means cluster"),
        df["performance_band"],
    ).reindex(columns=LABEL_ORDER)

    fig, ax = plt.subplots(figsize=(11.9, 5.1))
    sns.heatmap(
        comparison,
        annot=True,
        fmt="d",
        cmap="YlGnBu",
        linewidths=0.8,
        linecolor="white",
        cbar_kws={"label": "Number of students"},
        ax=ax,
    )
    ax.set_title("K-Means clusters compared with performance bands", fontsize=14, pad=12)
    ax.set_xlabel("Performance band")
    ax.set_ylabel("Cluster")
    fig.tight_layout()
    return fig


def kmeans_information_criteria(model, X):
    X_arr = X.to_numpy() if hasattr(X, "to_numpy") else np.asarray(X)
    n_samples, n_features = X_arr.shape
    sse = max(float(model.inertia_), np.finfo(float).eps)
    variance = max(sse / (n_samples * n_features), np.finfo(float).eps)
    log_likelihood = -0.5 * n_samples * n_features * (np.log(2 * np.pi * variance) + 1)
    n_parameters = model.n_clusters * n_features + 1
    aic = 2 * n_parameters - 2 * log_likelihood
    bic = np.log(n_samples) * n_parameters - 2 * log_likelihood
    return aic, bic


def build_aic_bic_model_selection(X_scaled):
    k_range = range(1, 11)
    rows = []
    for k in k_range:
        model = KMeans(
            n_clusters=k,
            n_init=20,
            random_state=42,
        )
        model.fit(X_scaled)
        aic, bic = kmeans_information_criteria(model, X_scaled)
        rows.append(
            {
                "k": k,
                "AIC": aic,
                "BIC": bic,
            }
        )

    scores = pd.DataFrame(rows)
    best_aic = scores.loc[scores["AIC"].idxmin()]
    best_bic = scores.loc[scores["BIC"].idxmin()]

    fig, ax = plt.subplots(figsize=(10.8, 5.6))
    ax.plot(scores["k"], scores["AIC"], marker="o", linewidth=2.2, color="#2b9dcc", label="AIC-style score")
    ax.plot(scores["k"], scores["BIC"], marker="o", linewidth=2.2, color="#c97a1a", label="BIC-style score")
    ax.axvline(best_aic["k"], color="#2b9dcc", linestyle="--", alpha=0.45)
    ax.axvline(best_bic["k"], color="#c97a1a", linestyle="--", alpha=0.45)
    ax.scatter(best_aic["k"], best_aic["AIC"], s=95, color="#2b9dcc", edgecolor="white", zorder=4)
    ax.scatter(best_bic["k"], best_bic["BIC"], s=95, color="#c97a1a", edgecolor="white", zorder=4)
    ax.text(best_aic["k"] + 0.15, best_aic["AIC"], f"AIC min: {int(best_aic['k'])}", color="#203653")
    ax.text(best_bic["k"] + 0.15, best_bic["BIC"], f"BIC min: {int(best_bic['k'])}", color="#203653")
    ax.set_title("K-Means AIC/BIC-style elbow: fit improves, complexity is penalised", fontsize=14, pad=12)
    ax.set_xlabel("Number of clusters (k)")
    ax.set_ylabel("Information criterion score (lower is better)")
    ax.set_xticks(list(k_range))
    ax.grid(alpha=0.22)
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def fit_random_forest(df):
    X = df[RF_FEATURES]
    y = df["performance_band"]
    X_train, X_test, y_train, y_test, _, _ = preprocess(
        X,
        y=y,
        scale="standard",
        encode_categoricals="label",
        test_size=0.2,
        random_state=42,
    )
    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        max_features="sqrt",
        class_weight=None,
    )
    model.fit(X_train, y_train)
    return model, X_train, X_test, y_train, y_test


def build_confusion_matrix(model, X_test, y_test):
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred, labels=LABEL_ORDER)
    fig, ax = plt.subplots(figsize=(5.6, 4.9))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=LABEL_ORDER,
        yticklabels=LABEL_ORDER,
        linewidths=0.5,
        linecolor="white",
        cbar=False,
        ax=ax,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Random Forest confusion matrix", fontsize=13)
    ax.tick_params(axis="x", rotation=25)
    ax.tick_params(axis="y", rotation=0)
    fig.tight_layout()
    return fig


def main():
    df = pd.read_csv(DATA_PATH)

    save(build_performance_distribution(df), "01_performance_distribution.png")
    save(build_dataset_overview(df), "10_dataset_overview.png")
    save(build_categorical_encoding(df), "12_preprocessing_categorical_encoding.png")
    save(build_scaling_before_after(df, HCA_KMEANS_FEATURES), "14_preprocessing_scaling_before_after.png")

    save(plot_feature_scales(df[HCA_KMEANS_FEATURES]), "02_feature_scales.png")
    save(plot_correlation_heatmap(df[HCA_KMEANS_FEATURES], figsize=(10, 8)), "03_correlation_heatmap.png")

    X_cluster, _, _ = preprocess(
        df[HCA_KMEANS_FEATURES],
        y=None,
        scale="standard",
        encode_categoricals="label",
        random_state=42,
    )
    Z = linkage(X_cluster, method="ward")
    save(
        plot_dendrogram(
            Z,
            truncate_p=30,
            color_threshold=Z[-4, 2],
            figsize=(10.9, 4.9),
        ),
        "04_dendrogram.png",
    )

    k_range = range(2, 11)
    inertias = [
        KMeans(n_clusters=k, random_state=42, n_init=20).fit(X_cluster).inertia_
        for k in k_range
    ]
    save(
        plot_elbow_curve(
            inertias,
            k_range,
            selected_k=4,
            title="Elbow Curve - K-Means on Default Workshop Features",
        ),
        "05_elbow_curve.png",
    )
    save(build_kmeans_vs_bands(df, X_cluster), "07_kmeans_vs_bands.png")
    save(build_aic_bic_model_selection(X_cluster), "15_aic_bic_model_selection.png")

    X_raw = df[HCA_KMEANS_FEATURES].copy()
    labels_raw = KMeans(n_clusters=4, random_state=42, n_init=20).fit_predict(X_raw)
    labels_scaled = KMeans(n_clusters=4, random_state=42, n_init=20).fit_predict(X_cluster)
    save(
        plot_normalisation_comparison(
            X_raw,
            X_cluster,
            labels_raw,
            labels_scaled,
            title="Effect of Normalisation on K-Means Clusters",
        ),
        "06_normalisation_comparison.png",
    )

    model, X_train, X_test, _, y_test = fit_random_forest(df)
    save(
        plot_feature_importance(
            model.feature_importances_,
            np.array(X_train.columns),
            top_n=12,
            title="Random Forest Feature Importance",
        ),
        "08_feature_importance.png",
    )
    save(build_confusion_matrix(model, X_test, y_test), "09_confusion_matrix.png")

    print(f"Regenerated slide images in {IMAGE_DIR}")


if __name__ == "__main__":
    main()
