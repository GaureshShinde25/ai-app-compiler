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
    with st.spinner("Compiling database schema... (This takes about 5-10 seconds)"):
        try:
            schema = generate_database_with_repair(prompt)
            
            # THE FIX: We explicitly check if the schema exists before declaring success!
            if schema is not None:
                st.success("✅ Database Schema Generated Successfully!")
                
                with st.expander("View Raw JSON Output"):
                    st.json(schema.model_dump())
                    
                st.subheader("Validated SQL Architecture")
                for sql in schema.generate_sql():
                    st.code(sql, language="sql")
            else:
                # If it's None, it means the 5-step repair loop failed.
                st.error("CRITICAL FAILURE: AI failed to generate a valid schema after all 5 attempts.")
                st.info("💡 Look at the Streamlit Cloud logs (Manage App in the bottom right) to see exactly which SQL or Pydantic rule Gemini is getting stuck on!")
                
        except Exception as e:
            st.error(f"System Error: {str(e)}")