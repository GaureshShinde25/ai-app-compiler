import json
import sqlite3
import time
import streamlit as st
from groq import Groq
from pydantic import ValidationError
from schemas import DatabaseSchema

# --- 1. CONFIGURATION ---
# Use GROQ_API_KEY from Streamlit Secrets
api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

def verify_execution(sql_statements):
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
    # We keep the prompt strict for JSON keys
    current_prompt = f"""
    You are a Senior Database Architect. 
    Return ONLY a raw JSON object that matches the DatabaseSchema format.
    
    CRITICAL RULES:
    - Root: "tables" list.
    - Columns: MUST use "data_type" (not "type").
    - Return ONLY valid JSON. No talk.
    
    Request: {prompt}
    """

    for attempt in range(max_retries):
        if status_container:
            status_container.info(f"⚡ Starting Groq Attempt {attempt + 1}/5...")
            
        try:
            # Groq's Chat Completion Syntax
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": current_prompt}],
                model="llama-3.3-70b-versatile", # High intelligence, high speed
                temperature=0.1 # Keep it precise
            )
            
            raw_text = chat_completion.choices[0].message.content
            cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()
            parsed_json = json.loads(cleaned_text)
            
            schema_obj = DatabaseSchema(**parsed_json)
            sql_statements = schema_obj.generate_sql()
            
            # Logic Verification
            is_valid, exec_msg = verify_execution(sql_statements)
            if not is_valid:
                raise Exception(f"SQL Logic Error: {exec_msg}")
                    
            if status_container:
                status_container.success(f"✅ Groq Success on Attempt {attempt + 1}!")
            return schema_obj

        except Exception as e:
            error_msg = str(e)
            if status_container: 
                status_container.error(f"❌ Attempt {attempt + 1} Failed: {error_msg}")
            # Add the error to the prompt for the next attempt (Self-Healing)
            current_prompt += f"\n\nFix this error in next response: {error_msg}"
            time.sleep(1) # Groq doesn't need long waits
                
    return None