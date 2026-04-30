import streamlit as st
from main import generate_database_with_repair

# Force clear session state on first run to ensure new API key is used
if 'first_run' not in st.session_state:
    st.session_state.first_run = True
    st.cache_data.clear()

st.set_page_config(page_title="AI App Compiler", page_icon="⚡")

# UI Header
st.title("⚡ AI App Compiler 🔗")
st.subheader("Universal Sports League Manager")
st.write("Automatically generate and validate relational database architectures using AI.")

# Debugging Sidebar - Use this to verify the app is fresh
with st.sidebar:
    st.header("System Tools")
    if st.button("Force Clear Cache"):
        st.cache_data.clear()
        st.success("Cache Cleared!")

prompt = st.text_area(
    "Describe the database you want to build:",
    value="Build a database to track the 2026 cricket season, including teams like the Mumbai Indians (sponsored by LOTUS), player rosters, match venues like the Arun Jaitley Stadium, and live scores.",
    height=100
)

if st.button("Generate Architecture"):
    # Visible X-Ray Log Container
    log_container = st.container()
    
    with st.spinner("Compiling database schema..."):
        try:
            # The Agentic Pipeline
            schema = generate_database_with_repair(prompt, max_retries=5, status_container=log_container)
            
            if schema is not None:
                st.success("✅ Database Schema Generated Successfully!")
                
                with st.expander("View Raw JSON Output"):
                    st.json(schema.model_dump())
                    
                st.subheader("Validated SQL Architecture")
                # Directly calling the SQL generator from our Pydantic object
                sql_list = schema.generate_sql() 
                for sql in sql_list:
                    st.code(sql, language="sql")
            else:
                st.error("CRITICAL FAILURE: AI failed to generate a valid schema after all 5 attempts.")
                st.info("Check the logs above to see if it was a code error or a Google API Quota issue.")
                
        except Exception as e:
            st.error(f"System Error: {str(e)}")