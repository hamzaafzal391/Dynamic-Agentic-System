import pandas as pd
import numpy as np
from typing import Dict, Any, List, Union, Optional
import json
import re

class MathComputation:
    """Handles mathematical computations and data analysis using Pandas."""
    
    def __init__(self):
        self.data_cache = {}
    
    def evaluate_expression(self, expression: str) -> Dict[str, Any]:
        """Evaluate a mathematical expression safely."""
        try:
            # Remove any potentially dangerous operations
            dangerous_patterns = [
                r'import\s+',
                r'exec\s*\(',
                r'eval\s*\(',
                r'__\w+__',
                r'open\s*\(',
                r'file\s*\(',
                r'input\s*\(',
                r'raw_input\s*\(',
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, expression, re.IGNORECASE):
                    return {"error": f"Potentially dangerous operation detected: {pattern}"}
            
            # Only allow safe mathematical operations
            allowed_chars = set('0123456789+-*/()., \t\n\r')
            if not all(c in allowed_chars for c in expression):
                return {"error": "Expression contains disallowed characters"}
            
            # Evaluate the expression
            result = eval(expression, {"__builtins__": {}}, {
                'abs': abs, 'round': round, 'min': min, 'max': max,
                'sum': sum, 'len': len, 'pow': pow
            })
            
            return {
                "expression": expression,
                "result": result,
                "type": type(result).__name__
            }
            
        except Exception as e:
            return {"error": f"Failed to evaluate expression: {str(e)}"}
    
    def analyze_dataframe(self, data: Union[List[Dict], pd.DataFrame], operations: List[str]) -> Dict[str, Any]:
        """Analyze data using Pandas operations."""
        try:
            # Convert to DataFrame if needed
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = data.copy()
            
            results = {}
            
            for operation in operations:
                op_lower = operation.lower()
                
                if op_lower == "describe":
                    results["describe"] = df.describe().to_dict()
                
                elif op_lower == "info":
                    # Use StringIO for proper buffer handling
                    from io import StringIO
                    buffer = StringIO()
                    df.info(buf=buffer, max_cols=None, memory_usage=True)
                    results["info"] = buffer.getvalue()
                
                elif op_lower == "head":
                    results["head"] = df.head().to_dict('records')
                
                elif op_lower == "tail":
                    results["tail"] = df.tail().to_dict('records')
                
                elif op_lower == "shape":
                    results["shape"] = df.shape
                
                elif op_lower == "columns":
                    results["columns"] = df.columns.tolist()
                
                elif op_lower == "dtypes":
                    results["dtypes"] = df.dtypes.to_dict()
                
                elif op_lower == "isnull":
                    results["null_counts"] = df.isnull().sum().to_dict()
                
                elif op_lower == "correlation":
                    numeric_df = df.select_dtypes(include=[np.number])
                    if len(numeric_df.columns) > 1:
                        results["correlation"] = numeric_df.corr().to_dict()
                    else:
                        results["correlation"] = "Not enough numeric columns for correlation"
                
                elif op_lower.startswith("groupby"):
                    # Extract column name from "groupby:column"
                    parts = operation.split(":")
                    if len(parts) == 2:
                        group_col = parts[1].strip()
                        if group_col in df.columns:
                            results[f"groupby_{group_col}"] = df.groupby(group_col).size().to_dict()
                        else:
                            results[f"groupby_{group_col}"] = f"Column '{group_col}' not found"
                    else:
                        results["groupby"] = "Invalid groupby syntax. Use 'groupby:column_name'"
                
                elif op_lower.startswith("value_counts"):
                    # Extract column name from "value_counts:column"
                    parts = operation.split(":")
                    if len(parts) == 2:
                        col = parts[1].strip()
                        if col in df.columns:
                            results[f"value_counts_{col}"] = df[col].value_counts().to_dict()
                        else:
                            results[f"value_counts_{col}"] = f"Column '{col}' not found"
                    else:
                        results["value_counts"] = "Invalid value_counts syntax. Use 'value_counts:column_name'"
            
            return {
                "success": True,
                "data_shape": df.shape,
                "operations": results
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze data: {str(e)}"}
    
    def calculate_statistics(self, data: Union[List[float], pd.Series], stats: Optional[List[str]] = None) -> Dict[str, Any]:
        """Calculate statistical measures for numerical data."""
        try:
            if isinstance(data, list):
                series = pd.Series(data)
            else:
                series = data
            
            results = {}
            
            # Default stats if none provided
            if stats is None:
                stats = ["mean", "median", "std", "min", "max", "count"]
                
            for stat in stats:
                stat_lower = stat.lower()
                
                if stat_lower == "mean":
                    results["mean"] = float(series.mean())
                elif stat_lower == "median":
                    results["median"] = float(series.median())
                elif stat_lower == "std":
                    results["std"] = float(series.std())
                elif stat_lower == "var":
                    results["variance"] = float(series.var())
                elif stat_lower == "min":
                    results["min"] = float(series.min())
                elif stat_lower == "max":
                    results["max"] = float(series.max())
                elif stat_lower == "sum":
                    results["sum"] = float(series.sum())
                elif stat_lower == "count":
                    results["count"] = int(series.count())
                elif stat_lower == "quantiles":
                    results["quantiles"] = series.quantile([0.25, 0.5, 0.75]).to_dict()
                elif stat_lower == "skew":
                    results["skewness"] = float(series.skew())
                elif stat_lower == "kurt":
                    results["kurtosis"] = float(series.kurtosis())
            
            return {
                "success": True,
                "statistics": results,
                "data_length": len(series)
            }
            
        except Exception as e:
            return {"error": f"Failed to calculate statistics: {str(e)}"}
    
    def perform_calculation(self, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a specific calculation operation."""
        try:
            op_lower = operation.lower()
            
            if op_lower == "percentage_change":
                values = data.get("values", [])
                if len(values) < 2:
                    return {"error": "Need at least 2 values for percentage change"}
                
                pct_changes = []
                for i in range(1, len(values)):
                    if values[i-1] != 0:
                        pct_change = ((values[i] - values[i-1]) / values[i-1]) * 100
                        pct_changes.append(pct_change)
                    else:
                        pct_changes.append(float('inf'))
                
                return {
                    "operation": "percentage_change",
                    "result": pct_changes,
                    "formula": "((current - previous) / previous) * 100"
                }
            
            elif op_lower == "moving_average":
                values = data.get("values", [])
                window = data.get("window", 3)
                
                if len(values) < window:
                    return {"error": f"Need at least {window} values for moving average"}
                
                ma_values = []
                for i in range(window - 1, len(values)):
                    window_values = values[i - window + 1:i + 1]
                    ma_values.append(sum(window_values) / len(window_values))
                
                return {
                    "operation": "moving_average",
                    "window": window,
                    "result": ma_values
                }
            
            elif op_lower == "compound_growth":
                initial = data.get("initial", 0)
                final = data.get("final", 0)
                periods = data.get("periods", 1)
                
                if initial <= 0 or periods <= 0:
                    return {"error": "Initial value and periods must be positive"}
                
                growth_rate = (final / initial) ** (1 / periods) - 1
                
                return {
                    "operation": "compound_growth",
                    "initial": initial,
                    "final": final,
                    "periods": periods,
                    "growth_rate": growth_rate,
                    "growth_rate_percent": growth_rate * 100
                }
            
            else:
                return {"error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            return {"error": f"Failed to perform calculation: {str(e)}"}

# Global math computation instance
math_computation = MathComputation() 