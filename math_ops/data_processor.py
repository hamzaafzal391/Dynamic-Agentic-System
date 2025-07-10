import pandas as pd
import os
from typing import Dict, Any, List, Optional
from config import Config

class DataProcessor:
    """Handles CSV data processing for stock data and other structured data."""
    
    def __init__(self):
        self.stock_data_dir = Config.STOCK_DATA_DIR
        self.data_cache = {}
        self._load_sample_data()
    
    def _load_sample_data(self):
        """Load sample stock data if no CSV files exist."""
        try:
            os.makedirs(self.stock_data_dir, exist_ok=True)
            
            # Create sample stock data if directory is empty
            if not os.listdir(self.stock_data_dir):
                self._create_sample_stock_data()
                
        except Exception as e:
            print(f"Failed to initialize data directory: {e}")
    
    def _create_sample_stock_data(self):
        """Create sample stock data CSV files."""
        import datetime
        
        # Sample data for multiple stocks
        stocks_data = {
            'AAPL': [
                {'date': '2024-01-01', 'open': 150.0, 'close': 155.0, 'high': 157.0, 'low': 149.0, 'volume': 1000000},
                {'date': '2024-01-02', 'open': 155.0, 'close': 160.0, 'high': 162.0, 'low': 154.0, 'volume': 1200000},
                {'date': '2024-01-03', 'open': 160.0, 'close': 158.0, 'high': 161.0, 'low': 157.0, 'volume': 1100000},
                {'date': '2024-01-04', 'open': 158.0, 'close': 165.0, 'high': 166.0, 'low': 157.0, 'volume': 1300000},
                {'date': '2024-01-05', 'open': 165.0, 'close': 163.0, 'high': 167.0, 'low': 162.0, 'volume': 1150000},
            ],
            'GOOGL': [
                {'date': '2024-01-01', 'open': 2800.0, 'close': 2850.0, 'high': 2870.0, 'low': 2790.0, 'volume': 500000},
                {'date': '2024-01-02', 'open': 2850.0, 'close': 2900.0, 'high': 2920.0, 'low': 2840.0, 'volume': 600000},
                {'date': '2024-01-03', 'open': 2900.0, 'close': 2880.0, 'high': 2910.0, 'low': 2870.0, 'volume': 550000},
                {'date': '2024-01-04', 'open': 2880.0, 'close': 2950.0, 'high': 2960.0, 'low': 2870.0, 'volume': 650000},
                {'date': '2024-01-05', 'open': 2950.0, 'close': 2930.0, 'high': 2970.0, 'low': 2920.0, 'volume': 580000},
            ],
            'MSFT': [
                {'date': '2024-01-01', 'open': 350.0, 'close': 355.0, 'high': 357.0, 'low': 349.0, 'volume': 800000},
                {'date': '2024-01-02', 'open': 355.0, 'close': 360.0, 'high': 362.0, 'low': 354.0, 'volume': 900000},
                {'date': '2024-01-03', 'open': 360.0, 'close': 358.0, 'high': 361.0, 'low': 357.0, 'volume': 850000},
                {'date': '2024-01-04', 'open': 358.0, 'close': 365.0, 'high': 366.0, 'low': 357.0, 'volume': 950000},
                {'date': '2024-01-05', 'open': 365.0, 'close': 363.0, 'high': 367.0, 'low': 362.0, 'volume': 880000},
            ]
        }
        
        # Create CSV files for each stock
        for symbol, data in stocks_data.items():
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            file_path = os.path.join(self.stock_data_dir, f"{symbol}.csv")
            df.to_csv(file_path, index=False)
            print(f"Created sample data for {symbol}: {file_path}")
    
    def get_available_datasets(self) -> Dict[str, Any]:
        """Get list of available datasets."""
        try:
            datasets = []
            
            # List files in the stock data directory
            if os.path.exists(self.stock_data_dir):
                for file in os.listdir(self.stock_data_dir):
                    if file.endswith('.csv'):
                        dataset_name = file.replace('.csv', '')
                        file_path = os.path.join(self.stock_data_dir, file)
                        
                        # Read the CSV to get actual structure
                        try:
                            df = pd.read_csv(file_path)
                            datasets.append({
                                "name": dataset_name,
                                "type": "stock_data",
                                "file": file,
                                "file_path": file_path,
                                "rows": len(df),
                                "columns": list(df.columns),
                                "file_type": "csv"
                            })
                        except Exception as e:
                            # Fallback if CSV can't be read
                            datasets.append({
                                "name": dataset_name,
                                "type": "stock_data",
                                "file": file,
                                "file_path": file_path,
                                "rows": 0,
                                "columns": [],
                                "file_type": "csv"
                            })
            
            return {
                "success": True,
                "datasets": datasets
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def load_dataset(self, dataset_name: str) -> Optional[pd.DataFrame]:
        """Load a specific dataset by name."""
        try:
            file_path = os.path.join(self.stock_data_dir, f"{dataset_name}.csv")
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                df['date'] = pd.to_datetime(df['date'])
                return df
            else:
                return None
                
        except Exception as e:
            print(f"Failed to load dataset {dataset_name}: {e}")
            return None
    
    def query_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Query stock data for a specific symbol."""
        try:
            # Check if dataset exists
            file_path = os.path.join(self.stock_data_dir, f"{symbol}.csv")
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"Dataset not found for symbol: {symbol}"
                }
            
            # Load dataset
            df = pd.read_csv(file_path)
            
            # Convert to list of dictionaries
            data = df.to_dict('records')
            
            return {
                "success": True,
                "data": data,
                "symbol": symbol,
                "rows": len(data)
            }
            
        except Exception as e:
            print(f"Failed to query stock data for {symbol}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def calculate_moving_average(self, symbol: str, window: int = 20, 
                               start_date: Optional[str] = None, 
                               end_date: Optional[str] = None) -> Dict[str, Any]:
        """Calculate moving average for a stock."""
        try:
            df = self.load_dataset(symbol)
            if df is None:
                return {"error": f"Dataset not found: {symbol}"}
            
            # Filter by date range if provided
            if start_date:
                df = df[df['date'] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df['date'] <= pd.to_datetime(end_date)]
            
            # Sort by date
            df = df.sort_values('date')
            
            # Calculate moving average
            df[f'MA_{window}'] = df['close'].rolling(window=window).mean()
            
            # Remove NaN values
            result_df = df.dropna()
            
            return {
                "success": True,
                "symbol": symbol,
                "window": window,
                "data": result_df[['date', 'close', f'MA_{window}']].to_dict('records'),
                "rows": len(result_df)
            }
            
        except Exception as e:
            print(f"Failed to calculate moving average for {symbol}: {e}")
            return {"error": f"Failed to calculate moving average: {str(e)}"}
    
    def get_stock_statistics(self, symbol: str) -> Dict[str, Any]:
        """Get basic statistics for a stock."""
        try:
            df = self.load_dataset(symbol)
            if df is None:
                return {"error": f"Dataset not found: {symbol}"}
            
            stats = {
                "symbol": symbol,
                "total_days": len(df),
                "price_stats": {
                    "open": {
                        "min": float(df['open'].min()),
                        "max": float(df['open'].max()),
                        "mean": float(df['open'].mean()),
                        "std": float(df['open'].std())
                    },
                    "close": {
                        "min": float(df['close'].min()),
                        "max": float(df['close'].max()),
                        "mean": float(df['close'].mean()),
                        "std": float(df['close'].std())
                    },
                    "high": {
                        "min": float(df['high'].min()),
                        "max": float(df['high'].max()),
                        "mean": float(df['high'].mean()),
                        "std": float(df['high'].std())
                    },
                    "low": {
                        "min": float(df['low'].min()),
                        "max": float(df['low'].max()),
                        "mean": float(df['low'].mean()),
                        "std": float(df['low'].std())
                    }
                },
                "volume_stats": {
                    "total": int(df['volume'].sum()),
                    "mean": float(df['volume'].mean()),
                    "max": int(df['volume'].max()),
                    "min": int(df['volume'].min())
                },
                "date_range": {
                    "start": df['date'].min().strftime('%Y-%m-%d'),
                    "end": df['date'].max().strftime('%Y-%m-%d')
                }
            }
            
            return {"success": True, "statistics": stats}
            
        except Exception as e:
            print(f"Failed to get statistics for {symbol}: {e}")
            return {"error": f"Failed to get statistics: {str(e)}"}
    
    def search_stocks(self, query: str) -> Dict[str, Any]:
        """Search for stocks based on query."""
        try:
            available_datasets = self.get_available_datasets()
            if not available_datasets.get("success"):
                return available_datasets
            
            matching_stocks = []
            query_lower = query.lower()
            
            for dataset in available_datasets["datasets"]:
                symbol = dataset["name"]
                if query_lower in symbol.lower():
                    matching_stocks.append(symbol)
            
            return {
                "success": True,
                "query": query,
                "matching_stocks": matching_stocks,
                "count": len(matching_stocks)
            }
            
        except Exception as e:
            print(f"Failed to search stocks: {e}")
            return {"error": f"Failed to search stocks: {str(e)}"}

# Global data processor instance
data_processor = DataProcessor() 