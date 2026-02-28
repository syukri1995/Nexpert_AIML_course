import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io
import json
from thefuzz import process, fuzz
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(
    page_title="Yash Sharma's Class Resources",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Styling and Animations ---
st.markdown("""
<style>
    /* Card Styles */
    .resource-card {
        background-color: var(--secondary-background-color);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, opacity 0.6s ease-out, transform 0.6s ease-out;
        border: 1px solid rgba(128, 128, 128, 0.2);

        /* Initial state for fade-in animation */
        opacity: 0;
        transform: translateY(20px);
    }

    /* Class applied by JavaScript when element is in view */
    .resource-card.visible {
        opacity: 1;
        transform: translateY(0);
    }

    .resource-card:hover {
        transform: translateY(-5px); /* Slightly more lift on hover */
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
    }

    .resource-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: var(--text-color);
        margin-bottom: 0.5rem;
    }
    .resource-desc {
        color: var(--text-color);
        font-size: 0.95rem;
        margin-bottom: 1rem;
        opacity: 0.8;
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

# --- JavaScript for Scroll Animation ---
# Injected via components.html to run reliably in an iframe
animation_script = """
<script>
    console.log("Animation script initializing...");

    // Function to setup the observer
    const setupObserver = () => {
        // We need to access the parent document because this script runs in an iframe
        const parentDoc = window.parent.document;

        if (!parentDoc) {
            console.error("Cannot access parent document");
            return;
        }

        const cards = parentDoc.querySelectorAll('.resource-card');
        console.log(`Found ${cards.length} cards in parent document`);

        if (cards.length === 0) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target); // Only animate once
                }
            });
        }, {
            threshold: 0.1,
            root: null, // viewport
            rootMargin: '0px'
        });

        cards.forEach((card) => {
            if (!card.classList.contains('observed')) {
                observer.observe(card);
                card.classList.add('observed');
            }
        });
    };

    // Run initially
    setupObserver();

    // Re-run setup when Streamlit re-renders parts of the page
    const mutationObserver = new MutationObserver((mutations) => {
        setupObserver();
    });

    // Observe the parent body for changes
    if (window.parent.document.body) {
        mutationObserver.observe(window.parent.document.body, {
            childList: true,
            subtree: true
        });
    }
</script>
"""
components.html(animation_script, height=0, width=0)

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

    # Sorting Options
    sort_options = ["Relevance", "Topic (A-Z)", "Topic (Z-A)"]
    selected_sort = st.selectbox("Sort By:", sort_options, index=0)

    st.markdown("---")
    st.caption("Data extracted from course materials.")

# --- Filtering Logic ---
filtered_df = df[
    (df['Topic'].isin(selected_topics)) &
    (df['Resource Type'].isin(selected_types))
]

if search_query:
    # Use fuzzy matching for filtering
    # We'll create a new column combining text fields to search against
    filtered_df['SearchText'] = filtered_df['Topic'].fillna('') + " " + filtered_df['Description'].fillna('')

    # Extract matches with a score > 60
    # process.extract returns a list of tuples (match, score, index)
    # But filtering a dataframe is easier if we apply a function row-wise

    def get_fuzzy_score(row_text, query):
        return fuzz.partial_token_set_ratio(query.lower(), row_text.lower())

    # Calculate scores
    filtered_df['MatchScore'] = filtered_df['SearchText'].apply(lambda x: get_fuzzy_score(x, search_query))

    # Filter
    filtered_df = filtered_df[filtered_df['MatchScore'] >= 60]
else:
    # If no search, set a dummy MatchScore for sorting consistency
    filtered_df['MatchScore'] = 100

# Apply Sorting
if selected_sort == "Relevance":
    filtered_df = filtered_df.sort_values(by=['MatchScore', 'Topic'], ascending=[False, True])
elif selected_sort == "Topic (A-Z)":
    filtered_df = filtered_df.sort_values(by='Topic', ascending=True)
elif selected_sort == "Topic (Z-A)":
    filtered_df = filtered_df.sort_values(by='Topic', ascending=False)

# --- Main Interface with Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["📚 Browse Resources", "⭐ My Learning", "📊 Analytics", "➕ Suggest Resource"])

# --- TAB 1: Browse Resources ---
with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"Showing {len(filtered_df)} Resources")
    with col2:
        # Download Button
        # Check if 'MatchScore' or 'SearchText' exist and drop them before export
        export_df = filtered_df.copy()
        if 'Tag Class' in export_df.columns:
            export_df = export_df.drop(columns=['Tag Class'])
        if 'SearchText' in export_df.columns:
            export_df = export_df.drop(columns=['SearchText'])
        if 'MatchScore' in export_df.columns:
            export_df = export_df.drop(columns=['MatchScore'])

        csv = export_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name='yash_resources_filtered.csv',
            mime='text/csv',
        )

    if filtered_df.empty:
        st.info("No resources match your filters.")
    else:
        # Pagination
        import math
        items_per_page = 12
        total_items = len(filtered_df)
        total_pages = math.ceil(total_items / items_per_page)

        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1
        if st.session_state.current_page > total_pages:
            st.session_state.current_page = 1

        # Pagination controls
        if total_pages > 1:
            pc1, pc2, pc3 = st.columns([2, 1, 2])
            with pc2:
                page_options = list(range(1, total_pages + 1))
                st.session_state.current_page = st.selectbox("Page", page_options, index=st.session_state.current_page - 1, label_visibility="collapsed")

        start_idx = (st.session_state.current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page

        paginated_df = filtered_df.iloc[start_idx:end_idx]

        # Grid Layout for Cards
        cols = st.columns(3)  # 3 columns for desktop view
        for i, (idx, row) in enumerate(paginated_df.iterrows()):
            with cols[i % 3]:
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

                    # Embedded Video Preview
                    if "Video" in row['Resource Type']:
                        with st.expander("🎥 Preview Video"):
                            st.video(row['Link'])

# --- TAB 2: My Learning ---
with tab2:
    st.header("My Learning Progress")

    # Data Persistence: Export/Import
    with st.expander("💾 Manage Progress (Export/Import)"):
        c1, c2 = st.columns(2)
        with c1:
            # Export
            data_to_export = {
                "favorites": list(st.session_state.favorites),
                "completed": list(st.session_state.completed)
            }
            json_str = json.dumps(data_to_export)
            st.download_button(
                label="⬇️ Export Progress",
                data=json_str,
                file_name='yash_resources_progress.json',
                mime='application/json',
            )
        with c2:
            # Import
            uploaded_file = st.file_uploader("⬆️ Import Progress (JSON)", type=['json'])
            if uploaded_file is not None:
                try:
                    data = json.load(uploaded_file)
                    st.session_state.favorites = set(data.get("favorites", []))
                    st.session_state.completed = set(data.get("completed", []))
                    st.success("Progress restored successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error importing file: {e}")

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
        type_counts = df['Resource Type'].value_counts().reset_index()
        type_counts.columns = ['Resource Type', 'Count']
        fig_type = px.pie(type_counts, values='Count', names='Resource Type', hole=0.3)
        st.plotly_chart(fig_type, use_container_width=True)

    with col2:
        st.subheader("Resources by Topic")
        topic_counts = df['Topic'].value_counts().head(10).reset_index()
        topic_counts.columns = ['Topic', 'Count']
        fig_topic = px.bar(topic_counts, x='Count', y='Topic', orientation='h')
        fig_topic.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_topic, use_container_width=True)

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
        st.subheader("Manage Suggestions")
        st.info("In a real application, this would be restricted to admins. Here you can review and append suggestions to the dataset.")

        # Display suggestions as a dataframe
        sugg_df = pd.DataFrame(st.session_state.suggested_resources)
        st.dataframe(sugg_df)

        pending_suggestions = [s for s in st.session_state.suggested_resources if s['Status'] == 'Pending']

        if pending_suggestions:
            st.markdown("### Approve Suggestions")
            for idx, sugg in enumerate(pending_suggestions):
                with st.container():
                    col_info, col_action = st.columns([4, 1])
                    with col_info:
                        st.write(f"**{sugg['Topic']}**: {sugg['Description']} ([Link]({sugg['Link']}))")
                    with col_action:
                        if st.button("Approve & Add", key=f"approve_{idx}"):
                            # Add to CSV
                            new_row = pd.DataFrame([{
                                "Topic": sugg['Topic'],
                                "Description": sugg['Description'],
                                "Link": sugg['Link']
                            }])
                            try:
                                import os
                                # Append to CSV
                                new_row.to_csv("Yash_Resources.csv", mode='a', header=not os.path.exists("Yash_Resources.csv"), index=False)

                                # Update session state status
                                sugg['Status'] = 'Approved'
                                st.success(f"'{sugg['Topic']}' added to resources!")

                                # Clear cache to reload new data on next run
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error saving to CSV: {e}")

# --- Footer ---
st.markdown("---")
st.markdown("© 2024 Yash Sharma's Class Resources | Enhanced with Streamlit")
