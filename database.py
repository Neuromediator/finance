from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
import re


class Database:
    """Database wrapper using SQLAlchemy Core for compatibility with cs50.SQL API"""
    
    def __init__(self, connection_string):
        """
        Initialize database connection.
        
        Args:
            connection_string: Database connection string (e.g., "sqlite:///finance.db")
        """
        self.engine = create_engine(connection_string, echo=False)
    
    def _convert_query(self, query, args):
        """
        Convert SQL query with ? placeholders to SQLAlchemy named parameters.
        
        Args:
            query: SQL query with ? placeholders
            args: Tuple of parameter values
            
        Returns:
            Tuple of (converted_query, params_dict)
        """
        if not args:
            return query, {}
        
        # Replace ? with :param1, :param2, etc.
        param_dict = {}
        param_index = 1
        
        def replace_placeholder(match):
            nonlocal param_index
            param_name = f"param{param_index}"
            param_index += 1
            return f":{param_name}"
        
        # Replace ? placeholders with named parameters
        converted_query = re.sub(r'\?', replace_placeholder, query)
        
        # Create parameter dictionary
        for i, arg in enumerate(args, start=1):
            param_dict[f"param{i}"] = arg
        
        return converted_query, param_dict
    
    def execute(self, query, *args):
        """
        Execute SQL query and return results.
        
        For SELECT queries: returns list of dictionaries
        For INSERT queries: returns lastrowid (primary key of inserted row)
        For UPDATE/DELETE queries: returns rowcount
        
        Args:
            query: SQL query string with ? placeholders
            *args: Query parameters
            
        Returns:
            For SELECT: list of dicts
            For INSERT: int (lastrowid)
            For UPDATE/DELETE: int (rowcount)
        """
        query_upper = query.strip().upper()
        
        with self.engine.connect() as conn:
            try:
                # Convert ? placeholders to named parameters for SQLAlchemy
                converted_query, params = self._convert_query(query, args)
                
                # Execute query with parameters
                result = conn.execute(text(converted_query), params)
                
                # Commit transaction
                conn.commit()
                
                # Handle different query types
                if query_upper.startswith('SELECT'):
                    # Convert rows to list of dictionaries
                    rows = result.fetchall()
                    return [dict(row._mapping) for row in rows]
                elif query_upper.startswith('INSERT'):
                    # Return lastrowid for INSERT
                    return result.lastrowid
                else:
                    # For UPDATE/DELETE, return rowcount
                    return result.rowcount
                    
            except IntegrityError as e:
                # Convert IntegrityError to ValueError for compatibility with cs50.SQL
                # This handles UNIQUE constraint violations
                raise ValueError(str(e)) from e
            except Exception as e:
                # Rollback on error
                conn.rollback()
                raise
