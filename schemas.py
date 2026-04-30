from pydantic import BaseModel, Field
from typing import List, Optional

class Column(BaseModel):
    name: str = Field(..., description="The name of the column (e.g., id, team_name)")
    data_type: str = Field(..., description="The SQL data type (e.g., INTEGER, VARCHAR(255), DATE)")
    is_primary_key: bool = Field(default=False, description="True if this is the primary key")
    is_nullable: bool = Field(default=True, description="True if the column can be NULL")
    # This specific description helps the AI avoid the 'dictionary' error you saw
    foreign_key: Optional[str] = Field(
        default=None, 
        description="MUST be a string in format 'table(column)'. Example: 'teams(id)'. DO NOT USE OBJECTS."
    )

class Table(BaseModel):
    name: str = Field(..., description="The name of the table")
    columns: List[Column] = Field(..., description="List of columns in the table")

class DatabaseSchema(BaseModel):
    tables: List[Table] = Field(..., description="List of tables in the database")

    def generate_sql(self) -> List[str]:
        """
        Converts the validated Pydantic object into raw SQL CREATE TABLE statements.
        """
        sql_statements = []
        
        for table in self.tables:
            column_defs = []
            foreign_keys = []
            
            for col in table.columns:
                # Build base column string
                col_def = f"{col.name} {col.data_type}"
                if col.is_primary_key:
                    col_def += " PRIMARY KEY"
                elif not col.is_nullable:
                    col_def += " NOT NULL"
                    
                column_defs.append(col_def)
                
                # Build Foreign Key constraints
                if col.foreign_key:
                    # Clean up the string just in case the AI adds spaces
                    ref = col.foreign_key.strip()
                    foreign_keys.append(f"FOREIGN KEY ({col.name}) REFERENCES {ref}")
            
            # Combine everything into one CREATE TABLE block
            all_defs = column_defs + foreign_keys
            sql = f"CREATE TABLE {table.name} (\n    " + ",\n    ".join(all_defs) + "\n);"
            sql_statements.append(sql)
            
        return sql_statements