import os
import sqlite3
import time
from google import genai
from google.genai import types
from pydantic import ValidationError

# Import our strict rules from schemas.py
from schemas import DatabaseResponse

# --- SETUP GEMINI (NEW SDK) ---
os.environ["GEMINI_API_KEY"] = "AIzaSyBR8zvxWTAS3mFYvhisXMK-kbv7mRGiGVw"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# --- THE REPAIR ENGINE ---
def generate_database_with_repair(user_prompt: str, max_retries: int = 5) -> DatabaseResponse:
    system_prompt = """
    You are an expert Database Architect. 
    Design a relational database for the user's application.
    You MUST output valid JSON containing a single key called "tables" which holds an array of table objects.
    Make sure to include primary keys and foreign keys where appropriate.
    """
    
    error_history = ""
    
    for attempt in range(max_retries):
        print(f"\nAttempt {attempt + 1} to generate database... (Please wait ~5-10 seconds)")
        
        try:
            full_prompt = f"{system_prompt}\n\nUSER REQUEST: {user_prompt}\n{error_history}"
            
            # Using the new SDK syntax to force JSON output
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            
            raw_json = response.text
            validated_data = DatabaseResponse.model_validate_json(raw_json)
            
            print("✅ SUCCESS! The AI followed all Pydantic rules.")
            return validated_data
            
        except ValidationError as e:
            print(f"❌ AI broke the rules! Caught error. Sending back for repair...")
            error_history = f"\n\nYOUR LAST RESPONSE FAILED VALIDATION WITH THIS ERROR:\n{e.json()}\nFIX IT."
            
        except Exception as e:
            # Catch Server Errors (503/429) and Wait instead of crashing
            if "503" in str(e) or "429" in str(e):
                print("⚠️ Server is busy (High Demand). Waiting 5 seconds before retrying...")
                time.sleep(5)
            else:
                print(f"⚠️ Network error: {e}. Retrying in 2 seconds...")
                time.sleep(2)
            
    raise Exception("AI failed to generate a valid schema after all attempts.")

# --- EXECUTION AWARENESS TEST ---
def verify_execution(database_schema: DatabaseResponse):
    print("\n--- INITIATING EXECUTION AWARENESS TEST ---")
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    try:
        for table in database_schema.tables:
            columns_sql = []
            
            for col in table.columns:
                col_def = f"{col.name} {col.data_type}"
                if col.is_primary_key:
                    col_def += " PRIMARY KEY"
                columns_sql.append(col_def)
                
            for col in table.columns:
                if col.foreign_key_to and '.' in col.foreign_key_to:
                    ref_table, ref_col = col.foreign_key_to.split('.')
                    columns_sql.append(f"FOREIGN KEY ({col.name}) REFERENCES {ref_table}({ref_col})")
            
            create_table_sql = f"CREATE TABLE {table.table_name} ({', '.join(columns_sql)});"
            print(f"Running SQL: {create_table_sql}")
            
            cursor.execute(create_table_sql)
            
        print("\n🏆 EXECUTION PASSED: The database schema is structurally sound and executable!")
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ EXECUTION FAILED: The AI generated invalid SQL logic. Error: {e}")
        return False
    finally:
        conn.close()

# --- RUN THE TEST ---
if __name__ == "__main__":
    intent = "Build the Universal Sports League Manager to track cricket teams, players, and match scores."
    print(f"Processing Intent: '{intent}'")
    
    try:
        # 1. Generate the Database Schema
        final_database = generate_database_with_repair(intent)
        
        print("\n--- FINAL VALIDATED DATABASE SCHEMA ---")
        print(final_database.model_dump_json(indent=2))
        
        # 2. Test if it actually works in SQL
        verify_execution(final_database)
        
    except Exception as e:
        print(f"\nCRITICAL FAILURE: {str(e)}")