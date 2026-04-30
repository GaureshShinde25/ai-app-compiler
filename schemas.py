from pydantic import BaseModel, Field
from typing import List, Optional

class Column(BaseModel):
    name: str = Field(..., description="The name of the column (e.g., id, team_name)")
    data_type: str = Field(..., description="The SQL data type (e.g., INTEGER, VARCHAR(255), BOOLEAN, DATE)")
    is_primary_key: bool = Field(default=False, description="True if this column is the primary key")
    is_nullable: bool = Field(default=True, description="True if the column can be NULL")
    foreign_key: Optional[str] = Field(
        default=None, 
        description="If this is a foreign key, provide the reference in format: target_table(target_column)"
    )

class Table(BaseModel):
    name: str = Field(..., description="The name of the table")
    columns: List[Column] = Field(..., description="List of columns in the table")

class DatabaseSchema(BaseModel):
    tables: List[Table] = Field(..., description="List of tables in the database")

    def generate_sql(self) -> List[str]:
        """
        Translates the verified Pydantic object into raw SQL statements.
        This is what main.py uses in the SQLite execution engine!
        """
        sql_statements = []
        
        for table in self.tables:
            column_defs = []
            foreign_keys = []
            
            for col in table.columns:
                # Base column definition
                col_def = f"{col.name} {col.data_type}"
                
                # Constraints
                if col.is_primary_key:
                    col_def += " PRIMARY KEY"
                if not col.is_nullable and not col.is_primary_key:
                    col_def += " NOT NULL"
                    
                column_defs.append(col_def)
                
                # Foreign key collection
                if col.foreign_key:
                    foreign_keys.append(f"FOREIGN KEY ({col.name}) REFERENCES {col.foreign_key}")
            
            # Combine columns and foreign keys
            all_definitions = column_defs + foreign_keys
            
            # Build the final CREATE TABLE statement
            create_statement = f"CREATE TABLE {table.name} (\n    " + ",\n    ".join(all_definitions) + "\n);"
            sql_statements.append(create_statement)
            
        return sql_statements