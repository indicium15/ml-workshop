"""
DataLoaderWidget: CSV upload + column mapping for any dataset.
Provides a file path input, preview, and feature/label selectors.
"""
import io
import os

import ipywidgets as widgets
import pandas as pd
from IPython.display import display


_SAMPLE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "sample_data", "student_learning_profiles.csv"
)


class DataLoaderWidget:
    """
    Step-by-step widget for loading a CSV and mapping columns.

    Parameters
    ----------
    show_label_selector : bool
        If True, show a dropdown for choosing the target/label column
        (used for supervised learning notebooks).

    After the user clicks Confirm, the following attributes are populated:
        .df          — full loaded DataFrame
        .X_df        — DataFrame of selected feature columns
        .y           — Series of label column (None if show_label_selector=False)
        .confirmed   — bool flag
    """

    def __init__(self, show_label_selector=True):
        self.show_label_selector = show_label_selector
        self.df = None
        self.X_df = None
        self.y = None
        self.confirmed = False

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        title = widgets.HTML("<h3>📂 Step 1 — Load Data</h3>")

        # File path input (pre-filled with sample data)
        self._path_input = widgets.Text(
            value=os.path.abspath(_SAMPLE_PATH),
            description="CSV path:",
            layout=widgets.Layout(width="80%"),
            style={"description_width": "80px"},
        )
        self._upload_btn = widgets.Button(
            description="Load CSV",
            button_style="primary",
            icon="upload",
        )
        self._upload_widget = widgets.FileUpload(
            accept=".csv",
            multiple=False,
            description="Or upload:",
            layout=widgets.Layout(width="200px"),
        )
        self._status = widgets.HTML("")

        # Preview area
        self._preview_out = widgets.Output()

        # Column selectors (hidden until data loaded)
        self._feature_select = widgets.SelectMultiple(
            options=[],
            description="Features:",
            layout=widgets.Layout(width="60%", height="150px"),
            style={"description_width": "80px"},
        )
        self._label_dropdown = widgets.Dropdown(
            options=[],
            description="Label col:",
            layout=widgets.Layout(width="60%"),
            style={"description_width": "80px"},
        )
        self._select_all_btn = widgets.Button(
            description="Select all numeric",
            button_style="",
            layout=widgets.Layout(width="180px"),
        )
        self._confirm_btn = widgets.Button(
            description="Confirm Selection",
            button_style="success",
            icon="check",
            disabled=True,
        )
        self._confirm_out = widgets.Output()

        # Wire callbacks
        self._upload_btn.on_click(self._on_load_path)
        self._upload_widget.observe(self._on_file_upload, names="value")
        self._select_all_btn.on_click(self._on_select_all_numeric)
        self._confirm_btn.on_click(self._on_confirm)

        selector_box = widgets.VBox(
            [
                widgets.HTML("<b>Select feature columns (hold Ctrl/Cmd for multi-select):</b>"),
                self._feature_select,
                self._select_all_btn,
            ]
        )

        if self.show_label_selector:
            selector_box.children += (
                widgets.HTML("<b>Select label/target column:</b>"),
                self._label_dropdown,
            )

        self._selector_section = widgets.VBox(
            [selector_box, self._confirm_btn, self._confirm_out],
            layout=widgets.Layout(display="none"),
        )

        self._widget = widgets.VBox(
            [
                title,
                widgets.HBox([self._path_input, self._upload_btn]),
                self._upload_widget,
                self._status,
                self._preview_out,
                self._selector_section,
            ]
        )

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def _load_from_df(self, df):
        self.df = df
        cols = list(df.columns)
        numeric_cols = list(df.select_dtypes(include="number").columns)

        self._feature_select.options = cols
        self._feature_select.value = numeric_cols[:min(len(numeric_cols), 10)]

        self._label_dropdown.options = cols
        if "performance_band" in cols:
            self._label_dropdown.value = "performance_band"

        self._preview_out.clear_output()
        with self._preview_out:
            display(
                widgets.HTML(
                    f"<b>Loaded {len(df):,} rows × {len(cols)} columns</b>"
                )
            )
            display(df.head())

        self._selector_section.layout.display = ""
        self._confirm_btn.disabled = False
        self._status.value = (
            f'<span style="color:green">✓ Loaded {len(df):,} rows × {len(cols)} columns</span>'
        )

    def _on_load_path(self, _btn):
        path = self._path_input.value.strip()
        try:
            df = pd.read_csv(path)
            self._load_from_df(df)
        except Exception as exc:
            self._status.value = f'<span style="color:red">Error: {exc}</span>'

    def _on_file_upload(self, change):
        if not change["new"]:
            return
        try:
            uploaded = next(iter(change["new"].values()))
            content = uploaded["content"]
            df = pd.read_csv(io.BytesIO(bytes(content)))
            self._load_from_df(df)
        except Exception as exc:
            self._status.value = f'<span style="color:red">Error: {exc}</span>'

    def _on_select_all_numeric(self, _btn):
        if self.df is not None:
            numeric_cols = list(self.df.select_dtypes(include="number").columns)
            self._feature_select.value = numeric_cols

    def _on_confirm(self, _btn):
        try:
            feature_cols = list(self._feature_select.value)
            if not feature_cols:
                self._confirm_out.clear_output()
                with self._confirm_out:
                    display(widgets.HTML('<span style="color:red">Please select at least one feature column.</span>'))
                return

            self.X_df = self.df[feature_cols].copy()

            if self.show_label_selector:
                label_col = self._label_dropdown.value
                if label_col in feature_cols:
                    self._confirm_out.clear_output()
                    with self._confirm_out:
                        display(widgets.HTML('<span style="color:orange">⚠ Label column is also in features — removing it from features.</span>'))
                    self.X_df = self.X_df.drop(columns=[label_col])
                self.y = self.df[label_col].copy()
            else:
                self.y = None

            self.confirmed = True
            self._confirm_btn.disabled = True
            self._confirm_out.clear_output()
            with self._confirm_out:
                n_feat = len(self.X_df.columns)
                label_info = (
                    f", label: <b>{self._label_dropdown.value}</b>"
                    if self.show_label_selector
                    else ""
                )
                display(
                    widgets.HTML(
                        f'<span style="color:green">✓ Confirmed — {n_feat} features{label_info}. '
                        f"Run the next cell to continue.</span>"
                    )
                )
        except Exception as exc:
            self._confirm_out.clear_output()
            with self._confirm_out:
                display(widgets.HTML(f'<span style="color:red">Error: {exc}</span>'))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def display(self):
        display(self._widget)

    def __repr__(self):
        return "DataLoaderWidget()"
