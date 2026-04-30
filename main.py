import json
import sqlite3
import time
import streamlit as st
from google import genai
from pydantic import ValidationError
from schemas import DatabaseSchema

# --- 1. CLOUD CONFIGURATION ---
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

def verify_execution(sql_statements):
    """Spins up SQLite in-memory to test SQL execution"""
    try:
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        for statement in sql_statements:
            if statement.strip():
                cursor.execute(statement)
        conn.commit()
        conn.close()
        return True, "Execution successful."
    except Exception as e:
        return False, str(e)

def generate_database_with_repair(prompt: str, max_retries: int = 5):
    current_prompt = f"""
    You are a Senior Database Architect. 
    Based on the following request, generate a relational database schema.
    Return ONLY a raw JSON object that perfectly matches the DatabaseSchema format.
    Do not include any explanations or markdown formatting.
    
    Request: {prompt}
    """

    for attempt in range(max_retries):
        print(f"\n--- Starting AI Attempt {attempt + 1}/5 ---")
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=current_prompt,
            )
            
            raw_text = response.text
            cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()
            
            parsed_json = json.loads(cleaned_text)
            schema_obj = DatabaseSchema(**parsed_json)
            
            sql_statements = schema_obj.generate_sql() if hasattr(schema_obj, 'generate_sql') else []
            
            if sql_statements:
                is_valid, exec_msg = verify_execution(sql_statements)
                if not is_valid:
                    raise Exception(f"SQL Execution Failed: {exec_msg}")
                    
            print(f"✅ Attempt {attempt + 1} SUCCESS!")
            return schema_obj

        except json.JSONDecodeError as e:
            error_msg = f"JSON Parsing Error: {str(e)}"
            print(f"❌ Attempt {attempt + 1} Failed: {error_msg}")
            current_prompt += f"\n\nPrevious attempt failed with: {error_msg}\nPlease fix the JSON formatting."
        
        except ValidationError as e:
            error_msg = f"Pydantic Validation Error: {str(e)}"
            print(f"❌ Attempt {attempt + 1} Failed: {error_msg}")
            current_prompt += f"\n\nPrevious attempt failed with: {error_msg}\nPlease fix the schema."
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Attempt {attempt + 1} Failed: {error_msg}")
            if "429" in error_msg or "503" in error_msg:
                time.sleep(5)
            else:
                current_prompt += f"\n\nPrevious attempt failed with: {error_msg}\nPlease fix the database logic."
                
    return None