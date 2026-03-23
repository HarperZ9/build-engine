"""
Engine configuration with sensible defaults for prediction-and-trading.

Covers symbol selection, risk management, model selection, and feedback-loop
tuning knobs.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EngineConfig:
    """Central configuration for the adaptive engine.

    Attributes
    ----------
    symbols:
        Ticker symbols to trade.
    risk_per_trade:
        Fraction of equity risked on each new position.
    max_positions:
        Maximum simultaneous open positions.
    paper_trading:
        If True, use PaperBroker; otherwise AlpacaBroker.
    models:
        Oracle model names to use (``"arima"``, ``"prophet"``, ``"neural"``).
    lookback_days:
        Number of historical days fed to models.
    forecast_horizon:
        Number of future steps to predict.
    retrain_interval_hours:
        Hours between automatic model retraining.
    min_confidence:
        Minimum signal strength to act on (0.0 .. 1.0).
    accuracy_window:
        Number of recent predictions used to compute model weights.
    direction_threshold:
        Minimum predicted move (as fraction) to classify as directional.
    """

    # Trading
    symbols: list[str] = field(default_factory=lambda: ["AAPL", "BTC-USD"])
    risk_per_trade: float = 0.02
    max_positions: int = 5
    paper_trading: bool = True

    # Prediction
    models: list[str] = field(default_factory=lambda: ["arima", "prophet"])
    lookback_days: int = 90
    forecast_horizon: int = 5
    retrain_interval_hours: int = 24

    # Feedback
    min_confidence: float = 0.3
    accuracy_window: int = 50
    direction_threshold: float = 0.005  # 0.5% move = directional signal
