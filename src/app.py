"""
Interactive Resume Analysis Dashboard
=====================================

Compact and efficient Streamlit web application for exploring resume data.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from wordcloud import WordCloud
import re
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="Resume Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; font-weight: bold; color: #1f77b4; text-align: center; margin-bottom: 2rem;}
    .metric-card {background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; border-left: 0.25rem solid #1f77b4;}
    .sidebar-header {font-size: 1.5rem; font-weight: bold; color: #1f77b4; margin-bottom: 1rem;}
</style>
""", unsafe_allow_html=True)

class StreamlitResumeAnalyzer:
    """Compact Streamlit-based resume analyzer."""

    def __init__(self):
        self.skill_keywords = self._get_skill_keywords()
        self.df = None
        self.skill_df = None

    def _get_skill_keywords(self):
        """Get skill keywords as sets for efficiency."""
        return {
            'technical': {'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
                         'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'docker', 'kubernetes',
                         'aws', 'azure', 'gcp', 'linux', 'git', 'html', 'css', 'react', 'angular',
                         'vue', 'node.js', 'django', 'flask', 'spring', 'tensorflow', 'pytorch',
                         'machine learning', 'data science', 'api', 'rest', 'graphql'},
            'soft': {'communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking',
                    'time management', 'adaptability', 'creativity', 'empathy', 'collaboration',
                    'project management', 'agile', 'scrum', 'presentation', 'negotiation'},
            'business': {'marketing', 'sales', 'finance', 'accounting', 'strategy', 'analytics',
                        'business development', 'customer service', 'operations', 'supply chain',
                        'e-commerce', 'crm', 'erp', 'budgeting', 'forecasting'},
            'industry': {'healthcare', 'banking', 'retail', 'manufacturing', 'education', 'consulting',
                        'automotive', 'aviation', 'construction', 'energy', 'telecom', 'media'}
        }

    @st.cache_data
    def load_data(_self, sample_size=5000):
        """Load resume data with optional sampling."""
        try:
            df = pd.read_csv('Dataset/Resume/Resume.csv')
            if sample_size and len(df) > sample_size:
                df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)
            return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return None

    def preprocess_text(self, text):
        """Clean and preprocess resume text."""
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_skills(self, text):
        """Extract skills from resume text."""
        text = self.preprocess_text(text)
        found_skills = {'technical': [], 'soft': [], 'business': [], 'industry': []}

        for category, keywords in self.skill_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    found_skills[category].append(keyword)

        return found_skills

    @st.cache_data
    def analyze_skills(_self, df):
        """Analyze skills from resume data."""
        skill_data = []
        progress_bar = st.progress(0)
        total = len(df)

        for i, (_, row) in enumerate(df.iterrows()):
            text = row['Resume_str']
            skills = _self.extract_skills(text)
            for skill_type, skill_list in skills.items():
                for skill in skill_list:
                    skill_data.append({
                        'ID': row['ID'],
                        'Category': row['Category'],
                        'skill': skill,
                        'skill_type': skill_type
                    })
            progress_bar.progress((i + 1) / total)

        progress_bar.empty()
        return pd.DataFrame(skill_data)

    def create_overview_tab(self):
        """Create overview tab with dataset statistics."""
        st.markdown('<h2 class="main-header">📊 Dataset Overview</h2>', unsafe_allow_html=True)

        if self.df is None:
            st.warning("Please load data first using the sidebar.")
            return

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Resumes", len(self.df))
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Categories", self.df['Category'].nunique())
            st.markdown('</div>', unsafe_allow_html=True)

        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            avg_length = self.df['Resume_str'].str.len().mean()
            st.metric("Avg Resume Length", f"{avg_length:.0f} chars")
            st.markdown('</div>', unsafe_allow_html=True)

        # Category distribution
        st.subheader("Category Distribution")
        fig = px.pie(self.df, names='Category', title="Resume Categories")
        st.plotly_chart(fig, use_container_width=True)

    def create_skills_tab(self):
        """Create skills analysis tab."""
        st.markdown('<h2 class="main-header">🎯 Skills Analysis</h2>', unsafe_allow_html=True)

        if self.skill_df is None:
            st.warning("Please analyze skills first using the sidebar.")
            return

        col1, col2 = st.columns(2)

        with col1:
            # Top skills by type
            st.subheader("Top Skills by Type")
            skill_counts = self.skill_df.groupby(['skill_type', 'skill']).size().reset_index(name='count')
            for skill_type in skill_counts['skill_type'].unique():
                type_data = skill_counts[skill_counts['skill_type'] == skill_type].nlargest(10, 'count')
                fig = px.bar(type_data, x='skill', y='count', title=f"Top {skill_type.title()} Skills")
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Skills distribution
            st.subheader("Skills Distribution")
            type_counts = self.skill_df['skill_type'].value_counts()
            fig = px.pie(values=type_counts.values, names=type_counts.index, title="Skills by Type")
            st.plotly_chart(fig, use_container_width=True)

    def create_wordcloud_tab(self):
        """Create word cloud tab."""
        st.markdown('<h2 class="main-header">☁️ Skills Word Cloud</h2>', unsafe_allow_html=True)

        if self.skill_df is None:
            st.warning("Please analyze skills first using the sidebar.")
            return

        # Word cloud options
        col1, col2 = st.columns(2)

        with col1:
            skill_type = st.selectbox(
                "Select skill type for word cloud:",
                ["All"] + list(self.skill_df['skill_type'].unique()),
                key="wordcloud_type"
            )

        with col2:
            max_words = st.slider("Max words:", 50, 200, 100, key="max_words")

        # Generate word cloud
        if skill_type == "All":
            text = ' '.join(self.skill_df['skill'])
        else:
            filtered_df = self.skill_df[self.skill_df['skill_type'] == skill_type]
            text = ' '.join(filtered_df['skill'])

        wordcloud = WordCloud(width=800, height=400, max_words=max_words, background_color='white').generate(text)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

    def create_search_tab(self):
        """Create resume search and exploration tab."""
        st.markdown('<h2 class="main-header">🔍 Resume Explorer</h2>', unsafe_allow_html=True)

        if self.df is None or self.skill_df is None:
            st.warning("Please load data and analyze skills first.")
            return

        # Search options
        col1, col2, col3 = st.columns(3)

        with col1:
            search_category = st.selectbox("Filter by Category:", ["All"] + list(self.df['Category'].unique()), key="search_category")

        with col2:
            search_skill = st.text_input("Search by Skill:", key="search_skill")

        with col3:
            min_skills = st.slider("Min Skills Count:", 0, 20, 0, key="min_skills")

        # Filter data
        filtered_df = self.df.copy()

        if search_category != "All":
            filtered_df = filtered_df[filtered_df['Category'] == search_category]

        if search_skill:
            # Find resumes containing the skill
            resumes_with_skill = self.skill_df[self.skill_df['skill'].str.contains(search_skill, case=False, na=False)]['ID'].unique()
            filtered_df = filtered_df[filtered_df['ID'].isin(resumes_with_skill)]

        if min_skills > 0:
            skill_counts = self.skill_df.groupby('ID').size()
            filtered_df = filtered_df[filtered_df['ID'].isin(skill_counts[skill_counts >= min_skills].index)]

        st.write(f"Found {len(filtered_df)} matching resumes")

        # Display results
        if not filtered_df.empty:
            # Show sample resumes
            for idx, row in filtered_df.head(5).iterrows():
                with st.expander(f"Resume {row['ID']} - {row['Category']}"):
                    # Extract and display skills for this resume
                    skills = self.extract_skills(row['Resume_str'])
                    if any(skills.values()):
                        st.write("**Extracted Skills:**")
                        for skill_type, skill_list in skills.items():
                            if skill_list:
                                st.write(f"- **{skill_type.title()}:** {', '.join(skill_list)}")

                    # Show resume text (truncated)
                    resume_text = row['Resume_str'][:1000] + "..." if len(row['Resume_str']) > 1000 else row['Resume_str']
                    st.text_area("Resume Content:", resume_text, height=200, key=f"resume_{idx}")

    def run(self):
        """Run the Streamlit application."""
        if "df" not in st.session_state:
            st.session_state.df = None
        if "skill_df" not in st.session_state:
            st.session_state.skill_df = None

        self.df = st.session_state.df
        self.skill_df = st.session_state.skill_df

        st.sidebar.markdown('<h2 class="sidebar-header">Navigation</h2>', unsafe_allow_html=True)

        with st.sidebar:
            if st.button("Load Data", key="load_data"):
                with st.spinner("Loading resume data..."):
                    loaded_df = self.load_data()
                    if loaded_df is not None:
                        st.session_state.df = loaded_df
                        self.df = loaded_df
                        st.success(f"Loaded {len(self.df)} resumes")

            if st.button("Analyze Skills", key="analyze_skills") and self.df is not None:
                with st.spinner("Analyzing skills..."):
                    analyzed_df = self.analyze_skills(self.df)
                    if analyzed_df is not None:
                        st.session_state.skill_df = analyzed_df
                        self.skill_df = analyzed_df
                        st.success(f"Found {len(self.skill_df)} skill mentions")

            if self.df is not None:
                st.markdown(f"**Loaded:** {len(self.df)} resumes | **Categories:** {self.df['Category'].nunique()}")
            if self.skill_df is not None:
                st.markdown(f"**Analyzed:** {len(self.skill_df)} skills extracted")

        # Main content tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🎯 Skills", "☁️ Word Cloud", "🔍 Explorer"])

        with tab1:
            self.create_overview_tab()

        with tab2:
            self.create_skills_tab()

        with tab3:
            self.create_wordcloud_tab()

        with tab4:
            self.create_search_tab()


def main():
    """Main function."""
    analyzer = StreamlitResumeAnalyzer()
    analyzer.run()


if __name__ == "__main__":
    main()