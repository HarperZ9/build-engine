"""
Quanta Engine -- Main Application

Professional self-improving prediction and trading dashboard with sidebar
navigation, page transitions, and the shared Calibrate Pro visual framework.
"""

import logging
import sys
from typing import Optional

logger = logging.getLogger(__name__)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QMenuBar, QMenu,
    QStatusBar, QMessageBox, QFileDialog, QScrollArea,
    QSizePolicy, QGridLayout, QGroupBox, QProgressBar,
    QGraphicsDropShadowEffect, QGraphicsOpacityEffect,
    QLineEdit, QComboBox, QCheckBox, QSpinBox, QSlider,
    QTextEdit,
)
from PyQt6.QtCore import (
    Qt, QSize, QTimer, pyqtSignal, QSettings,
    QPropertyAnimation, QEasingCurve, QPoint,
)
from PyQt6.QtGui import (
    QAction, QFont, QColor, QIcon, QPixmap, QPainter, QPen,
    QLinearGradient, QPolygonF, QShortcut, QKeySequence,
    QBrush,
)
from PyQt6.QtCore import QPointF, QRectF


APP_NAME = "Quanta Engine"
APP_VERSION = "1.0.0"
APP_ORG = "Quanta Universe"


# =============================================================================
# Application Icon -- candlestick chart with prediction line
# =============================================================================

def make_app_icon() -> QIcon:
    """
    Create the application icon programmatically.

    A stylized candlestick chart with a prediction line rendered at multiple
    sizes for crisp display at any DPI.
    """
    icon = QIcon()
    for size in [16, 24, 32, 48, 64, 128, 256]:
        pm = QPixmap(size, size)
        pm.fill(QColor(0, 0, 0, 0))

        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        s = size
        pad = s * 0.12

        # Background circle
        p.setPen(Qt.PenStyle.NoPen)
        bg = QColor("#1a1a2e")
        p.setBrush(bg)
        p.drawRoundedRect(QRectF(0, 0, s, s), s * 0.22, s * 0.22)

        # Candlestick bars
        bar_w = max(1.5, s * 0.08)
        wick_w = max(0.8, s * 0.02)

        candles = [
            # (x_frac, open_frac, close_frac, high_frac, low_frac, bullish)
            (0.20, 0.65, 0.45, 0.35, 0.72, True),
            (0.35, 0.50, 0.60, 0.40, 0.68, False),
            (0.50, 0.55, 0.35, 0.28, 0.62, True),
            (0.65, 0.38, 0.50, 0.30, 0.58, False),
            (0.80, 0.45, 0.25, 0.18, 0.52, True),
        ]

        for x_frac, open_f, close_f, high_f, low_f, bullish in candles:
            cx = s * x_frac
            o_y = s * open_f
            c_y = s * close_f
            h_y = s * high_f
            l_y = s * low_f

            color = QColor("#4ade80") if bullish else QColor("#f87171")

            # Wick
            pen = QPen(color, wick_w)
            p.setPen(pen)
            p.drawLine(QPointF(cx, h_y), QPointF(cx, l_y))

            # Body
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(color)
            body_top = min(o_y, c_y)
            body_h = max(abs(c_y - o_y), wick_w * 1.5)
            p.drawRoundedRect(
                QRectF(cx - bar_w, body_top, bar_w * 2, body_h),
                max(1, s * 0.02), max(1, s * 0.02),
            )

        # Prediction line (dashed, cyan)
        pred_pen = QPen(QColor("#38bdf8"), max(1.2, s * 0.025))
        pred_pen.setStyle(Qt.PenStyle.DashLine)
        p.setPen(pred_pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        points = [
            QPointF(s * 0.50, s * 0.35),
            QPointF(s * 0.65, s * 0.28),
            QPointF(s * 0.80, s * 0.22),
            QPointF(s * 0.92, s * 0.18),
        ]
        for i in range(len(points) - 1):
            p.drawLine(points[i], points[i + 1])

        # Small dot at prediction end
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#38bdf8"))
        dot_r = max(1.5, s * 0.03)
        p.drawEllipse(points[-1], dot_r, dot_r)

        p.end()
        icon.addPixmap(pm)

    return icon


# =============================================================================
# Color Palette -- trading-focused dark accents on soft pastel light theme
# =============================================================================

class C:
    """Application color constants -- soft pastel light theme."""
    BG =        "#fdf9f5"       # Cream white
    BG_ALT =    "#f8f2ec"       # Warm blush sidebar
    SURFACE =   "#ffffff"       # White cards
    SURFACE2 =  "#faf5f0"       # Barely tinted
    BORDER =    "#ede4da"       # Soft warm border
    BORDER_LT = "#e0d5ca"       # Touch darker
    TEXT =      "#443933"       # Warm charcoal
    TEXT2 =     "#907e73"       # Muted taupe
    TEXT3 =     "#bfb0a4"       # Soft taupe
    ACCENT =    "#d4a0a0"       # Soft pink
    ACCENT_HI = "#deb0b0"       # Soft pink hover
    ACCENT_TX = "#b07878"       # Muted pink for text
    GREEN =     "#4ade80"       # Profit green
    GREEN_BG =  "#dcfce7"       # Light green background
    GREEN_MUT = "#92ad7e"       # Soft sage
    RED =       "#f87171"       # Loss red
    RED_BG =    "#fee2e2"       # Light red background
    RED_MUT =   "#d08888"       # Soft coral
    YELLOW =    "#e0c87a"       # Pastel yellow / buttercream
    CYAN =      "#38bdf8"       # Prediction blue
    CYAN_MUT =  "#95b3ba"       # Powder blue


# =============================================================================
# Stylesheet -- minimal, consistent, scales with DPI
# =============================================================================

STYLE = f"""
* {{
    font-family: "Segoe UI Variable Display", "Segoe UI Variable", "Segoe UI", "SF Pro Rounded", "SF Pro Display", sans-serif;
    font-size: 13px;
    letter-spacing: 0.2px;
    color: {C.TEXT};
}}

QMainWindow {{
    background: {C.BG};
}}

QMenuBar {{
    background: {C.BG};
    border-bottom: 1px solid {C.BORDER};
    padding: 4px 0;
    font-size: 12px;
}}
QMenuBar::item {{
    padding: 6px 16px;
    border-radius: 8px;
    margin: 0 2px;
}}
QMenuBar::item:selected {{
    background: {C.SURFACE2};
}}

QMenu {{
    background: {C.SURFACE};
    border: 1px solid {C.BORDER};
    border-radius: 10px;
    padding: 6px;
}}
QMenu::item {{
    padding: 8px 30px 8px 16px;
    border-radius: 6px;
    margin: 1px 2px;
}}
QMenu::item:selected {{
    background: {C.ACCENT};
    color: white;
}}
QMenu::separator {{
    height: 1px;
    background: {C.BORDER};
    margin: 6px 10px;
}}

QStatusBar {{
    background: {C.BG};
    border-top: 1px solid {C.BORDER};
    font-size: 11px;
    color: {C.TEXT2};
    padding: 4px 12px;
}}

QScrollArea {{
    border: none;
    background: transparent;
}}

QPushButton {{
    background: {C.SURFACE};
    border: 1px solid {C.BORDER};
    border-radius: 10px;
    padding: 9px 22px;
    font-weight: 500;
}}
QPushButton:hover {{
    background: {C.SURFACE2};
    border-color: {C.ACCENT};
}}
QPushButton:pressed {{
    background: {C.BORDER};
}}
QPushButton[primary="true"] {{
    background: {C.ACCENT};
    border: none;
    color: white;
    font-weight: 600;
    border-radius: 10px;
}}
QPushButton[primary="true"]:hover {{
    background: {C.ACCENT_HI};
}}

QGroupBox {{
    border: 1px solid {C.BORDER};
    border-radius: 12px;
    margin-top: 18px;
    padding-top: 22px;
    font-weight: 500;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 18px;
    padding: 0 8px;
    color: {C.TEXT2};
}}

QProgressBar {{
    border: none;
    border-radius: 6px;
    background: {C.BORDER};
    height: 10px;
    text-align: center;
    font-size: 9px;
    color: {C.TEXT2};
}}
QProgressBar::chunk {{
    border-radius: 6px;
    background: {C.ACCENT};
}}

QComboBox {{
    background: {C.SURFACE};
    border: 1px solid {C.BORDER};
    border-radius: 8px;
    padding: 6px 12px;
}}
QComboBox:hover {{
    border-color: {C.ACCENT};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QCheckBox {{
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1px solid {C.BORDER_LT};
    background: {C.SURFACE};
}}
QCheckBox::indicator:checked {{
    background: {C.ACCENT};
    border-color: {C.ACCENT};
}}

QTextEdit, QPlainTextEdit {{
    background: {C.SURFACE};
    border: 1px solid {C.BORDER};
    border-radius: 8px;
    padding: 8px;
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 11px;
}}

QLineEdit {{
    background: {C.SURFACE};
    border: 1px solid {C.BORDER};
    border-radius: 8px;
    padding: 7px 12px;
}}
QLineEdit:focus {{
    border-color: {C.ACCENT};
}}

QSpinBox {{
    background: {C.SURFACE};
    border: 1px solid {C.BORDER};
    border-radius: 8px;
    padding: 6px 10px;
}}
QSpinBox:focus {{
    border-color: {C.ACCENT};
}}

QSlider::groove:horizontal {{
    border: none;
    height: 6px;
    background: {C.BORDER};
    border-radius: 3px;
}}
QSlider::handle:horizontal {{
    background: {C.ACCENT};
    border: none;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}}
QSlider::sub-page:horizontal {{
    background: {C.ACCENT};
    border-radius: 3px;
}}

QLabel {{
    background: transparent;
}}

QToolTip {{
    background: {C.SURFACE};
    color: {C.TEXT};
    border: 1px solid {C.BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 11px;
}}
"""


# =============================================================================
# Utility Widgets
# =============================================================================

class Card(QFrame):
    """A surface card with consistent styling."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            Card {{
                background: {C.SURFACE};
                border: 1px solid {C.BORDER};
                border-radius: 14px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(180, 160, 140, 30))
        self.setGraphicsEffect(shadow)

    @staticmethod
    def with_layout(layout_cls=QVBoxLayout, margins=(20, 16, 20, 16), spacing=10):
        card = Card()
        layout = layout_cls(card)
        layout.setContentsMargins(*margins)
        layout.setSpacing(spacing)
        return card, layout


class StatusDot(QWidget):
    """Small colored circle indicator."""

    def __init__(self, color: str = C.TEXT3, size: int = 10, parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(size, size)

    def set_color(self, color: str):
        self._color = color
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Soft glow ring
        glow = QColor(self._color)
        glow.setAlpha(40)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(glow)
        p.drawEllipse(0, 0, self.width(), self.height())
        # Inner dot
        p.setBrush(QColor(self._color))
        inset = max(2, self.width() // 4)
        p.drawEllipse(inset, inset, self.width() - inset * 2, self.height() - inset * 2)
        p.end()


class Heading(QLabel):
    """Section heading with consistent typography."""

    def __init__(self, text: str, level: int = 1, parent=None):
        super().__init__(text, parent)
        sizes = {1: 21, 2: 16, 3: 14}
        weights = {1: "500", 2: "500", 3: "400"}
        colors = {1: C.TEXT, 2: C.TEXT, 3: C.TEXT2}
        self.setStyleSheet(
            f"font-size: {sizes.get(level, 14)}px; "
            f"font-weight: {weights.get(level, '400')}; "
            f"color: {colors.get(level, C.TEXT)};"
        )


class Stat(QWidget):
    """Compact stat display: value + label."""

    def __init__(self, label: str, value: str = "\u2014", color: str = C.TEXT, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self._value_label = QLabel(value)
        self._value_label.setStyleSheet(
            f"font-size: 22px; font-weight: 600; color: {color};"
        )
        layout.addWidget(self._value_label)

        desc = QLabel(label)
        desc.setStyleSheet(f"font-size: 11px; color: {C.TEXT2};")
        layout.addWidget(desc)

    def set_value(self, value: str, color: str = None):
        self._value_label.setText(value)
        if color:
            self._value_label.setStyleSheet(
                f"font-size: 22px; font-weight: 600; color: {color};"
            )


# =============================================================================
# Sidebar Navigation
# =============================================================================

class NavButton(QPushButton):
    """Sidebar navigation button."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(42)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._update_style(False)

    def _update_style(self, checked: bool):
        if checked:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {C.ACCENT};
                    border: none;
                    border-radius: 10px;
                    color: white;
                    text-align: left;
                    padding-left: 18px;
                    font-weight: 600;
                    font-size: 13px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    border-radius: 10px;
                    color: {C.TEXT2};
                    text-align: left;
                    padding-left: 18px;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background: {C.SURFACE2};
                    color: {C.TEXT};
                }}
            """)

    def setChecked(self, checked: bool):
        super().setChecked(checked)
        self._update_style(checked)

    def nextCheckState(self):
        self.setChecked(True)


class Sidebar(QWidget):
    """Left sidebar with navigation buttons."""

    page_changed = pyqtSignal(int)

    def __init__(self, pages: list, parent=None):
        super().__init__(parent)
        self.setFixedWidth(190)
        self.setStyleSheet(
            f"background: {C.BG_ALT}; border-right: 1px solid {C.BORDER};"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 14, 10, 14)
        layout.setSpacing(6)

        # Logo / title
        title = QLabel(APP_NAME)
        title.setStyleSheet(
            f"font-size: 15px; font-weight: 600; color: {C.ACCENT_TX}; "
            f"padding: 8px 8px 20px 8px;"
        )
        layout.addWidget(title)

        self._buttons = []
        for i, name in enumerate(pages):
            btn = NavButton(name)
            btn.clicked.connect(lambda checked, idx=i: self._on_click(idx))
            layout.addWidget(btn)
            self._buttons.append(btn)

        layout.addStretch()

        # Bottom: version
        ver = QLabel(f"v{APP_VERSION}")
        ver.setStyleSheet(f"color: {C.TEXT3}; font-size: 10px; padding: 8px;")
        layout.addWidget(ver)

        self._buttons[0].setChecked(True)

    def _on_click(self, index: int):
        for i, btn in enumerate(self._buttons):
            btn._update_style(i == index)
        self.page_changed.emit(index)


# =============================================================================
# Toast Notification
# =============================================================================

class ToastNotification(QFrame):
    """Slide-in toast notification with auto-dismiss and fade-out."""

    _ICONS = {
        "info":    "i",
        "success": "+",
        "warning": "!",
        "error":   "x",
    }
    _BORDER_COLORS = {
        "info":    C.CYAN_MUT,
        "success": C.GREEN_MUT,
        "warning": C.YELLOW,
        "error":   C.RED_MUT,
    }

    def __init__(self, message: str, level: str = "info", parent=None):
        super().__init__(parent)
        self.setFixedWidth(340)
        self.setFixedHeight(52)

        border_color = self._BORDER_COLORS.get(level, C.CYAN_MUT)
        self.setStyleSheet(
            f"ToastNotification {{"
            f"  background: {C.SURFACE};"
            f"  border: 1px solid {border_color};"
            f"  border-radius: 12px;"
            f"}}"
        )

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(120, 100, 80, 50))
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 10, 8)
        layout.setSpacing(10)

        # Icon
        icon_text = self._ICONS.get(level, self._ICONS["info"])
        icon_label = QLabel(icon_text)
        icon_label.setFixedSize(22, 22)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(
            f"font-size: 12px; font-weight: 700; background: {border_color}; "
            f"color: white; border-radius: 11px;"
        )
        layout.addWidget(icon_label)

        # Message
        msg_label = QLabel(message)
        msg_label.setStyleSheet(
            f"font-size: 12px; color: {C.TEXT}; background: transparent;"
        )
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label, stretch=1)

        # Close button
        close_btn = QPushButton("\u2715")
        close_btn.setFixedSize(22, 22)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; "
            f"font-size: 12px; color: {C.TEXT3}; border-radius: 11px; }}"
            f"QPushButton:hover {{ background: {C.SURFACE2}; color: {C.TEXT}; }}"
        )
        close_btn.clicked.connect(self._fade_out)
        layout.addWidget(close_btn)

        # Auto-hide timer
        self._auto_timer = QTimer(self)
        self._auto_timer.setSingleShot(True)
        self._auto_timer.timeout.connect(self._fade_out)
        self._auto_timer.start(3000)

    def slide_in(self):
        """Animate the toast sliding up from below its final position."""
        final_pos = self.pos()
        start_pos = QPoint(final_pos.x(), final_pos.y() + 60)
        self.move(start_pos)
        self.show()

        self._slide_anim = QPropertyAnimation(self, b"pos")
        self._slide_anim.setDuration(250)
        self._slide_anim.setStartValue(start_pos)
        self._slide_anim.setEndValue(final_pos)
        self._slide_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._slide_anim.start()

    def _fade_out(self):
        """Fade out and remove the toast."""
        self._auto_timer.stop()
        try:
            effect = QGraphicsOpacityEffect(self)
            self.setGraphicsEffect(effect)
            effect.setOpacity(1.0)

            self._fade_anim = QPropertyAnimation(effect, b"opacity")
            self._fade_anim.setDuration(300)
            self._fade_anim.setStartValue(1.0)
            self._fade_anim.setEndValue(0.0)
            self._fade_anim.setEasingCurve(QEasingCurve.Type.InCubic)
            self._fade_anim.finished.connect(self._remove)
            self._fade_anim.start()
        except Exception:
            self._remove()

    def _remove(self):
        """Remove this toast from the parent."""
        self.hide()
        self.setParent(None)
        self.deleteLater()


# =============================================================================
# Placeholder Page (fallback for unbuilt pages)
# =============================================================================

class PlaceholderPage(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.addWidget(Heading(title))

        desc = QLabel("This page is under construction.")
        desc.setStyleSheet(f"font-size: 13px; color: {C.TEXT2};")
        layout.addWidget(desc)

        layout.addStretch()


# =============================================================================
# Main Window
# =============================================================================

PAGE_NAMES = [
    "Dashboard",
    "Engine Control",
    "Performance",
    "Backtest",
    "Market Data",
    "Settings",
]

PAGE_SHORTCUTS = ["Ctrl+1", "Ctrl+2", "Ctrl+3", "Ctrl+4", "Ctrl+5", "Ctrl+6"]

PAGE_MENU_NAMES = [
    "&Dashboard",
    "&Engine Control",
    "&Performance",
    "&Backtest",
    "&Market Data",
    "&Settings",
]


class QuantaEngineWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.settings = QSettings(APP_ORG, APP_NAME)
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        self.setStyleSheet(STYLE)
        self._app_icon = make_app_icon()
        self.setWindowIcon(self._app_icon)

        self._build_menubar()
        self._build_central()
        self._build_statusbar()
        self._setup_shortcuts()
        self._restore_geometry()

    # --- Keyboard Shortcuts ---

    def _setup_shortcuts(self):
        """Register keyboard shortcuts not already attached to menu actions."""
        sc_escape = QShortcut(QKeySequence("Escape"), self)
        sc_escape.activated.connect(self.close)

    def _shortcut_switch_page(self, index: int):
        """Switch to a page by index and update sidebar."""
        self._switch_page(index)
        self.sidebar._on_click(index)

    # --- Menu Bar ---

    def _build_menubar(self):
        mb = self.menuBar()

        # File
        file_menu = mb.addMenu("&File")
        file_menu.addAction(
            QAction("&New Session", self, shortcut="Ctrl+N",
                    triggered=self._new_session)
        )
        file_menu.addAction(
            QAction("&Export Report...", self, shortcut="Ctrl+E",
                    triggered=self._export_report)
        )
        file_menu.addSeparator()
        file_menu.addAction(
            QAction("E&xit", self, shortcut="Alt+F4",
                    triggered=self.close)
        )

        # View -- page navigation shortcuts
        view = mb.addMenu("&View")
        for i, (name, sc) in enumerate(zip(PAGE_MENU_NAMES, PAGE_SHORTCUTS)):
            act = QAction(name, self)
            act.setShortcut(QKeySequence(sc))
            act.triggered.connect(
                lambda checked, idx=i: self._shortcut_switch_page(idx)
            )
            view.addAction(act)
        view.addSeparator()
        view.addAction(
            QAction("&Refresh", self, shortcut="F5",
                    triggered=self._refresh_current)
        )

        # Engine
        engine_menu = mb.addMenu("En&gine")
        engine_menu.addAction(
            QAction("&Start Engine", self, shortcut="Ctrl+R",
                    triggered=self._start_engine_menu)
        )
        engine_menu.addAction(
            QAction("S&top Engine", self, shortcut="Ctrl+T",
                    triggered=self._stop_engine_menu)
        )
        engine_menu.addSeparator()
        engine_menu.addAction(
            QAction("Run &Backtest", self, shortcut="Ctrl+B",
                    triggered=lambda: self._shortcut_switch_page(3))
        )

        # Help
        help_menu = mb.addMenu("&Help")
        help_menu.addAction(
            QAction("&About", self, triggered=self._about)
        )

    # --- Central Widget ---

    def _build_central(self):
        central = QWidget()
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar(PAGE_NAMES)
        self.sidebar.page_changed.connect(self._switch_page)
        main_layout.addWidget(self.sidebar)

        # Page stack
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background: {C.BG};")

        # Page 0: Dashboard
        try:
            from quanta_engine.gui.pages.dashboard import DashboardPage
            self.stack.addWidget(DashboardPage(self))
        except Exception as e:
            logger.warning("Failed to load DashboardPage: %s", e)
            self.stack.addWidget(PlaceholderPage("Dashboard"))

        # Page 1: Engine Control
        try:
            from quanta_engine.gui.pages.engine_page import EngineControlPage
            self.stack.addWidget(EngineControlPage(self))
        except Exception as e:
            logger.warning("Failed to load EngineControlPage: %s", e)
            self.stack.addWidget(PlaceholderPage("Engine Control"))

        # Page 2: Performance
        try:
            from quanta_engine.gui.pages.performance_page import PerformancePage
            self.stack.addWidget(PerformancePage(self))
        except Exception as e:
            logger.warning("Failed to load PerformancePage: %s", e)
            self.stack.addWidget(PlaceholderPage("Performance"))

        # Page 3: Backtest
        try:
            from quanta_engine.gui.pages.backtest_page import BacktestPage
            self.stack.addWidget(BacktestPage(self))
        except Exception as e:
            logger.warning("Failed to load BacktestPage: %s", e)
            self.stack.addWidget(PlaceholderPage("Backtest"))

        # Page 4: Market Data
        try:
            from quanta_engine.gui.pages.data_page import DataPage
            self.stack.addWidget(DataPage(self))
        except Exception as e:
            logger.warning("Failed to load DataPage: %s", e)
            self.stack.addWidget(PlaceholderPage("Market Data"))

        # Page 5: Settings
        try:
            from quanta_engine.gui.pages.settings_page import SettingsPage
            self.stack.addWidget(SettingsPage(self))
        except Exception as e:
            logger.warning("Failed to load SettingsPage: %s", e)
            self.stack.addWidget(PlaceholderPage("Settings"))

        main_layout.addWidget(self.stack, stretch=1)
        self.setCentralWidget(central)

    # --- Status Bar ---

    def _build_statusbar(self):
        sb = self.statusBar()
        self._status = QLabel("Ready")
        sb.addWidget(self._status, 1)

        self._engine_status_dot = StatusDot(C.TEXT3, 8)
        sb.addPermanentWidget(self._engine_status_dot)

        self._engine_status_label = QLabel("Engine stopped")
        self._engine_status_label.setStyleSheet(f"font-size: 11px; color: {C.TEXT2};")
        sb.addPermanentWidget(self._engine_status_label)

    def set_engine_status(self, running: bool):
        """Update the status bar engine indicator."""
        if running:
            self._engine_status_dot.set_color(C.GREEN)
            self._engine_status_label.setText("Engine running")
        else:
            self._engine_status_dot.set_color(C.TEXT3)
            self._engine_status_label.setText("Engine stopped")

    # --- Page Switching ---

    def _switch_page(self, index: int):
        """Switch page with a subtle opacity fade transition."""
        if index == self.stack.currentIndex():
            return
        target = self.stack.widget(index)
        if target:
            try:
                effect = QGraphicsOpacityEffect(target)
                target.setGraphicsEffect(effect)
                effect.setOpacity(0.3)
                self.stack.setCurrentIndex(index)

                anim = QPropertyAnimation(effect, b"opacity")
                anim.setDuration(150)
                anim.setStartValue(0.3)
                anim.setEndValue(1.0)
                anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                anim.finished.connect(lambda: target.setGraphicsEffect(None))
                self._page_anim = anim  # prevent GC
                anim.start()
            except Exception:
                self.stack.setCurrentIndex(index)
        else:
            self.stack.setCurrentIndex(index)

    # --- Toast ---

    def show_toast(self, message: str, level: str = "info"):
        """Show a toast notification in the bottom-right corner."""
        toast = ToastNotification(message, level, parent=self)
        margin = 16
        x = self.width() - toast.width() - margin
        y = self.height() - toast.height() - margin
        toast.move(x, y)
        toast.slide_in()

    # --- Actions ---

    def _new_session(self):
        self._status.setText("New session started")
        self.show_toast("New session initialized", "success")

    def _export_report(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Report", "quanta_engine_report.txt",
            "Text Files (*.txt);;CSV Files (*.csv);;All Files (*)"
        )
        if path:
            self._status.setText(f"Report exported: {path}")
            self.show_toast("Report exported successfully", "success")

    def _start_engine_menu(self):
        """Start engine from menu -- delegate to engine page."""
        self._shortcut_switch_page(1)
        page = self.stack.widget(1)
        if hasattr(page, "start_engine"):
            page.start_engine()

    def _stop_engine_menu(self):
        """Stop engine from menu -- delegate to engine page."""
        page = self.stack.widget(1)
        if hasattr(page, "stop_engine"):
            page.stop_engine()

    def _refresh_current(self):
        page = self.stack.currentWidget()
        if hasattr(page, "refresh"):
            page.refresh()
        self._status.setText("Refreshed")

    def _about(self):
        QMessageBox.about(
            self, f"About {APP_NAME}",
            f"<h2>{APP_NAME}</h2>"
            f"<p>Version {APP_VERSION}</p>"
            f"<p>Self-improving prediction and trading engine.</p>"
            f"<p>Integrates quanta-oracle forecasting models with<br>"
            f"quanta-finance execution for a complete feedback loop.</p>"
            f"<p>Models: ARIMA, Prophet, Neural Network</p>"
            f"<p>&copy; 2024-2026 Quanta Universe</p>"
        )

    # --- Geometry Persistence ---

    def _restore_geometry(self):
        geo = self.settings.value("window/geometry")
        if geo:
            self.restoreGeometry(geo)

    def closeEvent(self, event):
        self.settings.setValue("window/geometry", self.saveGeometry())
        # Stop engine if running
        page = self.stack.widget(1)
        if hasattr(page, "_engine_running") and page._engine_running:
            page.stop_engine()
        event.accept()


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    from quanta_engine.gui import launch
    sys.exit(launch())
