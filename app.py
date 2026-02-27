import streamlit as st
import pandas as pd
import io

# --- Page Configuration ---
st.set_page_config(
    page_title="Yash Sharma's Class Resources",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Styling ---
st.markdown("""
<style>
    .resource-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .resource-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    .resource-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .resource-desc {
        color: #555;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }
    .tag {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
        color: white;
    }
    .tag-notebook { background-color: #f39c12; }
    .tag-video { background-color: #e74c3c; }
    .tag-dataset { background-color: #27ae60; }
    .tag-website { background-color: #3498db; }
    .tag-cloud { background-color: #9b59b6; }
    .tag-other { background-color: #7f8c8d; }

    .stButton>button {
        width: 100%;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def categorize_link(link):
    """Categorizes the resource based on the link URL."""
    if not isinstance(link, str):
        return "Other", "tag-other"

    link = link.lower()
    if "colab.research.google.com" in link:
        return "Notebook 📓", "tag-notebook"
    elif "youtube.com" in link or "youtu.be" in link:
        return "Video 🎥", "tag-video"
    elif "drive.google.com" in link or "sharepoint.com" in link:
        return "Cloud File ☁️", "tag-cloud"
    elif "kaggle.com" in link or "data.cityofchicago.org" in link or "raw.githubusercontent.com" in link or ".csv" in link or ".txt" in link or ".json" in link or ".xlsx" in link:
        return "Dataset 💾", "tag-dataset"
    elif "python.org" in link or "anaconda.com" in link or "realpython.com" in link or "w3resource.com" in link or "pynative.com" in link or "csiplearninghub.com" in link or "datacamp.com" in link or "analyticsvidhya.com" in link:
        return "Tool/Guide 🛠️", "tag-website"
    else:
        return "Website 🌐", "tag-website"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Yash_Resources.csv")
        # Add 'ID' column for unique identification if not present
        if 'ID' not in df.columns:
            df['ID'] = range(1, len(df) + 1)

        # Apply categorization
        df[['Resource Type', 'Tag Class']] = df['Link'].apply(lambda x: pd.Series(categorize_link(x)))
        return df
    except FileNotFoundError:
        return None

# --- Session State Initialization ---
if 'favorites' not in st.session_state:
    st.session_state.favorites = set()
if 'completed' not in st.session_state:
    st.session_state.completed = set()
if 'suggested_resources' not in st.session_state:
    st.session_state.suggested_resources = []

# --- Load Data ---
df = load_data()

if df is None:
    st.error("⚠️ File 'Yash_Resources.csv' not found! Please ensure it is in the same directory.")
    st.stop()

# --- Header ---
st.title("📚 Yash Sharma's AI/ML Class Resources")
st.markdown("Your one-stop hub for class materials, code notebooks, datasets, and tutorials.")

# --- Sidebar Filters ---
with st.sidebar:
    st.header("🔍 Filters & Options")

    # Text Search
    search_query = st.text_input("Search:", placeholder="Keywords (e.g. 'pandas', 'regression')...")

    # Topic Filter
    all_topics = sorted(df['Topic'].unique())
    selected_topics = st.multiselect("Filter by Topic:", all_topics, default=all_topics)

    # Resource Type Filter
    all_types = sorted(df['Resource Type'].unique())
    selected_types = st.multiselect("Filter by Type:", all_types, default=all_types)

    st.markdown("---")
    st.caption("Data extracted from course materials.")

# --- Filtering Logic ---
filtered_df = df[
    (df['Topic'].isin(selected_topics)) &
    (df['Resource Type'].isin(selected_types))
]

if search_query:
    filtered_df = filtered_df[
        filtered_df['Description'].str.contains(search_query, case=False, na=False) |
        filtered_df['Topic'].str.contains(search_query, case=False, na=False)
    ]

# --- Main Interface with Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["📚 Browse Resources", "⭐ My Learning", "📊 Analytics", "➕ Suggest Resource"])

# --- TAB 1: Browse Resources ---
with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"Showing {len(filtered_df)} Resources")
    with col2:
        # Download Button
        csv = filtered_df.drop(columns=['Tag Class']).to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name='yash_resources_filtered.csv',
            mime='text/csv',
        )

    if filtered_df.empty:
        st.info("No resources match your filters.")
    else:
        # Grid Layout for Cards
        cols = st.columns(3)  # 3 columns for desktop view
        for idx, row in filtered_df.iterrows():
            with cols[idx % 3]:
                # Card Container
                with st.container():
                    st.markdown(f"""
                    <div class="resource-card">
                        <div class="resource-title">{row['Topic']}</div>
                        <span class="tag {row['Tag Class']}">{row['Resource Type']}</span>
                        <p class="resource-desc">{row['Description']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Buttons
                    c1, c2, c3 = st.columns([1, 1, 1])
                    with c1:
                        st.link_button("🔗 Open", row['Link'])
                    with c2:
                        is_fav = row['ID'] in st.session_state.favorites
                        if st.button("⭐" if is_fav else "☆", key=f"fav_{row['ID']}", help="Toggle Favorite"):
                            if is_fav:
                                st.session_state.favorites.remove(row['ID'])
                            else:
                                st.session_state.favorites.add(row['ID'])
                            st.rerun()
                    with c3:
                        is_comp = row['ID'] in st.session_state.completed
                        if st.button("✅" if is_comp else "⬜", key=f"comp_{row['ID']}", help="Mark as Completed"):
                            if is_comp:
                                st.session_state.completed.remove(row['ID'])
                            else:
                                st.session_state.completed.add(row['ID'])
                            st.rerun()

# --- TAB 2: My Learning ---
with tab2:
    st.header("My Learning Progress")

    # Calculate Progress
    total_favorites = len(st.session_state.favorites)
    total_completed = len(st.session_state.completed)

    col1, col2, col3 = st.columns(3)
    col1.metric("Favorites", total_favorites)
    col2.metric("Completed", total_completed)

    if total_favorites > 0:
        completed_favorites = len(st.session_state.favorites.intersection(st.session_state.completed))
        progress = completed_favorites / total_favorites
        st.progress(progress)
        st.caption(f"You have completed {completed_favorites} out of {total_favorites} favorite items.")
    else:
        st.info("Add items to your favorites to track your progress!")

    st.subheader("⭐ Favorite Resources")
    if not st.session_state.favorites:
        st.info("You haven't added any favorites yet.")
    else:
        fav_df = df[df['ID'].isin(st.session_state.favorites)]
        st.dataframe(
            fav_df[['Topic', 'Description', 'Resource Type', 'Link']],
            column_config={
                "Link": st.column_config.LinkColumn("Link", display_text="Open")
            },
            hide_index=True,
            use_container_width=True
        )

# --- TAB 3: Analytics ---
with tab3:
    st.header("📊 Resource Analytics")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Resources by Type")
        type_counts = df['Resource Type'].value_counts()
        st.bar_chart(type_counts)

    with col2:
        st.subheader("Resources by Topic")
        topic_counts = df['Topic'].value_counts().head(10) # Top 10 topics
        st.bar_chart(topic_counts, horizontal=True)

# --- TAB 4: Suggest Resource ---
with tab4:
    st.header("➕ Suggest a New Resource")
    st.write("Found something useful? Suggest it to be added to the collection!")

    with st.form("suggestion_form"):
        new_topic = st.text_input("Topic")
        new_desc = st.text_input("Description")
        new_link = st.text_input("Link (URL)")

        submitted = st.form_submit_button("Submit Suggestion")

        if submitted:
            if new_topic and new_desc and new_link:
                suggestion = {
                    "Topic": new_topic,
                    "Description": new_desc,
                    "Link": new_link,
                    "Status": "Pending"
                }
                st.session_state.suggested_resources.append(suggestion)
                st.success("Thank you! Your suggestion has been recorded.")
            else:
                st.warning("Please fill in all fields.")

    if st.session_state.suggested_resources:
        st.subheader("Your Suggestions (Session Only)")
        st.dataframe(pd.DataFrame(st.session_state.suggested_resources))

# --- Footer ---
st.markdown("---")
st.markdown("© 2024 Yash Sharma's Class Resources | Enhanced with Streamlit")
