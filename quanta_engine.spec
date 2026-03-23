import os
block_cipher = None
a = Analysis(
    ['quanta_engine/cli.py'], pathex=[os.path.abspath('.')],
    binaries=[], datas=[],
    hiddenimports=[
        'quanta_engine', 'quanta_engine.config', 'quanta_engine.adaptive_engine',
        'quanta_engine.prediction_strategy', 'quanta_engine.model_trainer',
        'quanta_engine.performance_tracker',
        'quanta_engine.gui', 'quanta_engine.gui.app',
        'quanta_engine.gui.pages.dashboard', 'quanta_engine.gui.pages.engine_page',
        'quanta_engine.gui.pages.performance_page', 'quanta_engine.gui.pages.backtest_page',
        'quanta_engine.gui.pages.data_page', 'quanta_engine.gui.pages.settings_page',
        'quanta_oracle', 'quanta_oracle.arima', 'quanta_oracle.prophet',
        'quanta_oracle.changepoint', 'quanta_oracle.decompose', 'quanta_oracle.neural',
        'quanta_oracle.metrics', 'quanta_oracle.features', 'quanta_oracle.autodiff',
        'quanta_finance', 'quanta_finance.data', 'quanta_finance.indicators',
        'quanta_finance.strategies', 'quanta_finance.risk', 'quanta_finance.sizing',
        'quanta_finance.orderbook', 'quanta_finance.backtest', 'quanta_finance.portfolio',
        'quanta_finance.market_data', 'quanta_finance.broker', 'quanta_finance.autotrader',
        'numpy', 'scipy', 'scipy.optimize',
        'PyQt6', 'PyQt6.QtWidgets', 'PyQt6.QtCore', 'PyQt6.QtGui',
    ],
    excludes=[], noarchive=False,
)
pyz = PYZ(a.pure, cipher=block_cipher)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='quanta-engine', console=True)
coll = COLLECT(exe, a.binaries, a.datas, name='quanta-engine')
