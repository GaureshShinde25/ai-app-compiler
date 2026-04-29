import streamlit as st

# Import the engine and the tester we built in Phase 3 & 4
from main import generate_database_with_repair, verify_execution

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Universal Sports AI", page_icon="⚡", layout="centered")

st.title("⚡ AI App Compiler")
st.subheader("Universal Sports League Manager")
st.markdown("Automatically generate and validate relational database architectures using AI.")

# --- USER INPUT ---
# This text box lets you type the prompt on the webpage
user_intent = st.text_area(
    "Describe the database you want to build:",
    value="Build a database to track the 2026 cricket season, including teams like the Mumbai Indians (sponsored by LOTUS), player rosters, match venues like the Arun Jaitley Stadium, and live scores.",
    height=120
)

# --- EXECUTION BUTTON ---
if st.button("Generate Architecture", type="primary"):
    
    # Show a spinning loading wheel while the AI thinks
    with st.spinner("Compiling database schema... (This takes about 5-10 seconds)"):
        try:
            # 1. Trigger our main Python engine
            final_schema = generate_database_with_repair(user_intent)
            st.success("✅ Database Schema Generated Successfully!")
            
            # 2. Display the JSON beautifully on the screen
            with st.expander("View Raw JSON Output", expanded=True):
                st.json(final_schema.model_dump())
            
            # 3. Trigger the SQLite Execution Test
            is_valid = verify_execution(final_schema)
            
            # 4. Show the final trophy if it works
            if is_valid:
                st.balloons()
                st.success("🏆 EXECUTION PASSED: The schema is structurally sound and was successfully executed in a live SQLite database!")
            else:
                st.error("❌ EXECUTION FAILED: The AI generated invalid SQL logic.")
                
        except Exception as e:
            st.error(f"CRITICAL FAILURE: {str(e)}")