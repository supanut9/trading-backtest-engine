from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import os

from backtest.engine import BacktestEngine
from backtest.data import DuckDBDataHandler
from backtest.execution import SimulatedBroker
from strategies.rule_based import SmaCrossStrategy, RSIStrategy, BreakoutStrategy, BollingerBandsStrategy, MACDStrategy
from strategies.ml.ml_strategy import MLStrategy
from strategies.ensemble import EnsembleStrategy
from pipeline.collector import DataCollector
from pipeline.db import TradingDB

app = FastAPI(title="Trading Backtest API")

# Allow requests from the Next.js dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BacktestRequest(BaseModel):
    symbol: str = "BTC/USDT"
    timeframe: str = "1h"
    strategy: str = "sma"
    days: int = 30
    exchange: str = "binance"
    initial_capital: float = 10000.0

@app.post("/api/v1/backtest")
async def run_backtest(req: BacktestRequest):
    # 1. Ensure data exists
    # If running from src, we need to go up to प्रोजेक्ट root
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../trading-data-pipeline/data/trading.db"))
    db = TradingDB(db_path=db_path)
    collector = DataCollector(exchange_id=req.exchange, db=db)
    
    try:
        collector.sync_historical_data(
            symbol=req.symbol, timeframe=req.timeframe, days=req.days
        )
        # Close connection to avoid DuckDB multi-connection conflict
        db.close()
    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=f"Data collection failed: {str(e)}")

    # 2. Setup Engine
    engine = BacktestEngine(initial_capital=req.initial_capital)
    engine.data_handler = DuckDBDataHandler(
        db_path=db_path,
        symbol=req.symbol,
        timeframe=req.timeframe,
        events_queue=engine.events,
    )
    engine.execution_handler = SimulatedBroker(
        events_queue=engine.events, commission=0.001
    )

    # 3. Select Strategy
    strategy_names = [s.strip().lower() for s in req.strategy.split(",")]
    
    def create_strategy(name, symbol):
        if name == "sma" or name == "sma_cross":
            return SmaCrossStrategy(symbol=symbol)
        elif name == "rsi":
            return RSIStrategy(symbol=symbol)
        elif name == "breakout":
            return BreakoutStrategy(symbol=symbol)
        elif name == "bollinger":
            return BollingerBandsStrategy(symbol=symbol)
        elif name == "macd":
            return MACDStrategy(symbol=symbol)
        elif name == "ml":
            model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../trading-ml-lab/models/rf_latest.pkl"))
            if not os.path.exists(model_path):
                raise HTTPException(status_code=404, detail="ML Model file not found. Please train a model first.")
            return MLStrategy(symbol=symbol, model_path=model_path)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported strategy: {name}")

    try:
        instances = [create_strategy(name, req.symbol) for name in strategy_names]
        
        if len(instances) == 1:
            engine.strategy = instances[0]
        else:
            engine.strategy = EnsembleStrategy(instances)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 4. Run
    try:
        metrics = engine.run()
        
        # Prepare response (remove non-serializable objects like DataFrame)
        response_metrics = {k: v for k, v in metrics.items() if k != "history_df"}
        
        # Ensure trades are included (they were added to metrics in engine.py)
        if "trades" in metrics:
            response_metrics["trades"] = metrics["trades"]
        
        # Add equity curve for charting
        if "history_df" in metrics:
            df = metrics["history_df"]
            # Convert timestamp index to ISO strings and equity to list
            response_metrics["equity_curve"] = [
                {"time": ts.isoformat(), "value": float(val)}
                for ts, val in zip(df.index, df["equity"])
            ]

        return response_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest execution failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
