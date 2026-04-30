import streamlit as st
from main import generate_database_with_repair

st.set_page_config(page_title="AI App Compiler", page_icon="⚡")

st.title("⚡ AI App Compiler 🔗")
st.subheader("Universal Sports League Manager")
st.write("Automatically generate and validate relational database architectures using AI.")

prompt = st.text_area(
    "Describe the database you want to build:",
    value="Build a database to track the 2026 cricket season, including teams like the Mumbai Indians (sponsored by LOTUS), player rosters, match venues like the Arun Jaitley Stadium, and live scores.",
    height=100
)

if st.button("Generate Architecture"):
    # THE MAGIC BOX: This creates an empty space on the screen for our live X-Ray logs
    log_container = st.container()
    
    with st.spinner("Compiling database schema..."):
        try:
            # We pass the log_container to main.py so it can print its thoughts to the screen
            schema = generate_database_with_repair(prompt, max_retries=5, status_container=log_container)
            
            if schema is not None:
                st.success("✅ Database Schema Generated Successfully!")
                
                with st.expander("View Raw JSON Output"):
                    st.json(schema.model_dump())
                    
                st.subheader("Validated SQL Architecture")
                for sql in schema.generate_sql():
                    st.code(sql, language="sql")
            else:
                st.error("CRITICAL FAILURE: AI failed to generate a valid schema after all 5 attempts.")
                
        except Exception as e:
            st.error(f"System Error: {str(e)}")