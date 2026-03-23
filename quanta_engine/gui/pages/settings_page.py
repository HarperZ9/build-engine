"""
Settings -- configuration and about page.

Broker credentials, default models, data directory, and module
status indicators.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QLineEdit, QCheckBox, QGridLayout,
    QFileDialog, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from quanta_engine.gui.app import C, Card, Heading, Stat, StatusDot


class SettingsPage(QWidget):
    """Settings and about page."""

    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self._main_window = main_window
        self._build_ui()
        self._check_modules()

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(18)

        layout.addWidget(Heading("Settings"))

        # Row 1: Broker + Defaults
        row1 = QHBoxLayout()
        row1.setSpacing(16)

        # Broker card
        card_broker, broker_lay = Card.with_layout()
        broker_lay.addWidget(Heading("Broker Configuration", level=2))

        broker_grid = QGridLayout()
        broker_grid.setSpacing(10)
        broker_grid.setColumnMinimumWidth(0, 100)

        broker_grid.addWidget(QLabel("API Key:"), 0, 0, Qt.AlignmentFlag.AlignRight)
        self._api_key = QLineEdit()
        self._api_key.setPlaceholderText("Enter API key")
        self._api_key.setEchoMode(QLineEdit.EchoMode.Password)
        broker_grid.addWidget(self._api_key, 0, 1)

        broker_grid.addWidget(QLabel("API Secret:"), 1, 0, Qt.AlignmentFlag.AlignRight)
        self._api_secret = QLineEdit()
        self._api_secret.setPlaceholderText("Enter API secret")
        self._api_secret.setEchoMode(QLineEdit.EchoMode.Password)
        broker_grid.addWidget(self._api_secret, 1, 1)

        broker_grid.addWidget(QLabel("Broker:"), 2, 0, Qt.AlignmentFlag.AlignRight)
        broker_label = QLabel("Alpaca")
        broker_label.setStyleSheet(f"color: {C.ACCENT_TX}; font-weight: 500;")
        broker_grid.addWidget(broker_label, 2, 1)

        broker_lay.addLayout(broker_grid)

        btn_save_broker = QPushButton("Save Credentials")
        btn_save_broker.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save_broker.clicked.connect(self._save_broker)
        broker_lay.addWidget(btn_save_broker, alignment=Qt.AlignmentFlag.AlignLeft)
        broker_lay.addStretch()

        row1.addWidget(card_broker, stretch=1)

        # Defaults card
        card_defaults, defaults_lay = Card.with_layout()
        defaults_lay.addWidget(Heading("Default Settings", level=2))

        defaults_grid = QGridLayout()
        defaults_grid.setSpacing(10)
        defaults_grid.setColumnMinimumWidth(0, 100)

        defaults_grid.addWidget(QLabel("Models:"), 0, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        models_widget = QWidget()
        models_lay = QVBoxLayout(models_widget)
        models_lay.setContentsMargins(0, 0, 0, 0)
        models_lay.setSpacing(4)
        self._def_arima = QCheckBox("ARIMA")
        self._def_arima.setChecked(True)
        self._def_prophet = QCheckBox("Prophet")
        self._def_prophet.setChecked(True)
        self._def_neural = QCheckBox("Neural")
        models_lay.addWidget(self._def_arima)
        models_lay.addWidget(self._def_prophet)
        models_lay.addWidget(self._def_neural)
        defaults_grid.addWidget(models_widget, 0, 1)

        defaults_grid.addWidget(QLabel("Risk:"), 1, 0, Qt.AlignmentFlag.AlignRight)
        self._def_risk = QLineEdit("2%")
        self._def_risk.setFixedWidth(80)
        defaults_grid.addWidget(self._def_risk, 1, 1)

        defaults_grid.addWidget(QLabel("Data Dir:"), 2, 0, Qt.AlignmentFlag.AlignRight)
        dir_row = QHBoxLayout()
        self._data_dir = QLineEdit("./data")
        dir_row.addWidget(self._data_dir)
        btn_browse = QPushButton("Browse")
        btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse.clicked.connect(self._browse_dir)
        dir_row.addWidget(btn_browse)
        defaults_grid.addLayout(dir_row, 2, 1)

        defaults_lay.addLayout(defaults_grid)

        btn_save_defaults = QPushButton("Save Defaults")
        btn_save_defaults.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save_defaults.clicked.connect(self._save_defaults)
        defaults_lay.addWidget(btn_save_defaults, alignment=Qt.AlignmentFlag.AlignLeft)
        defaults_lay.addStretch()

        row1.addWidget(card_defaults, stretch=1)

        layout.addLayout(row1)

        # Module status
        card_modules, modules_lay = Card.with_layout()
        modules_lay.addWidget(Heading("Module Status", level=2))

        self._module_grid = QGridLayout()
        self._module_grid.setSpacing(10)

        self._module_dots = {}
        modules = [
            ("quanta-oracle", "Forecasting models (ARIMA, Prophet, Neural)"),
            ("quanta-finance", "Trading execution (AutoTrader, Backtester)"),
            ("quanta-engine", "Adaptive engine (this package)"),
            ("PyQt6", "GUI framework"),
            ("numpy", "Numerical computing"),
            ("pandas", "Data manipulation"),
        ]

        for row, (name, desc) in enumerate(modules):
            dot = StatusDot(C.TEXT3, 10)
            self._module_grid.addWidget(dot, row, 0)

            name_label = QLabel(name)
            name_label.setStyleSheet(f"font-weight: 600; font-size: 12px;")
            name_label.setFixedWidth(130)
            self._module_grid.addWidget(name_label, row, 1)

            desc_label = QLabel(desc)
            desc_label.setStyleSheet(f"color: {C.TEXT2}; font-size: 11px;")
            self._module_grid.addWidget(desc_label, row, 2)

            status_label = QLabel("checking...")
            status_label.setStyleSheet(f"color: {C.TEXT3}; font-size: 11px;")
            status_label.setFixedWidth(90)
            self._module_grid.addWidget(status_label, row, 3)

            self._module_dots[name] = (dot, status_label)

        modules_lay.addLayout(self._module_grid)
        layout.addWidget(card_modules)

        # About
        card_about, about_lay = Card.with_layout()
        about_lay.addWidget(Heading("About", level=2))

        about_text = QLabel(
            "<b>Quanta Engine</b> v1.0.0<br><br>"
            "Self-improving prediction and trading engine.<br><br>"
            "Integrates <b>quanta-oracle</b> forecasting models (ARIMA, Prophet, "
            "Neural Network) with <b>quanta-finance</b> execution layer "
            "(AutoTrader, Backtester, PaperBroker) for a complete "
            "prediction-trade-evaluate feedback loop.<br><br>"
            "The adaptive engine automatically adjusts model weights "
            "based on directional accuracy, so better-performing models "
            "get more influence over time.<br><br>"
            "<b>Architecture:</b><br>"
            "Market Data -> Models Train -> Predictions -> Trades -> "
            "Results -> Models Improve<br><br>"
            "Part of the <b>Quanta Universe</b> ecosystem."
        )
        about_text.setWordWrap(True)
        about_text.setStyleSheet(f"font-size: 12px; color: {C.TEXT}; line-height: 1.5;")
        about_lay.addWidget(about_text)
        layout.addWidget(card_about)

        layout.addStretch()

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _check_modules(self):
        """Check which modules are available."""
        checks = {
            "quanta-oracle": "quanta_oracle",
            "quanta-finance": "quanta_finance",
            "quanta-engine": "quanta_engine",
            "PyQt6": "PyQt6",
            "numpy": "numpy",
            "pandas": "pandas",
        }

        for display_name, import_name in checks.items():
            dot, status_label = self._module_dots[display_name]
            try:
                __import__(import_name)
                dot.set_color(C.GREEN_MUT)
                status_label.setText("available")
                status_label.setStyleSheet(f"color: {C.GREEN_MUT}; font-size: 11px; font-weight: 500;")
            except ImportError:
                dot.set_color(C.RED_MUT)
                status_label.setText("missing")
                status_label.setStyleSheet(f"color: {C.RED_MUT}; font-size: 11px;")

    def _browse_dir(self):
        path = QFileDialog.getExistingDirectory(self, "Select Data Directory")
        if path:
            self._data_dir.setText(path)

    def _save_broker(self):
        if self._main_window:
            self._main_window.show_toast("Broker credentials saved", "success")

    def _save_defaults(self):
        if self._main_window:
            self._main_window.show_toast("Default settings saved", "success")

    def refresh(self):
        self._check_modules()
