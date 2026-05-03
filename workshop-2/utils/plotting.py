"""
Shared plotting helpers 
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram


def plot_correlation_heatmap(df, figsize=(12, 9), title="Feature Correlation Heatmap"):
    numeric = df.select_dtypes(include="number")
    corr = numeric.corr()
    fig, ax = plt.subplots(figsize=figsize)
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(
        corr,
        mask=mask,
        annot=True,
        fmt=".2f",
        cmap="RdYlGn",
        center=0,
        linewidths=0.5,
        ax=ax,
        annot_kws={"size": 7},
    )
    ax.set_title(title, fontsize=14)
    plt.tight_layout()
    return fig


def plot_feature_distributions(df, columns, ncols=3, figsize_per=(4, 3)):
    columns = [c for c in columns if c in df.columns]
    nrows = int(np.ceil(len(columns) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(figsize_per[0] * ncols, figsize_per[1] * nrows))
    axes = np.array(axes).flatten()
    for i, col in enumerate(columns):
        ax = axes[i]
        if df[col].dtype == object or df[col].nunique() <= 10:
            df[col].value_counts().plot(kind="bar", ax=ax, color="steelblue", edgecolor="white")
        else:
            ax.hist(df[col].dropna(), bins=20, color="steelblue", edgecolor="white")
        ax.set_title(col, fontsize=10)
        ax.set_xlabel("")
    for ax in axes[len(columns):]:
        ax.set_visible(False)
    plt.tight_layout()
    return fig


def plot_confusion_matrix(y_true, y_pred, labels=None, title="Confusion Matrix"):
    from sklearn.metrics import confusion_matrix as _cm

    if labels is None:
        labels = sorted(set(list(y_true) + list(y_pred)))
    cm = _cm(y_true, y_pred, labels=labels)
    fig, ax = plt.subplots(figsize=(max(5, len(labels)), max(4, len(labels))))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels,
        ax=ax,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(title)
    plt.tight_layout()
    return fig


def plot_feature_importance(importances, feature_names, top_n=15, title="Feature Importance"):
    idx = np.argsort(importances)[-top_n:]
    fig, ax = plt.subplots(figsize=(8, max(4, top_n * 0.35)))
    colors = ["tomato" if feature_names[i] in ("tutorial_attendance_rate", "lecture_attendance_rate") else "steelblue" for i in idx]
    ax.barh(
        [feature_names[i] for i in idx],
        importances[idx],
        color=colors,
        edgecolor="white",
    )
    ax.set_xlabel("Importance")
    ax.set_title(title)
    plt.tight_layout()
    return fig


def plot_dendrogram(
    linkage_matrix,
    labels=None,
    truncate_p=30,
    color_threshold=None,
    title="Hierarchical Clustering Dendrogram",
    figsize=(14, 6),
):
    fig, ax = plt.subplots(figsize=figsize)
    dend_kwargs = dict(
        Z=linkage_matrix,
        truncate_mode="lastp",
        p=truncate_p,
        leaf_rotation=90,
        leaf_font_size=9,
        show_contracted=True,
        ax=ax,
    )
    if color_threshold is not None:
        dend_kwargs["color_threshold"] = color_threshold
    if labels is not None and len(labels) <= truncate_p:
        dend_kwargs.pop("truncate_mode", None)
        dend_kwargs.pop("p", None)
        dend_kwargs["labels"] = labels
    dendrogram(**dend_kwargs)
    if color_threshold is not None:
        ax.axhline(y=color_threshold, color="red", linestyle="--", linewidth=1, label=f"cut = {color_threshold:.1f}")
        ax.legend(fontsize=9)
    ax.set_title(title, fontsize=13)
    ax.set_xlabel("Sample index (or cluster size)")
    ax.set_ylabel("Distance")
    plt.tight_layout()
    return fig


def plot_elbow_curve(inertias, k_range, selected_k=None, title="Elbow Curve — K-Means Inertia"):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(list(k_range), inertias, "o-", color="steelblue", linewidth=2)
    if selected_k is not None and selected_k in k_range:
        idx = list(k_range).index(selected_k)
        ax.axvline(x=selected_k, color="tomato", linestyle="--", label=f"k = {selected_k}")
        ax.scatter([selected_k], [inertias[idx]], color="tomato", s=100, zorder=5)
        ax.legend()
    ax.set_xlabel("Number of clusters (k)")
    ax.set_ylabel("Inertia (within-cluster SSE)")
    ax.set_title(title)
    ax.set_xticks(list(k_range))
    plt.tight_layout()
    return fig


def plot_silhouette(X, labels, title="Silhouette Plot"):
    from sklearn.metrics import silhouette_samples

    n_clusters = len(set(labels))
    sample_sil = silhouette_samples(X, labels)
    fig, ax = plt.subplots(figsize=(7, 4))
    y_lower = 10
    colors = plt.cm.tab10(np.linspace(0, 1, n_clusters))
    for i, cluster_label in enumerate(sorted(set(labels))):
        vals = np.sort(sample_sil[labels == cluster_label])
        size = len(vals)
        y_upper = y_lower + size
        ax.fill_betweenx(np.arange(y_lower, y_upper), 0, vals, alpha=0.7, color=colors[i], label=f"Cluster {cluster_label}")
        y_lower = y_upper + 10
    avg_sil = sample_sil.mean()
    ax.axvline(x=avg_sil, color="red", linestyle="--", label=f"Avg = {avg_sil:.3f}")
    ax.set_xlabel("Silhouette coefficient")
    ax.set_ylabel("Cluster")
    ax.set_title(title)
    ax.legend(fontsize=8, loc="upper right")
    plt.tight_layout()
    return fig


def plot_cluster_scatter(X_2d_or_high, labels, method="PCA", title=None, figsize=(7, 5)):
    """
    Scatter plot of samples coloured by cluster label.
    If X has > 2 columns, applies PCA or t-SNE reduction first.
    """
    import pandas as pd

    if hasattr(X_2d_or_high, "values"):
        X_arr = X_2d_or_high.values
    else:
        X_arr = np.array(X_2d_or_high)

    if X_arr.shape[1] > 2:
        if method.upper() == "TSNE":
            from sklearn.manifold import TSNE
            reducer = TSNE(n_components=2, random_state=42, perplexity=min(30, len(X_arr) - 1))
        else:
            from sklearn.decomposition import PCA
            reducer = PCA(n_components=2, random_state=42)
        X_arr = reducer.fit_transform(X_arr)
        axis_labels = (f"{method} Component 1", f"{method} Component 2")
    else:
        axis_labels = ("Feature 1", "Feature 2")

    if title is None:
        title = f"Cluster Scatter ({method} projection)"

    labels_arr = np.array(labels)
    unique_labels = sorted(set(labels_arr))
    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_labels)))

    fig, ax = plt.subplots(figsize=figsize)
    for i, lbl in enumerate(unique_labels):
        mask = labels_arr == lbl
        ax.scatter(X_arr[mask, 0], X_arr[mask, 1], c=[colors[i]], label=f"Cluster {lbl}", alpha=0.7, s=30, edgecolors="none")
    ax.set_xlabel(axis_labels[0])
    ax.set_ylabel(axis_labels[1])
    ax.set_title(title)
    ax.legend(markerscale=1.5, fontsize=9)
    plt.tight_layout()
    return fig


def plot_feature_scales(df, title="Feature Value Ranges Before Normalisation"):
    """
    Horizontal bar chart showing (max − min) for each numeric feature.
    Bars are colour-coded by order of magnitude so scale differences are
    immediately obvious.  Pairs of related features at different scales
    (e.g. minutes vs hours) are labelled with an annotation.
    """
    numeric = df.select_dtypes(include="number")
    # Drop obvious ID columns
    numeric = numeric[[c for c in numeric.columns if "id" not in c.lower()]]
    ranges = (numeric.max() - numeric.min()).sort_values(ascending=True)

    # Colour tiers: <10 → green, 10–100 → orange, 100–500 → tomato, >500 → darkred
    def _colour(v):
        if v < 10:
            return "#2ca02c"
        elif v < 100:
            return "#ff7f0e"
        elif v < 500:
            return "#d62728"
        else:
            return "#8b0000"

    colours = [_colour(v) for v in ranges.values]

    fig, ax = plt.subplots(figsize=(9, max(5, len(ranges) * 0.38)))
    bars = ax.barh(ranges.index, ranges.values, color=colours, edgecolor="white")

    # Legend for colour tiers
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#2ca02c", label="Range < 10"),
        Patch(facecolor="#ff7f0e", label="Range 10–100"),
        Patch(facecolor="#d62728", label="Range 100–500"),
        Patch(facecolor="#8b0000", label="Range > 500"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=8)

    # Annotate the scale-pair columns
    scale_pairs = {
        "total_study_minutes_per_week": "← same info as avg_weekly_study_hours (×60 scale)",
        "cumulative_lms_sessions_per_semester": "← same info as lms_logins_per_week (×13 scale)",
    }
    for feat, note in scale_pairs.items():
        if feat in ranges.index:
            idx = list(ranges.index).index(feat)
            ax.annotate(
                note,
                xy=(ranges[feat], idx),
                xytext=(ranges[feat] + ranges.max() * 0.02, idx),
                fontsize=7.5,
                color="#8b0000",
                va="center",
            )

    ax.set_xlabel("Value range (max − min) — raw, unscaled")
    ax.set_title(title, fontsize=12)
    ax.axvline(0, color="black", linewidth=0.5)
    plt.tight_layout()
    return fig


def plot_normalisation_comparison(X_raw_numeric, X_scaled_numeric, labels_raw, labels_scaled,
                                   title="Effect of Normalisation on K-Means Clusters"):
    """
    2×2 grid: PCA scatter (raw vs scaled) side by side, each coloured by
    cluster label, to make the effect of normalisation visible.
    """
    from sklearn.decomposition import PCA

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    for ax, X, labels, subtitle in zip(
        axes,
        [X_raw_numeric, X_scaled_numeric],
        [labels_raw, labels_scaled],
        ["Without normalisation\n(dominated by large-scale features)",
         "With StandardScaler normalisation\n(all features contribute equally)"],
    ):
        X_arr = X.values if hasattr(X, "values") else np.array(X)
        labels_arr = np.array(labels)
        pca = PCA(n_components=2, random_state=42)
        X_2d = pca.fit_transform(X_arr)
        unique = sorted(set(labels_arr))
        colours = plt.cm.tab10(np.linspace(0, 1, len(unique)))
        for i, lbl in enumerate(unique):
            mask = labels_arr == lbl
            ax.scatter(X_2d[mask, 0], X_2d[mask, 1], c=[colours[i]],
                       label=f"Cluster {lbl}", alpha=0.7, s=25, edgecolors="none")
        ax.set_title(subtitle, fontsize=10)
        ax.set_xlabel("PC 1")
        ax.set_ylabel("PC 2")
        ax.legend(fontsize=8)

    fig.suptitle(title, fontsize=12, y=1.01)
    plt.tight_layout()
    return fig


def plot_cluster_profile_heatmap(cluster_means_df, title="Cluster Profiles (Feature Means)"):
    def _pretty_label(label, max_len=18):
        text = str(label).replace("_", " ")
        words = text.split()
        lines = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if current and len(candidate) > max_len:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
        return "\n".join(lines)

    values = cluster_means_df.astype(float)
    col_min = values.min(axis=0)
    col_range = values.max(axis=0) - col_min
    heat_values = (values - col_min) / col_range.replace(0, np.nan)
    heat_values = heat_values.fillna(0.5)

    fig_width = max(9, len(values.columns) * 0.9)
    fig_height = max(4.5, len(values.index) * 0.7 + 2)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    sns.heatmap(
        heat_values,
        annot=values,
        fmt=".1f",
        cmap="YlGnBu",
        vmin=0,
        vmax=1,
        ax=ax,
        linewidths=0.8,
        linecolor="white",
        annot_kws={"size": 8},
        cbar_kws={"label": "Relative mean within each feature"},
    )
    ax.set_title(title, fontsize=13, pad=12)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xticklabels([_pretty_label(c) for c in values.columns], rotation=45, ha="right")
    ax.set_yticklabels([_pretty_label(i, max_len=14) for i in values.index], rotation=0)
    ax.tick_params(axis="both", length=0)
    plt.tight_layout()
    return fig
