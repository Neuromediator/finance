from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError


class Database:
    """Database wrapper using SQLAlchemy Core for compatibility with cs50.SQL API"""
    
    def __init__(self, connection_string):
        """
        Initialize database connection.
        
        Args:
            connection_string: Database connection string (e.g., "sqlite:///finance.db")
        """
        self.engine = create_engine(connection_string, echo=False)
    
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
                # Execute query with parameters
                # SQLAlchemy text() with ? placeholders requires parameters as tuple/list
                if args:
                    # Convert args tuple to list for SQLAlchemy
                    # SQLAlchemy expects parameters as a sequence for ? placeholders
                    result = conn.execute(text(query), list(args))
                else:
                    result = conn.execute(text(query))
                
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
