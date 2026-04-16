"""
Resume Analysis Dashboard
=========================
Minimalistic dark-theme Streamlit app — mobile responsive.
Color palette: #2B2F36 · #404754 · #5D6675 · #8A919C · #CFD3D8
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import re
import os
import warnings
warnings.filterwarnings('ignore')

# ── Paths ──────────────────────────────────────────────────────────────────────
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_PATH = os.path.join(_BASE_DIR, 'Dataset', 'Resume', 'Resume.csv')

# ── Palette ────────────────────────────────────────────────────────────────────
C0 = "#2B2F36"   # darkest bg
C1 = "#404754"   # card / panel bg
C2 = "#5D6675"   # borders, dividers
C3 = "#8A919C"   # muted text, axis labels
C4 = "#CFD3D8"   # primary text

# Vibrant colors for charts
CHART_COLORS = ["#FF4B4B", "#00D280", "#00C4EB", "#FFB142", "#A66CFF", "#FF7CA8", "#F9F871"]

# ── Plotly theme ───────────────────────────────────────────────────────────────
LAYOUT = dict(
    paper_bgcolor=C1,
    plot_bgcolor=C1,
    font=dict(family="Inter, sans-serif", color=C4, size=12),
    margin=dict(l=16, r=16, t=36, b=16),
    xaxis=dict(gridcolor=C2, linecolor=C2, tickcolor=C3, zerolinecolor=C2),
    yaxis=dict(gridcolor=C2, linecolor=C2, tickcolor=C3, zerolinecolor=C2),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C4)),
    colorway=CHART_COLORS,
)


# ── Cached data functions ──────────────────────────────────────────────────────
@st.cache_data
def _cached_load_data(sample_size=5000):
    try:
        df = pd.read_csv(_DATA_PATH)
        if sample_size and len(df) > sample_size:
            df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"Could not load data: {e}")
        return None


@st.cache_data
def _cached_analyze_skills(df, skill_keywords_items):
    skill_keywords = dict(skill_keywords_items)
    skill_data = []
    total = len(df)
    bar = st.progress(0, text="Analysing…")
    for i, (_, row) in enumerate(df.iterrows()):
        text = row['Resume_str'] if isinstance(row['Resume_str'], str) else ""
        text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
        text = re.sub(r'\s+', ' ', text).strip()
        for skill_type, keywords in skill_keywords.items():
            for kw in keywords:
                if kw in text:
                    skill_data.append({
                        'ID': row['ID'],
                        'Category': row['Category'],
                        'skill': kw,
                        'skill_type': skill_type,
                    })
        bar.progress((i + 1) / total, text=f"Analysing resume {i+1}/{total}…")
    bar.empty()
    return pd.DataFrame(skill_data)


# ── Page config (must be first st call) ───────────────────────────────────────
st.set_page_config(
    page_title="Resume Analyser",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
def load_css():
    css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'style.css')
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()


# ── Helper: styled plotly chart ────────────────────────────────────────────────
def _chart(fig):
    fig.update_layout(**LAYOUT)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def _metric(label, value):
    return f"""
    <div class="metric-box">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
    </div>"""


def _section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


# ── Main app class ─────────────────────────────────────────────────────────────
class ResumeApp:

    SKILL_KEYWORDS = {
        'Technical': {'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
                      'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'docker', 'kubernetes',
                      'aws', 'azure', 'gcp', 'linux', 'git', 'html', 'css', 'react', 'angular',
                      'vue', 'node.js', 'django', 'flask', 'spring', 'tensorflow', 'pytorch',
                      'machine learning', 'data science', 'api', 'rest', 'graphql'},
        'Soft': {'communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking',
                 'time management', 'adaptability', 'creativity', 'empathy', 'collaboration',
                 'project management', 'agile', 'scrum', 'presentation', 'negotiation'},
        'Business': {'marketing', 'sales', 'finance', 'accounting', 'strategy', 'analytics',
                     'business development', 'customer service', 'operations', 'supply chain',
                     'e-commerce', 'crm', 'erp', 'budgeting', 'forecasting'},
        'Industry': {'healthcare', 'banking', 'retail', 'manufacturing', 'education', 'consulting',
                     'automotive', 'aviation', 'construction', 'energy', 'telecom', 'media'},
    }

    def __init__(self):
        if "df" not in st.session_state:
            st.session_state.df = None
        if "skill_df" not in st.session_state:
            st.session_state.skill_df = None

    # ── Sidebar ────────────────────────────────────────────────────────────────
    def _sidebar(self):
        with st.sidebar:
            st.markdown('<div class="sidebar-brand">Resume Analyser</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:0.75rem;color:#8A919C;">Dataset exploration tool</div>', unsafe_allow_html=True)
            st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

            if st.button("Load dataset", key="btn_load"):
                with st.spinner("Loading…"):
                    df = _cached_load_data()
                    if df is not None:
                        st.session_state.df = df
                        st.success(f"Loaded {len(df):,} resumes")

            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

            df = st.session_state.df
            btn_disabled = df is None
            if st.button("Analyse skills", key="btn_skills", disabled=btn_disabled):
                with st.spinner("Extracting skills…"):
                    kw_items = tuple(
                        (k, tuple(sorted(v))) for k, v in sorted(self.SKILL_KEYWORDS.items())
                    )
                    skill_df = _cached_analyze_skills(df, kw_items)
                    st.session_state.skill_df = skill_df
                    st.success(f"Found {len(skill_df):,} skill mentions")

            # Stats block
            st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
            df = st.session_state.df
            skill_df = st.session_state.skill_df
            if df is not None:
                st.markdown(
                    f'<div class="sidebar-stat">Resumes &nbsp;<span>{len(df):,}</span></div>'
                    f'<div class="sidebar-stat">Categories &nbsp;<span>{df["Category"].nunique()}</span></div>',
                    unsafe_allow_html=True,
                )
            if skill_df is not None:
                st.markdown(
                    f'<div class="sidebar-stat">Skill mentions &nbsp;<span>{len(skill_df):,}</span></div>',
                    unsafe_allow_html=True,
                )

    # ── Overview tab ──────────────────────────────────────────────────────────
    def _tab_overview(self):
        st.markdown('<div class="page-header">Dataset overview</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-sub">High-level summary of the loaded resume dataset.</div>', unsafe_allow_html=True)

        df = st.session_state.df
        if df is None:
            st.info("Load the dataset using the sidebar to get started.")
            return

        avg_len = int(df['Resume_str'].str.len().mean())
        top_cat = df['Category'].value_counts().index[0]

        st.markdown(
            '<div class="metric-row">'
            + _metric("Total resumes", f"{len(df):,}")
            + _metric("Categories", df['Category'].nunique())
            + _metric("Avg length", f"{avg_len:,}")
            + _metric("Top category", top_cat)
            + '</div>',
            unsafe_allow_html=True,
        )

        _section("Category distribution")
        cat_counts = df['Category'].value_counts().reset_index()
        cat_counts.columns = ['Category', 'Count']
        fig = px.bar(
            cat_counts, x='Count', y='Category', orientation='h',
            color='Category',
            color_discrete_sequence=CHART_COLORS,
        )
        fig.update_layout(**LAYOUT, showlegend=False)
        fig.update_yaxes(categoryorder='total ascending')
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        _section("Resume length distribution")
        lengths = df['Resume_str'].str.len().dropna()
        fig2 = go.Figure(go.Histogram(
            x=lengths, nbinsx=40,
            marker_color="#00C4EB",
            marker_line_color=C0,
            marker_line_width=0.8,
        ))
        fig2.update_layout(xaxis_title="Characters", yaxis_title="Count", **LAYOUT)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # ── Skills tab ────────────────────────────────────────────────────────────
    def _tab_skills(self):
        st.markdown('<div class="page-header">Skills analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-sub">Frequency of extracted skills across all resumes.</div>', unsafe_allow_html=True)

        skill_df = st.session_state.skill_df
        if skill_df is None:
            st.info("Run 'Analyse skills' from the sidebar first.")
            return

        # Skill type breakdown
        _section("Skill type breakdown")
        type_counts = skill_df['skill_type'].value_counts().reset_index()
        type_counts.columns = ['Type', 'Count']
        fig = px.bar(type_counts, x='Type', y='Count', color='Type', color_discrete_sequence=CHART_COLORS)
        fig.update_layout(**LAYOUT, showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # Top skills per type
        _section("Top skills by type")
        skill_type_filter = st.selectbox(
            "Skill type", list(skill_df['skill_type'].unique()), key="skills_type_filter",
            label_visibility="collapsed",
        )
        top_n = st.slider("Show top N skills", 5, 30, 15, key="skills_topn")

        filtered = (
            skill_df[skill_df['skill_type'] == skill_type_filter]
            ['skill'].value_counts()
            .head(top_n)
            .reset_index()
        )
        filtered.columns = ['Skill', 'Count']
        fig2 = px.bar(filtered, x='Count', y='Skill', orientation='h', color='Skill', color_discrete_sequence=CHART_COLORS)
        fig2.update_layout(**LAYOUT, showlegend=False)
        fig2.update_yaxes(categoryorder='total ascending')
        st.plotly_chart(fig2, width="stretch", config={"displayModeBar": False})

        # Heatmap: categories × skill types
        _section("Category × skill type heatmap")
        top_cats = skill_df['Category'].value_counts().head(12).index
        heat_data = skill_df[skill_df['Category'].isin(top_cats)]
        pivot = heat_data.groupby(['Category', 'skill_type']).size().reset_index(name='n')
        pivot_wide = pivot.pivot(index='Category', columns='skill_type', values='n').fillna(0)
        fig3 = go.Figure(go.Heatmap(
            z=pivot_wide.values,
            x=list(pivot_wide.columns),
            y=list(pivot_wide.index),
            colorscale='Turbo',
            showscale=True,
        ))
        fig3.update_layout(**LAYOUT)
        st.plotly_chart(fig3, width="stretch", config={"displayModeBar": False})

    # ── Word cloud tab ────────────────────────────────────────────────────────
    def _tab_wordcloud(self):
        st.markdown('<div class="page-header">Skill cloud</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-sub">Visual frequency map of extracted skill keywords.</div>', unsafe_allow_html=True)

        skill_df = st.session_state.skill_df
        if skill_df is None:
            st.info("Run 'Analyse skills' from the sidebar first.")
            return

        col1, col2 = st.columns([2, 1])
        with col1:
            skill_type = st.selectbox(
                "Skill type",
                ["All"] + list(skill_df['skill_type'].unique()),
                key="wc_type",
            )
        with col2:
            max_words = st.slider("Max words", 30, 200, 80, key="wc_maxwords")

        corpus = skill_df if skill_type == "All" else skill_df[skill_df['skill_type'] == skill_type]
        text = ' '.join(corpus['skill'].tolist())

        wc = WordCloud(
            width=1200,
            height=480,
            max_words=max_words,
            background_color=C1,
            colormap='cool',
            prefer_horizontal=0.85,
        ).generate(text)

        fig, ax = plt.subplots(figsize=(12, 4.8))
        fig.patch.set_facecolor(C1)
        ax.set_facecolor(C1)
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig, use_container_width=True) # retaining use_container_width for pyplot just in case, but let's change it. Actually, the warning might be for all of them. Let's just do `width="stretch"`... wait no. On streamlit doc `st.pyplot` still accepts `use_container_width`.
        plt.close(fig)

    # ── Explorer tab ──────────────────────────────────────────────────────────
    def _tab_explorer(self):
        st.markdown('<div class="page-header">Resume explorer</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-sub">Search and browse individual resume entries.</div>', unsafe_allow_html=True)

        df = st.session_state.df
        skill_df = st.session_state.skill_df
        if df is None:
            st.info("Load the dataset first.")
            return

        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            cat_filter = st.selectbox(
                "Category", ["All"] + sorted(df['Category'].unique().tolist()),
                key="exp_cat", label_visibility="visible",
            )
        with col2:
            skill_search = st.text_input("Skill keyword", placeholder="e.g. python", key="exp_skill")
        with col3:
            min_skills = st.number_input("Min skills", min_value=0, max_value=30, value=0, key="exp_min")

        filtered = df.copy()
        if cat_filter != "All":
            filtered = filtered[filtered['Category'] == cat_filter]
        if skill_search and skill_df is not None:
            ids = skill_df[skill_df['skill'].str.contains(skill_search.strip(), case=False, na=False)]['ID'].unique()
            filtered = filtered[filtered['ID'].isin(ids)]
        if min_skills > 0 and skill_df is not None:
            sc = skill_df.groupby('ID').size()
            filtered = filtered[filtered['ID'].isin(sc[sc >= min_skills].index)]

        st.markdown(f'<div class="result-count">{len(filtered):,} result(s)</div>', unsafe_allow_html=True)

        for _, row in filtered.head(8).iterrows():
            label = f"{row['Category']}  ·  ID {row['ID']}"
            with st.expander(label):
                if skill_df is not None:
                    resume_skills = skill_df[skill_df['ID'] == row['ID']]
                    if not resume_skills.empty:
                        by_type = resume_skills.groupby('skill_type')['skill'].apply(list).to_dict()
                        cols = st.columns(len(by_type))
                        for col, (stype, skills) in zip(cols, by_type.items()):
                            with col:
                                st.markdown(f'<div class="sidebar-stat">{stype}</div>', unsafe_allow_html=True)
                                st.caption(", ".join(skills))
                preview = row['Resume_str']
                if len(preview) > 900:
                    preview = preview[:900] + "…"
                st.markdown(
                    f'<div style="background:{C0};border:1px solid {C2};border-radius:4px;'
                    f'padding:0.9rem;font-size:0.8rem;color:{C3};'
                    f'max-height:220px;overflow-y:auto;white-space:pre-wrap;'
                    f'font-family:monospace;line-height:1.5">{preview}</div>',
                    unsafe_allow_html=True,
                )

    # ── Run ────────────────────────────────────────────────────────────────────
    def run(self):
        self._sidebar()

        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Skills", "Skill cloud", "Explorer"])
        with tab1:
            self._tab_overview()
        with tab2:
            self._tab_skills()
        with tab3:
            self._tab_wordcloud()
        with tab4:
            self._tab_explorer()


# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    ResumeApp().run()


if __name__ == "__main__":
    main()