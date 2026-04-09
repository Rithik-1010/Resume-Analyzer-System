#!/usr/bin/env python3
"""
Resume Analysis Demo
====================

Quick demonstration of the resume analysis system with a small sample.
"""

import pandas as pd
import re
from collections import Counter

def preprocess_text(text):
    """Clean and preprocess resume text."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_skills(text):
    """Extract skills from resume text."""
    text = preprocess_text(text)
    skills = []

    # Define skill keywords
    skill_keywords = [
        'python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'angular',
        'aws', 'azure', 'docker', 'git', 'linux', 'communication', 'leadership',
        'marketing', 'sales', 'finance', 'project management', 'agile', 'scrum'
    ]

    for skill in skill_keywords:
        if skill in text:
            skills.append(skill)

    return skills

def main():
    """Run the demo analysis."""
    print("🚀 Resume Analysis Demo")
    print("=" * 40)

    try:
        # Load a small sample
        print("Loading resume data...")
        df = pd.read_csv('Dataset/Resume/Resume.csv', nrows=100)
        print(f"✅ Loaded {len(df)} resumes")

        # Show basic stats
        print(f"\n📊 Basic Statistics:")
        print(f"   Categories: {df['Category'].nunique()}")
        print(f"   Top categories: {df['Category'].value_counts().head(3).to_dict()}")

        # Extract skills from sample
        print("\n🔄 Extracting skills...")
        all_skills = []
        for idx, row in df.iterrows():
            skills = extract_skills(row['Resume_str'])
            all_skills.extend(skills)

        # Show skill analysis
        if all_skills:
            skill_counts = Counter(all_skills)
            print(f"✅ Found {len(set(all_skills))} unique skills")
            print(f"   Total skill mentions: {len(all_skills)}")

            print("\n🏆 Top 10 Skills:")
            for skill, count in skill_counts.most_common(10):
                print(f"   • {skill}: {count} mentions")
        else:
            print("⚠️  No skills found in sample")

        print("\n✅ Demo completed successfully!")
        print("\n💡 To run full analysis:")
        print("   python src/resume_analyzer.py")
        print("\n🌐 To launch dashboard:")
        print("   streamlit run src/app.py")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure Dataset/Resume/Resume.csv exists")
        print("   2. Install dependencies: pip install -r requirements.txt")
        print("   3. Try with smaller sample size")

if __name__ == "__main__":
    main()