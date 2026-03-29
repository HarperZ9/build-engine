"""
Quanta Engine GUI — professional trading dashboard.

Launch with::

    from quanta_engine.gui import launch
    launch()
"""


def launch():
    """Launch the Quanta Engine GUI application."""
    import sys

    from PyQt6.QtWidgets import QApplication

    from quanta_engine.gui.app import QuantaEngineWindow

    app = QApplication(sys.argv)
    w = QuantaEngineWindow()
    w.show()
    return app.exec()
