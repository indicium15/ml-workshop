"""
PreprocessorWidget: scaling, encoding, and train/test split controls.
Also exposes a standalone preprocess() function for non-widget use.
"""
import ipywidgets as widgets
import numpy as np
import pandas as pd
from IPython.display import display
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, OneHotEncoder, StandardScaler


def preprocess(
    X_df,
    y=None,
    scale="standard",
    encode_categoricals="label",
    test_size=0.2,
    random_state=42,
):
    """
    Preprocess features for ML.

    Parameters
    ----------
    X_df : pd.DataFrame
    y : pd.Series or None
    scale : 'standard' | 'minmax' | None
    encode_categoricals : 'label' | 'onehot' | 'drop'
    test_size : float
    random_state : int

    Returns
    -------
    If y is not None:
        X_train, X_test, y_train, y_test, scaler, encoder_info
    If y is None (clustering):
        X_scaled, scaler, encoder_info
    """
    X = X_df.copy()
    cat_cols = list(X.select_dtypes(include=["object", "category"]).columns)
    encoder_info = {}

    if cat_cols:
        if encode_categoricals == "label":
            for col in cat_cols:
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
                encoder_info[col] = le
        elif encode_categoricals == "onehot":
            ohe = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
            ohe_arr = ohe.fit_transform(X[cat_cols])
            ohe_cols = ohe.get_feature_names_out(cat_cols)
            X = X.drop(columns=cat_cols)
            ohe_df = pd.DataFrame(ohe_arr, columns=ohe_cols, index=X.index)
            X = pd.concat([X, ohe_df], axis=1)
            encoder_info["onehot"] = ohe
        elif encode_categoricals == "drop":
            X = X.drop(columns=cat_cols)

    X = X.apply(pd.to_numeric, errors="coerce").fillna(0)

    scaler = None
    if scale == "standard":
        scaler = StandardScaler()
        X_arr = scaler.fit_transform(X)
    elif scale == "minmax":
        scaler = MinMaxScaler()
        X_arr = scaler.fit_transform(X)
    else:
        X_arr = X.values

    X_scaled = pd.DataFrame(X_arr, columns=X.columns, index=X.index)

    if y is None:
        return X_scaled, scaler, encoder_info

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=test_size, random_state=random_state, stratify=y if y.nunique() < 20 else None
    )
    return X_train, X_test, y_train, y_test, scaler, encoder_info


class PreprocessorWidget:
    """
    Interactive widget for choosing scaling, encoding, and test split.

    After the user clicks Confirm, the following attributes are populated:
        .X_train, .X_test, .y_train, .y_test   (supervised)
        .X_scaled                                (clustering, when y=None)
        .scaler, .encoder_info
        .confirmed
    """

    def __init__(self, X_df=None, y=None, force_scale=False, clustering_mode=False, source_loader=None):
        """
        Parameters
        ----------
        X_df : pd.DataFrame — features (can be set later via .set_data())
        y : pd.Series or None
        force_scale : bool — disables the "None" scaling option (for K-Means)
        clustering_mode : bool — hides test split (for unsupervised tasks)
        source_loader : DataLoaderWidget or None — when provided, the latest
            confirmed loader selections are pulled when the user clicks Apply.
        """
        self.X_df = X_df
        self.y = y
        self.force_scale = force_scale
        self.clustering_mode = clustering_mode
        self.source_loader = source_loader

        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.X_scaled = None
        self.scaler = None
        self.encoder_info = {}
        self.confirmed = False

        self._build_ui()

    def set_data(self, X_df, y=None):
        self.X_df = X_df
        self.y = y

    def _refresh_from_loader(self):
        if self.source_loader is None:
            return
        if getattr(self.source_loader, "confirmed", False):
            self.X_df = self.source_loader.X_df
            self.y = self.source_loader.y

    def _build_ui(self):
        title = widgets.HTML("<h3>⚙️ Step 2 — Preprocessing</h3>")

        scale_options = ["standard", "minmax"] if self.force_scale else ["standard", "minmax", "none"]
        self._scale_dd = widgets.Dropdown(
            options=scale_options,
            value=scale_options[0],
            description="Scaling:",
            style={"description_width": "120px"},
        )
        self._encode_dd = widgets.Dropdown(
            options=["label", "onehot", "drop"],
            value="label",
            description="Categorical enc:",
            style={"description_width": "120px"},
        )

        self._split_slider = widgets.FloatSlider(
            value=0.2,
            min=0.1,
            max=0.4,
            step=0.05,
            description="Test split:",
            readout_format=".0%",
            style={"description_width": "120px"},
        )
        self._seed_input = widgets.IntText(
            value=42,
            description="Random state:",
            layout=widgets.Layout(width="200px"),
            style={"description_width": "120px"},
        )
        self._confirm_btn = widgets.Button(
            description="Apply Preprocessing",
            button_style="success",
            icon="check",
        )
        self._out = widgets.Output()

        self._confirm_btn.on_click(self._on_confirm)

        children = [
            title,
            self._scale_dd,
            self._encode_dd,
        ]
        if not self.clustering_mode:
            children += [self._split_slider]
        children += [self._seed_input, self._confirm_btn, self._out]

        if self.force_scale:
            children.insert(
                2,
                widgets.HTML('<span style="color:#888">ℹ Scaling is required for K-Means and is always enabled.</span>'),
            )

        self._widget = widgets.VBox(children)

    def _on_confirm(self, _btn):
        self._refresh_from_loader()
        if self.X_df is None:
            with self._out:
                display(widgets.HTML('<span style="color:red">No data loaded yet. Run the data loading cell first.</span>'))
            return

        scale_val = self._scale_dd.value if self._scale_dd.value != "none" else None
        encode_val = self._encode_dd.value
        test_size = self._split_slider.value if not self.clustering_mode else 0.2
        seed = self._seed_input.value

        try:
            if self.y is None or self.clustering_mode:
                result = preprocess(
                    self.X_df,
                    y=None,
                    scale=scale_val,
                    encode_categoricals=encode_val,
                    test_size=test_size,
                    random_state=seed,
                )
                self.X_scaled, self.scaler, self.encoder_info = result
            else:
                result = preprocess(
                    self.X_df,
                    y=self.y,
                    scale=scale_val,
                    encode_categoricals=encode_val,
                    test_size=test_size,
                    random_state=seed,
                )
                self.X_train, self.X_test, self.y_train, self.y_test, self.scaler, self.encoder_info = result

            self.confirmed = True
            self._confirm_btn.disabled = True
            self._out.clear_output()
            with self._out:
                if self.y is None or self.clustering_mode:
                    shape = self.X_scaled.shape
                    display(widgets.HTML(
                        f'<span style="color:green">✓ Preprocessed — {shape[0]} rows × {shape[1]} features. '
                        f"Run the next cell to continue.</span>"
                    ))
                else:
                    display(widgets.HTML(
                        f'<span style="color:green">✓ Preprocessed — '
                        f"train: {len(self.X_train)}, test: {len(self.X_test)} rows × "
                        f"{self.X_train.shape[1]} features. Run the next cell to continue.</span>"
                    ))
        except Exception as exc:
            self._out.clear_output()
            with self._out:
                display(widgets.HTML(f'<span style="color:red">Error during preprocessing: {exc}</span>'))

    def display(self):
        display(self._widget)

    def __repr__(self):
        return "PreprocessorWidget()"
