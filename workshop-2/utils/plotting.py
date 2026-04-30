"""
Shared plotting helpers — no widgets, pure matplotlib/seaborn functions.
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


def plot_cluster_profile_heatmap(cluster_means_df, title="Cluster Profiles (Feature Means)"):
    fig, ax = plt.subplots(figsize=(max(8, len(cluster_means_df.columns) * 0.6), max(4, len(cluster_means_df) * 0.5 + 1)))
    sns.heatmap(
        cluster_means_df,
        annot=True,
        fmt=".1f",
        cmap="YlOrRd",
        ax=ax,
        linewidths=0.5,
        annot_kws={"size": 8},
    )
    ax.set_title(title)
    ax.set_xlabel("Feature")
    ax.set_ylabel("Cluster")
    plt.tight_layout()
    return fig
