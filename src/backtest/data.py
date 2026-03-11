import duckdb
from strategies import Candle
from .events import DataEvent

class DuckDBDataHandler:
    def __init__(self, db_path: str, symbol: str, timeframe: str, events_queue):
        self.conn = duckdb.connect(db_path, read_only=True)
        self.symbol = symbol
        self.timeframe = timeframe
        self.events_queue = events_queue
        self.continue_backtest = True
        
        # Load all data into a generator/iterator
        self.iterator = self._load_data()

    def _load_data(self):
        """Load data from DuckDB and yield one candle at a time."""
        query = """
            SELECT timestamp, open, high, low, close, volume 
            FROM ohlcv 
            WHERE symbol = ? AND timeframe = ?
            ORDER BY timestamp ASC
        """
        df = self.conn.execute(query, [self.symbol, self.timeframe]).df()
        
        for _, row in df.iterrows():
            yield Candle(
                symbol=self.symbol,
                timestamp=row['timestamp'],
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                volume=float(row['volume'])
            )

    def stream_next_candle(self):
        """Fetch next candle and put into event queue."""
        try:
            candle = next(self.iterator)
            self.events_queue.put(DataEvent(candle=candle))
        except StopIteration:
            self.continue_backtest = False
