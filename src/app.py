"""
Resume Analysis Dashboard
=========================
Blue-themed glassmorphism Streamlit app — mobile responsive.
Palette: #243A5E · #5F86A6 · #9FB6D8 · #CFE3F1 · #EDF4FA
"""

import streamlit as st
import pandas as pd
import re
import os
import warnings
warnings.filterwarnings('ignore')
from single_analyzer import SingleResumeAnalyzer

# ── Paths ──────────────────────────────────────────────────────────────────────
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_PATH = os.path.join(_BASE_DIR, 'Dataset', 'Resume', 'Resume.csv')

# ── Palette ────────────────────────────────────────────────────────────────────
C0 = "#243A5E"   # Midnight Blue – darkest bg
C1 = "#5F86A6"   # Dusty Denim – card / panel bg
C2 = "#9FB6D8"   # Calm Ocean – borders, dividers
C3 = "#CFE3F1"   # Powder Sky – muted text, axis labels
C4 = "#EDF4FA"   # Cloud Blue – primary text

# Chart accent colors (cool-toned to match blue palette)
CHART_COLORS = ["#5F86A6", "#9FB6D8", "#CFE3F1", "#EDF4FA", "#7EB8D4", "#4A7FA5", "#B8D4E8"]

# ── Plotly theme ───────────────────────────────────────────────────────────────
LAYOUT = dict(
    paper_bgcolor="rgba(36,58,94,0.72)",
    plot_bgcolor="rgba(36,58,94,0.0)",
    font=dict(family="DM Sans, sans-serif", color=C4, size=12),
    margin=dict(l=16, r=16, t=36, b=16),
    xaxis=dict(gridcolor="rgba(159,182,216,0.2)", linecolor=C2, tickcolor=C3, zerolinecolor="rgba(159,182,216,0.15)"),
    yaxis=dict(gridcolor="rgba(159,182,216,0.2)", linecolor=C2, tickcolor=C3, zerolinecolor="rgba(159,182,216,0.15)"),
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
    """Vectorized skill analysis – processes the entire column at once per keyword."""
    skill_keywords = dict(skill_keywords_items)

    # Pre-compile all patterns once
    compiled = {
        st_: {kw: re.compile(r'(?<![a-z0-9])' + re.escape(kw) + r'(?![a-z0-9])')
              for kw in kws}
        for st_, kws in skill_keywords.items()
    }

    # Vectorized: normalise all resume text once
    texts = df['Resume_str'].fillna('').str.lower().str.replace(r'\s+', ' ', regex=True)
    ids = df['ID'].values
    cats = df['Category'].values
    total_kw = sum(len(v) for v in skill_keywords.values())

    skill_data = []
    bar = st.progress(0, text="Analysing\u2026")
    done = 0
    for skill_type, keywords in skill_keywords.items():
        for kw, pat in compiled[skill_type].items():
            # Boolean mask over the entire column at once
            mask = texts.str.contains(pat, regex=True)
            for idx in mask[mask].index:
                skill_data.append({
                    'ID': ids[idx],
                    'Category': cats[idx],
                    'skill': kw,
                    'skill_type': skill_type,
                })
            done += 1
            if done % 5 == 0 or done == total_kw:
                bar.progress(done / total_kw, text=f"Analysing keyword {done}/{total_kw}\u2026")
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
@st.cache_data
def get_css():
    css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'style.css')
    with open(css_path) as f:
        return f.read()

st.markdown(f'<style>{get_css()}</style>', unsafe_allow_html=True)


# ── Helper: styled plotly chart ────────────────────────────────────────────────
def _chart(fig):
    fig.update_layout(**LAYOUT)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


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
            st.markdown('<div style="font-size:0.75rem;color:#9FB6D8;">Dataset exploration tool</div>', unsafe_allow_html=True)
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
        import plotly.express as px
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
        import plotly.graph_objects as go
        lengths = df['Resume_str'].str.len().dropna()
        fig2 = go.Figure(go.Histogram(
            x=lengths, nbinsx=40,
            marker_color="#9FB6D8",
            marker_line_color=C0,
            marker_line_width=0.8,
        ))
        fig2.update_layout(xaxis_title="Characters", yaxis_title="Count", **LAYOUT)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # ── Skills tab ──────────────────────────────────────────────────────────
    def _tab_skills(self):
        st.markdown('<div class="page-header">Skills analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-sub">Frequency of extracted skills across all resumes.</div>', unsafe_allow_html=True)

        skill_df = st.session_state.skill_df
        if skill_df is None:
            st.info("Run 'Analyse skills' from the sidebar first.")
            return

        import plotly.express as px
        import plotly.graph_objects as go

        # ── Row 1: Donut + Bar side by side ───────────────────────────────────
        col_donut, col_bar = st.columns([1, 2])

        with col_donut:
            _section("Skill type share")
            type_counts = skill_df['skill_type'].value_counts().reset_index()
            type_counts.columns = ['Type', 'Count']
            fig_donut = go.Figure(go.Pie(
                labels=type_counts['Type'],
                values=type_counts['Count'],
                hole=0.55,
                marker=dict(colors=CHART_COLORS[:len(type_counts)],
                            line=dict(color=C0, width=2)),
                textinfo='label+percent',
                textfont=dict(color=C4, size=11),
            ))
            fig_donut.update_layout(
                **LAYOUT,
                showlegend=False,
                annotations=[dict(text='Skills', x=0.5, y=0.5,
                                  font=dict(size=14, color=C3), showarrow=False)]
            )
            st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

        with col_bar:
            _section("Skill type breakdown")
            fig_bar = px.bar(type_counts, x='Type', y='Count', color='Type',
                             color_discrete_sequence=CHART_COLORS, text='Count')
            fig_bar.update_traces(textposition='outside', textfont_color=C3)
            fig_bar.update_layout(**LAYOUT, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

        # ── Row 2: Top skills per selected type ───────────────────────────────
        _section("Top skills by type")
        col_sel, col_n = st.columns([2, 1])
        with col_sel:
            skill_type_filter = st.selectbox(
                "Skill type", list(skill_df['skill_type'].unique()), key="skills_type_filter"
            )
        with col_n:
            top_n = st.slider("Show top N skills", 5, 30, 15, key="skills_topn")

        filtered = (
            skill_df[skill_df['skill_type'] == skill_type_filter]
            ['skill'].value_counts().head(top_n).reset_index()
        )
        filtered.columns = ['Skill', 'Count']
        fig2 = px.bar(filtered, x='Count', y='Skill', orientation='h',
                      color='Count', color_continuous_scale='Blues',
                      text='Count')
        fig2.update_traces(textposition='outside', textfont_color=C3)
        fig2.update_layout(**LAYOUT, showlegend=False, coloraxis_showscale=False)
        fig2.update_yaxes(categoryorder='total ascending')
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        # ── Row 3: Multi-category grouped bar – top 5 skills per type ─────────
        _section("Top 5 skills per type — side-by-side comparison")
        all_top = []
        for stype in skill_df['skill_type'].unique():
            top5 = (skill_df[skill_df['skill_type'] == stype]
                    ['skill'].value_counts().head(5).reset_index())
            top5.columns = ['Skill', 'Count']
            top5['Type'] = stype
            all_top.append(top5)
        all_top_df = pd.concat(all_top, ignore_index=True)
        fig3 = px.bar(all_top_df, x='Skill', y='Count', color='Type',
                      barmode='group', color_discrete_sequence=CHART_COLORS,
                      text='Count')
        fig3.update_traces(textposition='outside', textfont_color=C3)
        fig3.update_layout(**LAYOUT, xaxis_tickangle=-35)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

        # ── Row 4: Skill diversity per category (unique skills count) ─────────
        _section("Skill diversity by category (unique skills per resume category)")
        diversity = (skill_df.groupby('Category')['skill']
                     .nunique().reset_index(name='Unique Skills')
                     .sort_values('Unique Skills', ascending=False).head(15))
        fig4 = px.bar(diversity, x='Unique Skills', y='Category', orientation='h',
                      color='Unique Skills', color_continuous_scale='Blues', text='Unique Skills')
        fig4.update_traces(textposition='outside', textfont_color=C3)
        fig4.update_layout(**LAYOUT, showlegend=False, coloraxis_showscale=False)
        fig4.update_yaxes(categoryorder='total ascending')
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

        # ── Row 5: Heatmap: categories × skill types ──────────────────────────
        _section("Category × skill type heatmap")
        top_cats = skill_df['Category'].value_counts().head(12).index
        heat_data = skill_df[skill_df['Category'].isin(top_cats)]
        pivot = heat_data.groupby(['Category', 'skill_type']).size().reset_index(name='n')
        pivot_wide = pivot.pivot(index='Category', columns='skill_type', values='n').fillna(0)
        fig5 = go.Figure(go.Heatmap(
            z=pivot_wide.values,
            x=list(pivot_wide.columns),
            y=list(pivot_wide.index),
            colorscale='Blues',
            showscale=True,
            texttemplate='%{z:.0f}',
            textfont=dict(size=10, color=C0),
        ))
        fig5.update_layout(**LAYOUT)
        st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})

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

        from wordcloud import WordCloud
        import matplotlib.pyplot as plt

        corpus = skill_df if skill_type == "All" else skill_df[skill_df['skill_type'] == skill_type]
        text = ' '.join(corpus['skill'].tolist())

        wc = WordCloud(
            width=1200,
            height=480,
            max_words=max_words,
            background_color=C1,
            colormap='Blues',
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
                                st.markdown(
                                    f'<div style="font-size:0.72rem;font-weight:600;'
                                    f'letter-spacing:0.08em;text-transform:uppercase;'
                                    f'color:{C3};margin-bottom:0.3rem;">{stype}</div>'
                                    f'<div style="color:{C4};font-size:0.84rem;line-height:1.6;">'
                                    f'{", ".join(skills)}</div>',
                                    unsafe_allow_html=True
                                )
                st.markdown("<br>", unsafe_allow_html=True)
                preview = row['Resume_str']
                if len(preview) > 900:
                    preview = preview[:900] + "…"
                st.markdown(
                    f'<div style="background:rgba(36,58,94,0.75);border:1px solid {C2};'
                    f'border-radius:8px;padding:1rem;font-size:0.82rem;color:{C4};'
                    f'max-height:220px;overflow-y:auto;white-space:pre-wrap;'
                    f'font-family:monospace;line-height:1.6;">{preview}</div>',
                    unsafe_allow_html=True,
                )

    # ── Analyzer tab ─────────────────────────────────────────────────────────
    def _tab_analyzer(self):
        import plotly.graph_objects as go
        import plotly.express as px

        st.markdown('<div class="page-header">Resume Analyzer</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-sub">Upload your resume to get instant ATS scoring, skill matching, and actionable suggestions.</div>', unsafe_allow_html=True)

        uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=['pdf', 'docx'])

        if uploaded_file is not None:
            analyzer = SingleResumeAnalyzer(skill_keywords=self.SKILL_KEYWORDS)
            file_bytes = uploaded_file.read()

            with st.spinner("Analyzing resume..."):
                raw_text = analyzer.extract_text(file_bytes, uploaded_file.name)
                results = analyzer.analyze(raw_text)

            if not results:
                st.error("Could not analyze the file. Please ensure it is a valid PDF or DOCX.")
                return

            score = results['overall_score']
            word_count = results['word_count']
            skills_count = results['total_skills_count']
            action_verbs = results['action_verbs_found']
            sections = results['has_sections']

            # ── Metric cards row ────────────────────────────────────────────
            score_color = "#CFE3F1" if score >= 80 else "#9FB6D8" if score >= 60 else "#7EB8D4"
            col1, col2, col3, col4 = st.columns(4)
            glass = f'text-align:center;padding:1rem;border:1px solid rgba(159,182,216,0.3);border-radius:12px;background:rgba(95,134,166,0.18);backdrop-filter:blur(14px);'
            with col1:
                st.markdown(f'<div style="{glass}"><h3 style="color:{C4};margin:0;">Overall Score</h3><h1 style="color:{score_color};font-size:2.8rem;margin:0;">{score}/100</h1></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div style="{glass}"><h3 style="color:{C4};margin:0;">Word Count</h3><h1 style="color:#CFE3F1;font-size:2.8rem;margin:0;">{word_count}</h1></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div style="{glass}"><h3 style="color:{C4};margin:0;">Skills Found</h3><h1 style="color:#CFE3F1;font-size:2.8rem;margin:0;">{skills_count}</h1></div>', unsafe_allow_html=True)
            with col4:
                st.markdown(f'<div style="{glass}"><h3 style="color:{C4};margin:0;">Action Verbs</h3><h1 style="color:#CFE3F1;font-size:2.8rem;margin:0;">{len(action_verbs)}</h1></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Row: Gauge + Radar ───────────────────────────────────────────
            col_gauge, col_radar = st.columns([1, 1])

            with col_gauge:
                _section("ATS Compatibility Gauge")
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=score,
                    delta={'reference': 70, 'increasing': {'color': C3}, 'decreasing': {'color': '#7EB8D4'}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickcolor': C3, 'tickfont': {'color': C3}},
                        'bar': {'color': score_color},
                        'bgcolor': C1,
                        'borderwidth': 1,
                        'bordercolor': C2,
                        'steps': [
                            {'range': [0, 40],  'color': 'rgba(36,58,94,0.6)'},
                            {'range': [40, 70], 'color': 'rgba(95,134,166,0.35)'},
                            {'range': [70, 100],'color': 'rgba(159,182,216,0.25)'},
                        ],
                        'threshold': {'line': {'color': C4, 'width': 2}, 'thickness': 0.75, 'value': 70},
                    },
                    number={'font': {'color': C4, 'size': 36}, 'suffix': '/100'},
                    title={'text': 'ATS Score', 'font': {'color': C3, 'size': 14}},
                ))
                fig_gauge.update_layout(**LAYOUT, height=300)
                st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

            with col_radar:
                _section("Score Dimensions Radar")
                # Derive per-dimension scores for the radar
                wc_score   = 20 if 200 <= word_count <= 800 else 10
                sk_score   = 40 if skills_count >= 15 else (30 if skills_count >= 8 else 15)
                av_score   = 20 if len(action_verbs) >= 5 else (10 if len(action_verbs) >= 2 else 5)
                fmt_score  = (7 if sections['education'] else 0) + \
                             (7 if sections['experience'] else 0) + \
                             (6 if sections['skills'] else 0)
                categories = ['Word Count<br>(20)', 'Skills<br>(40)', 'Action Verbs<br>(20)', 'Formatting<br>(20)']
                values     = [wc_score, sk_score, av_score, fmt_score]
                max_vals   = [20, 40, 20, 20]
                pct_vals   = [v/m*100 for v, m in zip(values, max_vals)]
                fig_radar = go.Figure(go.Scatterpolar(
                    r=pct_vals + [pct_vals[0]],
                    theta=categories + [categories[0]],
                    fill='toself',
                    fillcolor='rgba(159,182,216,0.18)',
                    line=dict(color=C2, width=2),
                    marker=dict(color=C3, size=7),
                ))
                fig_radar.update_layout(
                    **LAYOUT,
                    height=300,
                    polar=dict(
                        bgcolor='rgba(36,58,94,0.4)',
                        radialaxis=dict(visible=True, range=[0, 100],
                                        tickfont=dict(color=C3, size=9),
                                        gridcolor=C2),
                        angularaxis=dict(tickfont=dict(color=C3, size=10),
                                         gridcolor=C2),
                    ),
                )
                st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

            # ── Section check status row ─────────────────────────────────────
            _section("Resume Section Status")
            sec_col1, sec_col2, sec_col3 = st.columns(3)
            def _sec_card(col, label, found):
                icon  = "✅" if found else "❌"
                clr   = "#9FB6D8" if found else "#7EB8D4"
                msg   = "Detected" if found else "Missing"
                col.markdown(
                    f'<div style="{glass}margin-top:0;">'
                    f'<div style="font-size:1.8rem">{icon}</div>'
                    f'<div style="color:{C4};font-weight:600;font-size:0.95rem;">{label}</div>'
                    f'<div style="color:{clr};font-size:0.8rem;">{msg}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            _sec_card(sec_col1, "Education Section",   sections['education'])
            _sec_card(sec_col2, "Experience Section",  sections['experience'])
            _sec_card(sec_col3, "Skills Section",      sections['skills'])

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Suggestions ──────────────────────────────────────────────────
            _section("Suggestions for Improvement")
            if not results['suggestions']:
                st.success("✨ Great job! Your resume looks well-structured and optimized.")
            else:
                for suggestion in results['suggestions']:
                    st.warning(f"💡 {suggestion}")

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Skill bar chart + Pie donut + skills list ────────────────────
            col_chart, col_pie, col_skills = st.columns([2, 1, 1])

            extracted = results['skills_extracted']
            skills_data = [{'Category': c, 'Count': len(s)} for c, s in extracted.items()]
            chart_df = pd.DataFrame(skills_data)

            with col_chart:
                _section("Skills by Category (Bar)")
                if chart_df['Count'].sum() > 0:
                    fig_bar = px.bar(chart_df, x='Category', y='Count', color='Category',
                                     color_discrete_sequence=CHART_COLORS, text='Count')
                    fig_bar.update_traces(textposition='outside', textfont_color=C3)
                    fig_bar.update_layout(**LAYOUT, showlegend=False)
                    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
                else:
                    st.info("No predefined skills detected. Add technical or soft skills.")

            with col_pie:
                _section("Skill Distribution")
                if chart_df['Count'].sum() > 0:
                    fig_pie = go.Figure(go.Pie(
                        labels=chart_df['Category'],
                        values=chart_df['Count'],
                        hole=0.5,
                        marker=dict(colors=CHART_COLORS[:4], line=dict(color=C0, width=2)),
                        textinfo='percent',
                        textfont=dict(color=C4, size=11),
                    ))
                    pie_layout = {**LAYOUT, 'showlegend': True,
                                       'legend': dict(bgcolor='rgba(0,0,0,0)',
                                                      font=dict(color=C4, size=10))}
                    fig_pie.update_layout(**pie_layout)
                    st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

            with col_skills:
                _section("Extracted Skills")
                st.markdown(f'<div style="background:rgba(95,134,166,0.18);backdrop-filter:blur(14px);border:1px solid rgba(159,182,216,0.3);border-radius:12px;padding:1rem;max-height:360px;overflow-y:auto;">', unsafe_allow_html=True)
                for cat, s_list in extracted.items():
                    if s_list:
                        st.markdown(f"<strong style='color:{C4};'>{cat}</strong>", unsafe_allow_html=True)
                        st.markdown(f"<span style='color:{C3};font-size:0.85rem;'>{', '.join(s_list)}</span>", unsafe_allow_html=True)
                        st.markdown("<hr style='margin:0.4rem 0;border-color:rgba(159,182,216,0.25);'>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # ── Action verbs panel ───────────────────────────────────────────
            if action_verbs:
                _section("Detected Action Verbs")
                badges = ' '.join(
                    f'<span style="display:inline-block;background:rgba(159,182,216,0.2);'
                    f'border:1px solid {C2};border-radius:20px;padding:0.2rem 0.7rem;'
                    f'margin:0.2rem;font-size:0.82rem;color:{C4};">✔ {v}</span>'
                    for v in sorted(action_verbs)
                )
                st.markdown(f'<div style="line-height:2.2;">{badges}</div>', unsafe_allow_html=True)


    # ── Run ────────────────────────────────────────────────────────────────────
    def run(self):
        self._sidebar()

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Skills", "Skill cloud", "Explorer", "Analyzer"])
        with tab1:
            self._tab_overview()
        with tab2:
            self._tab_skills()
        with tab3:
            self._tab_wordcloud()
        with tab4:
            self._tab_explorer()
        with tab5:
            self._tab_analyzer()


# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    ResumeApp().run()


if __name__ == "__main__":
    main()