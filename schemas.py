from pydantic import BaseModel, Field
from typing import List, Optional

# --- RULES FOR THE DATABASE ---
class ColumnConfig(BaseModel):
    name: str = Field(..., description="Name of the column (e.g., 'team_name', 'score')")
    data_type: str = Field(..., description="SQL data type (e.g., 'VARCHAR', 'INTEGER')")
    is_primary_key: bool = Field(default=False)
    foreign_key_to: Optional[str] = Field(default=None, description="Links to another table, e.g., 'teams.id'")

class TableConfig(BaseModel):
    table_name: str = Field(..., description="Plural name of the table (e.g., 'players')")
    columns: List[ColumnConfig]

# We need this wrapper so the AI knows to return an array of tables
class DatabaseResponse(BaseModel):
    tables: List[TableConfig]

# --- RULES FOR THE API & FINAL APP ---
class ApiEndpointConfig(BaseModel):
    method: str = Field(..., description="HTTP method: GET, POST, PUT, DELETE")
    route: str = Field(..., description="The endpoint path (e.g., '/api/teams')")
    interacts_with_tables: List[str] = Field(..., description="Tables this API touches")

class AppBlueprint(BaseModel):
    project_name: str = Field(..., description="Name of the app")
    database_schema: List[TableConfig]
    api_routes: List[ApiEndpointConfig]