# Quanta Engine

Self-improving prediction and trading engine. Integrates **quanta-oracle** (forecasting) with **quanta-finance** (trading) into a single feedback loop.

## The Feedback Loop

```
 +------------------+      +------------------+      +------------------+
 |   Market Data    | ---> |  Models Train     | ---> |   Predictions    |
 +------------------+      +------------------+      +------------------+
                                                             |
 +------------------+      +------------------+              v
 |  Models Improve  | <--- |  Track Results   | <--- +------------------+
 +------------------+      +------------------+      | Trades Execute   |
                                                      +------------------+
```

1. **Data** flows in (candles from Yahoo Finance or broker).
2. **Oracle models** (ARIMA, Prophet, Neural) learn the patterns.
3. **Predictions** are ensembled with dynamic weights.
4. **Trades** execute through AutoTrader (paper or live via Alpaca).
5. **Results** are tracked -- did the prediction get the direction right?
6. **Models improve** -- accurate models get higher weight, poor ones shrink.

## Install

```bash
pip install -e ../quanta-oracle
pip install -e ../quanta-finance
pip install -e .
```

## Usage

### Run the engine (paper trading)

```bash
quanta-engine run --symbols AAPL,BTC-USD --paper --cycles 10
```

### Backtest the prediction strategy

```bash
quanta-engine backtest --symbols AAPL --days 252 --monte-carlo
```

### Check status

```bash
quanta-engine status
```

### Python API

```python
from quanta_engine.adaptive_engine import AdaptiveEngine
from quanta_engine.config import EngineConfig

config = EngineConfig(
    symbols=["AAPL", "BTC-USD"],
    models=["arima", "prophet"],
    paper_trading=True,
)

engine = AdaptiveEngine(config)
result = engine.run_cycle()
print(f"Equity: ${result['equity']:,.2f}")
print(f"Accuracy: {result['accuracy']:.0%}")
```

## Architecture

| Module | Role |
|---|---|
| `config.py` | Central configuration dataclass |
| `model_trainer.py` | Wraps quanta-oracle model fitting and prediction |
| `prediction_strategy.py` | Bridges oracle forecasts to quanta-finance Signals |
| `performance_tracker.py` | Tracks accuracy and computes dynamic model weights |
| `adaptive_engine.py` | Main loop wiring everything together |
| `cli.py` | Command-line interface |

## Dependencies

- **quanta-oracle** -- ARIMA, Prophet, Neural forecasting models
- **quanta-finance** -- AutoTrader, PaperBroker, Backtester, Candle/Signal types
- **numpy** >= 1.24
- **scipy** >= 1.10

## License

Copyright (c) 2022-2026 Zain Dana Harper. All rights reserved. See [LICENSE](LICENSE).
