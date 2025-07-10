import duckdb
import pandas as pd
from typing import Dict, Any, List, Optional, Union
import os
from config import Config

class SQLQueryEngine:
    """Handles SQL queries using DuckDB for data operations."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or Config.DATABASE_URL.replace("sqlite:///", "")
        self.connection = None
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize the database connection and create tables if needed."""
        try:
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            self.connection = duckdb.connect(self.db_path)
            
            # Create sample tables for demonstration
            self.create_sample_tables()
            
        except Exception as e:
            print(f"Failed to initialize database: {e}")
    
    def create_sample_tables(self):
        """Create sample tables for demonstration purposes."""
        try:
            # Create stocks table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS stocks (
                    symbol VARCHAR,
                    date DATE,
                    open_price DOUBLE,
                    close_price DOUBLE,
                    high_price DOUBLE,
                    low_price DOUBLE,
                    volume BIGINT,
                    market_cap DOUBLE
                )
            """)
            
            # Create documents table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id VARCHAR PRIMARY KEY,
                    title VARCHAR,
                    content TEXT,
                    file_type VARCHAR,
                    upload_date TIMESTAMP,
                    file_size BIGINT,
                    metadata JSON
                )
            """)
            
            # Create users table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username VARCHAR UNIQUE,
                    email VARCHAR,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)
            
            # Insert sample stock data
            sample_stocks = [
                ('AAPL', '2024-01-01', 150.0, 155.0, 157.0, 149.0, 1000000, 2500000000.0),
                ('AAPL', '2024-01-02', 155.0, 160.0, 162.0, 154.0, 1200000, 2600000000.0),
                ('GOOGL', '2024-01-01', 2800.0, 2850.0, 2870.0, 2790.0, 500000, 1800000000.0),
                ('GOOGL', '2024-01-02', 2850.0, 2900.0, 2920.0, 2840.0, 600000, 1850000000.0),
                ('MSFT', '2024-01-01', 350.0, 355.0, 357.0, 349.0, 800000, 2600000000.0),
                ('MSFT', '2024-01-02', 355.0, 360.0, 362.0, 354.0, 900000, 2650000000.0),
            ]
            
            self.connection.execute("DELETE FROM stocks")  # Clear existing data
            self.connection.executemany("""
                INSERT INTO stocks (symbol, date, open_price, close_price, high_price, low_price, volume, market_cap)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_stocks)
            
        except Exception as e:
            print(f"Failed to create sample tables: {e}")
    
    def execute_query(self, query: str) -> Dict[str, Any]:
        """Execute a SQL query and return results."""
        try:
            if not self.connection:
                return {"error": "Database connection not established"}
            
            # Basic SQL injection prevention
            dangerous_keywords = [
                'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE'
            ]
            
            query_upper = query.upper()
            for keyword in dangerous_keywords:
                if keyword in query_upper and not query_upper.startswith('SELECT'):
                    return {"error": f"Operation '{keyword}' not allowed for security reasons"}
            
            # Execute query
            result = self.connection.execute(query)
            
            # Fetch results
            if result.description:
                columns = [desc[0] for desc in result.description]
                rows = result.fetchall()
                
                # Convert to list of dictionaries
                data = []
                for row in rows:
                    data.append(dict(zip(columns, row)))
                
                return {
                    "success": True,
                    "columns": columns,
                    "data": data,
                    "row_count": len(data)
                }
            else:
                return {
                    "success": True,
                    "message": "Query executed successfully",
                    "affected_rows": result.rowcount
                }
                
        except Exception as e:
            return {"error": f"Query execution failed: {str(e)}"}
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a specific table."""
        try:
            query = f"DESCRIBE {table_name}"
            result = self.execute_query(query)
            
            if result.get("success"):
                return {
                    "table_name": table_name,
                    "columns": result["data"]
                }
            else:
                return {"error": f"Failed to get table info: {result.get('error')}"}
                
        except Exception as e:
            return {"error": f"Failed to get table info: {str(e)}"}
    
    def list_tables(self) -> Dict[str, Any]:
        """List all tables in the database."""
        try:
            query = "SHOW TABLES"
            result = self.execute_query(query)
            
            if result.get("success"):
                tables = [row["name"] for row in result["data"]]
                return {
                    "success": True,
                    "tables": tables,
                    "count": len(tables)
                }
            else:
                return {"error": f"Failed to list tables: {result.get('error')}"}
                
        except Exception as e:
            return {"error": f"Failed to list tables: {str(e)}"}
    
    def get_table_preview(self, table_name: str, limit: int = 10) -> Dict[str, Any]:
        """Get a preview of table data."""
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            result = self.execute_query(query)
            
            if result.get("success"):
                return {
                    "table_name": table_name,
                    "preview": result["data"],
                    "total_rows": result["row_count"]
                }
            else:
                return {"error": f"Failed to get table preview: {result.get('error')}"}
                
        except Exception as e:
            return {"error": f"Failed to get table preview: {str(e)}"}
    
    def analyze_table(self, table_name: str) -> Dict[str, Any]:
        """Analyze a table and provide statistics."""
        try:
            # Get row count
            count_query = f"SELECT COUNT(*) as total_rows FROM {table_name}"
            count_result = self.execute_query(count_query)
            
            if not count_result.get("success"):
                return {"error": f"Failed to get row count: {count_result.get('error')}"}
            
            total_rows = count_result["data"][0]["total_rows"]
            
            # Get column information
            columns_query = f"DESCRIBE {table_name}"
            columns_result = self.execute_query(columns_query)
            
            if not columns_result.get("success"):
                return {"error": f"Failed to get column info: {columns_result.get('error')}"}
            
            # Get sample data
            sample_query = f"SELECT * FROM {table_name} LIMIT 5"
            sample_result = self.execute_query(sample_query)
            
            return {
                "table_name": table_name,
                "total_rows": total_rows,
                "columns": columns_result["data"],
                "sample_data": sample_result.get("data", [])
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze table: {str(e)}"}
    
    def insert_data(self, table_name: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Insert data into a table."""
        try:
            if not data:
                return {"error": "No data provided"}
            
            # Get column names from first row
            columns = list(data[0].keys())
            
            # Prepare values
            values = []
            for row in data:
                row_values = [row.get(col) for col in columns]
                values.append(row_values)
            
            # Build INSERT query
            columns_str = ", ".join(columns)
            placeholders = ", ".join(["?" for _ in columns])
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            # Execute insert
            self.connection.executemany(query, values)
            
            return {
                "success": True,
                "message": f"Inserted {len(data)} rows into {table_name}",
                "affected_rows": len(data)
            }
            
        except Exception as e:
            return {"error": f"Failed to insert data: {str(e)}"}
    
    def close_connection(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()

# Global SQL query engine instance
sql_engine = SQLQueryEngine() 