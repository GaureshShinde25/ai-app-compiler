from schemas import AppBlueprint
from pydantic import ValidationError

# This is fake data simulating a "lazy" AI response
# Notice it is missing the required "api_routes"
fake_ai_output = {
    "project_name": "Universal Sports",
    "database_schema": [
        {
            "table_name": "teams",
            "columns": [
                {"name": "id", "data_type": "INTEGER", "is_primary_key": True},
                {"name": "team_name", "data_type": "VARCHAR"}
            ]
        }
    ]
}

print("Testing the AI Output against our Contract...")

try:
    # We try to force the fake AI data into our strict Blueprint
    blueprint = AppBlueprint(**fake_ai_output)
    print("Success! The AI followed the rules.")
except ValidationError as e:
    print("\n--- ERROR CAUGHT! ---")
    print("The AI broke the contract. Here is exactly what it missed:")
    print(e)