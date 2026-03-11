from typing import List, Dict
import pandas as pd
import numpy as np
from strategies import PortfolioSnapshot


class PerformanceAnalytics:
    """
    Calculates trading performance metrics from portfolio history.
    """

    @staticmethod
    def calculate_metrics(
        history: List[PortfolioSnapshot], initial_capital: float
    ) -> Dict:
        if not history:
            return {}

        df = pd.DataFrame(
            [
                {
                    "timestamp": s.timestamp,
                    "equity": s.equity,
                    "cash": s.cash,
                    "positions_value": s.positions_value,
                }
                for s in history
            ]
        )

        df.set_index("timestamp", inplace=True)

        # Returns calculation
        df["returns"] = df["equity"].pct_change().fillna(0)

        total_return = (df["equity"].iloc[-1] / initial_capital) - 1

        # Volatility & Sharpe (assume 252 trading days * 24 hours if using 1h timeframe,
        # but simplified here for generic timeframe)
        # Assuming annualization factor needs to be adjusted by timeframe.
        # For now, just raw metrics.
        volatility = df["returns"].std()
        sharpe_ratio = (
            (df["returns"].mean() / volatility * np.sqrt(len(df)))
            if volatility > 0
            else 0
        )

        # Drawdown
        df["rolling_max"] = df["equity"].cummax()
        df["drawdown"] = (df["equity"] - df["rolling_max"]) / df["rolling_max"]
        max_drawdown = df["drawdown"].min()

        return {
            "total_return": total_return,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "volatility": volatility,
            "final_equity": df["equity"].iloc[-1],
            "peak_equity": df["equity"].max(),
            "history_df": df,
        }
