import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Yash Sharma's Class Resources",
    page_icon="📚",
    layout="wide"
)

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Yash_Resources.csv")
        return df
    except FileNotFoundError:
        return None

df = load_data()

# 3. App Header
st.title("📚 Yash Sharma's AI/ML Class Resources")
st.markdown("Use the filters below to find specific Google Colab notebooks, datasets, and video tutorials shared in the class.")
st.divider()

# 4. Error Handling if CSV is missing
if df is None:
    st.error("⚠️ File 'Yash_Resources.csv' not found!")
    st.info("Please ensure you have saved the CSV file from the previous step in the same directory as this script.")
    st.stop()

# 5. Sidebar Filters
with st.sidebar:
    st.header("🔍 Filters")
    
    # Topic Filter
    all_topics = sorted(df['Topic'].unique())
    selected_topics = st.multiselect("Select Topics:", all_topics, default=all_topics)
    
    # Text Search
    search_query = st.text_input("Search Description:", "",placeholder="Type keywords to search in descriptions...")

# 6. Apply Filters
filtered_df = df[df['Topic'].isin(selected_topics)]

if search_query:
    filtered_df = filtered_df[filtered_df['Description'].str.contains(search_query, case=False, na=False)]

# 7. Display Metrics
col1, col2 = st.columns(2)
col1.metric("Total Resources", len(df))
col2.metric("Resources Shown", len(filtered_df))

# 8. Interactive Table
st.subheader("Resource List")

# This configures the 'Link' column to be clickable
st.data_editor(
    filtered_df,
    column_config={
        "Link": st.column_config.LinkColumn(
            "Resource Link",
            help="Click to open the resource",
            validate="^https://.*",
            display_text="Open Resource 🔗"
        ),
        "Topic": st.column_config.TextColumn("Topic", width="small"),
        "Description": st.column_config.TextColumn("Description", width="large"),
    },
    hide_index=True,
    use_container_width=True,
    disabled=True  # Disables editing the cells
)

# Footer
st.markdown("---")
st.caption("Data extracted from WhatsApp chat logs with Yash Sharma.")