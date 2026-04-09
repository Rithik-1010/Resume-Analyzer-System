"""
Resume Dataset Analysis & Skill Demand Visualization System
===========================================================

Optimized and compact resume analysis system with efficient processing.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ResumeAnalyzer:
    """Optimized resume analyzer with efficient processing."""

    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None
        self.skill_df = None
        self.skill_keywords = self._get_skill_keywords()

    def _get_skill_keywords(self):
        """Get skill keywords organized by category."""
        return {
            'technical': {'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
                         'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
                         'html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask',
                         'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
                         'linux', 'windows', 'macos', 'tensorflow', 'pytorch', 'scikit-learn',
                         'pandas', 'numpy', 'matplotlib', 'tableau', 'power bi'},
            'soft': {'communication', 'leadership', 'teamwork', 'problem solving',
                    'critical thinking', 'time management', 'adaptability', 'creativity',
                    'emotional intelligence', 'conflict resolution', 'negotiation',
                    'project management', 'agile', 'scrum', 'kanban'},
            'business': {'marketing', 'sales', 'finance', 'accounting', 'strategy',
                        'business development', 'customer service', 'operations',
                        'supply chain', 'logistics', 'e-commerce', 'crm', 'erp'},
            'industry': {'healthcare', 'finance', 'retail', 'manufacturing', 'education',
                        'consulting', 'government', 'nonprofit', 'startup', 'enterprise'}
        }

    def load_data(self, sample_size=None):
        """Load resume data efficiently."""
        print("Loading resume data...")
        try:
            if sample_size:
                self.df = pd.read_csv(self.data_path, nrows=sample_size)
            else:
                self.df = pd.read_csv(self.data_path)
            print(f"Loaded {len(self.df)} resumes from {self.df['Category'].nunique()} categories")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    @staticmethod
    def preprocess_text(text):
        """Efficient text preprocessing."""
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r'[^a-z\s]', ' ', text)
        return re.sub(r'\s+', ' ', text).strip()

    def extract_skills_vectorized(self, texts):
        """Vectorized skill extraction for efficiency."""
        skill_data = []

        for idx, text in enumerate(texts):
            text_clean = self.preprocess_text(text)
            found_skills = {'technical': [], 'soft': [], 'business': [], 'industry': []}

            for category, keywords in self.skill_keywords.items():
                for keyword in keywords:
                    if keyword in text_clean:
                        found_skills[category].append(keyword)

            # Only add if skills found
            for skill_type, skills in found_skills.items():
                for skill in skills:
                    skill_data.append({
                        'resume_id': idx,
                        'category': self.df.iloc[idx]['Category'],
                        'skill': skill,
                        'skill_type': skill_type
                    })

        return pd.DataFrame(skill_data)

    def analyze_efficiently(self, sample_size=5000):
        """Efficient analysis pipeline."""
        if self.df is None:
            return None

        print("Analyzing skills efficiently...")

        # Sample data
        sample_df = self.df.sample(min(sample_size, len(self.df)), random_state=42)

        # Vectorized skill extraction
        self.skill_df = self.extract_skills_vectorized(sample_df['Resume_str'].values)

        return self.skill_df

    def create_visualizations(self):
        """Create all visualizations efficiently."""
        if self.skill_df is None or self.skill_df.empty:
            return

        # Create subplots for comprehensive view
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # 1. Top skills
        top_skills = self.skill_df['skill'].value_counts().head(15)
        top_skills.plot(kind='barh', ax=axes[0,0], color='skyblue')
        axes[0,0].set_title('Top 15 Skills')
        axes[0,0].set_xlabel('Frequency')

        # 2. Skill types distribution
        skill_types = self.skill_df['skill_type'].value_counts()
        skill_types.plot(kind='pie', ax=axes[0,1], autopct='%1.1f%%')
        axes[0,1].set_title('Skill Types Distribution')
        axes[0,1].set_ylabel('')

        # 3. Skills by category
        top_cats = self.skill_df['category'].value_counts().head(5).index
        cat_data = self.skill_df[self.skill_df['category'].isin(top_cats)]
        pivot = pd.crosstab(cat_data['category'], cat_data['skill_type'])
        pivot.plot(kind='bar', ax=axes[1,0], stacked=True)
        axes[1,0].set_title('Skills by Top Categories')
        axes[1,0].tick_params(axis='x', rotation=45)

        # 4. Category distribution
        cat_counts = self.df['Category'].value_counts().head(10)
        cat_counts.plot(kind='bar', ax=axes[1,1], color='lightgreen')
        axes[1,1].set_title('Resume Categories')
        axes[1,1].tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig('skill_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()

    def create_interactive_dashboard(self):
        """Create interactive dashboard."""
        if self.skill_df is None or self.df is None:
            return

        # Category distribution
        cat_counts = self.df['Category'].value_counts()

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Categories', 'Top Skills', 'Skill Types', 'Category-Skill Heatmap'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'pie'}, {'type': 'heatmap'}]]
        )

        # Categories
        fig.add_trace(go.Bar(x=cat_counts.index, y=cat_counts.values), row=1, col=1)

        # Top skills
        top_skills = self.skill_df['skill'].value_counts().head(10)
        fig.add_trace(go.Bar(x=top_skills.values, y=top_skills.index, orientation='h'), row=1, col=2)

        # Skill types
        skill_types = self.skill_df['skill_type'].value_counts()
        fig.add_trace(go.Pie(labels=skill_types.index, values=skill_types.values), row=2, col=1)

        # Heatmap
        heatmap_data = pd.crosstab(self.skill_df['category'], self.skill_df['skill_type'])
        fig.add_trace(go.Heatmap(z=heatmap_data.values, x=heatmap_data.columns,
                                y=heatmap_data.index, colorscale='Blues'), row=2, col=2)

        fig.update_layout(height=800, title="Resume Analysis Dashboard")
        fig.write_html("resume_dashboard.html")
        print("Interactive dashboard saved")

    def generate_report(self):
        """Generate concise analysis report."""
        if self.df is None:
            return

        print(f"""
{'='*50}
RESUME ANALYSIS REPORT
{'='*50}

Dataset: {len(self.df)} resumes, {self.df['Category'].nunique()} categories
Top Categories: {', '.join(self.df['Category'].value_counts().head(3).index.tolist())}

Skills Analysis ({len(self.skill_df) if self.skill_df is not None else 0} mentions):
- Unique Skills: {self.skill_df['skill'].nunique() if self.skill_df is not None else 0}
- Top Skill: {self.skill_df['skill'].value_counts().index[0] if self.skill_df is not None and not self.skill_df.empty else 'N/A'}
- Distribution: {self.skill_df['skill_type'].value_counts().to_dict() if self.skill_df is not None else {}}

Files Generated:
- skill_analysis.png: Static visualizations
- resume_dashboard.html: Interactive dashboard
{'='*50}
""")


def main():
    """Main execution function."""
    analyzer = ResumeAnalyzer("Dataset/Resume/Resume.csv")

    if analyzer.load_data():
        analyzer.analyze_efficiently()
        analyzer.create_visualizations()
        analyzer.create_interactive_dashboard()
        analyzer.generate_report()

        print("\n✅ Analysis complete!")


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()