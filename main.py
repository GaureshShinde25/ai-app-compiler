import json
import sqlite3
import time
import streamlit as st
from google import genai
from pydantic import ValidationError
from schemas import DatabaseSchema

# --- 1. CLOUD CONFIGURATION ---
# Explicitly grab the API key from Streamlit Secrets to avoid 400 errors
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

def verify_execution(sql_statements):
    """
    EXECUTION STEP: Spins up an isolated, in-memory SQLite database to test 
    if the generated SQL logic (tables, foreign keys) is mathematically sound.
    """
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

def generate_database_with_repair(prompt: str, max_retries: int = 5, status_container=None):
    """
    THE AGENTIC WORKFLOW: Generation -> Validation -> Execution -> Repair
    Now with Visible X-Ray Logging via status_container!
    """
    current_prompt = f"""
    You are a Senior Database Architect. 
    Based on the following request, generate a relational database schema.
    Return ONLY a raw JSON object that perfectly matches the DatabaseSchema format.
    Do not include any explanations or markdown formatting.
    
    Request: {prompt}
    """

    for attempt in range(max_retries):
        # Tell the UI we are starting a new attempt
        if status_container:
            status_container.info(f"🔄 Starting AI Attempt {attempt + 1}/5...")
            
        try:
            # --- STEP 1: GENERATION ---
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=current_prompt,
            )
            
            # Fix the Markdown Bug: Strip out the formatting backticks
            raw_text = response.text
            cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()
            
            # Parse JSON
            parsed_json = json.loads(cleaned_text)
            
            # --- STEP 2: VALIDATION ---
            # Enforce the strict Pydantic Contract
            schema_obj = DatabaseSchema(**parsed_json)
            
            # Extract SQL statements from your schema 
            sql_statements = schema_obj.generate_sql() if hasattr(schema_obj, 'generate_sql') else []
            
            # --- STEP 3: EXECUTION ---
            if sql_statements:
                is_valid, exec_msg = verify_execution(sql_statements)
                if not is_valid:
                    raise Exception(f"SQL Execution Failed: {exec_msg}")
                    
            # If it passes everything, tell the UI it succeeded!
            if status_container:
                status_container.success(f"✅ Attempt {attempt + 1} SUCCESS!")
            return schema_obj

        # --- STEP 4: REPAIR LOOP ---
        except json.JSONDecodeError as e:
            error_msg = f"JSON Parsing Error: {str(e)}"
            if status_container:
                status_container.error(f"❌ Attempt {attempt + 1} Failed: {error_msg}")
            current_prompt += f"\n\nPrevious attempt failed with: {error_msg}\nPlease fix the JSON formatting."
        
        except ValidationError as e:
            error_msg = f"Pydantic Validation Error: {str(e)}"
            if status_container:
                status_container.error(f"❌ Attempt {attempt + 1} Failed: {error_msg}")
            current_prompt += f"\n\nPrevious attempt failed with: {error_msg}\nPlease fix the schema to match the required format."
            
        except Exception as e:
            error_msg = str(e)
            if status_container:
                status_container.error(f"❌ Attempt {attempt + 1} Failed: {error_msg}")
                
            # Handle Network Reliability (API Rate Limits / Server Errors)
            if "429" in error_msg or "503" in error_msg:
                time.sleep(5)  # Wait 5 seconds and try again without changing the prompt
            else:
                # Handle SQL Execution failures
                current_prompt += f"\n\nPrevious attempt failed with: {error_msg}\nPlease fix the database logic."
                
    # If it fails 5 times, return None so app.py can trigger the Red Critical Failure box
    return None