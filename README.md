# 📄 Resume Analyzer System

> A powerful, interactive Streamlit dashboard for resume dataset exploration, real-time single-resume ATS scoring, skill extraction, and visual insights — built with a modern glassmorphism blue-themed UI.

---

## 📌 Table of Contents

1. [Overview](#-overview)
2. [Key Features](#-key-features)
3. [Tech Stack](#-tech-stack)
4. [Project Structure](#-project-structure)
5. [Installation & Setup](#-installation--setup)
6. [Running the Application](#-running-the-application)
7. [Dashboard Tabs](#-dashboard-tabs)
   - [Overview Tab](#1-overview-tab)
   - [Skills Tab](#2-skills-tab)
   - [Skill Cloud Tab](#3-skill-cloud-tab)
   - [Explorer Tab](#4-explorer-tab)
   - [Analyzer Tab](#5-analyzer-tab)
8. [Resume Scoring Algorithm](#-resume-scoring-algorithm)
9. [Skill Taxonomy](#-skill-taxonomy)
10. [Dataset Format](#-dataset-format)
11. [Color Palette & Design System](#-color-palette--design-system)
12. [Performance Optimizations](#-performance-optimizations)
13. [File-by-File Description](#-file-by-file-description)
14. [Troubleshooting](#-troubleshooting)
15. [Future Improvements](#-future-improvements)

---

## 🧠 Overview

The **Resume Analyzer System** is a full-featured, self-contained data analytics and machine learning tool built with Python and Streamlit. It offers two complementary modes:

1. **Dataset Mode** — Load a bulk CSV dataset of thousands of resumes, run skill extraction across the full corpus, and explore visual analytics including category distributions, skill heatmaps, and interactive word clouds.
2. **Single Resume Analyzer Mode** — Upload your own personal resume (PDF or DOCX), receive an instant ATS compatibility score out of 100, get a breakdown of detected skills across four taxonomies, view actionable improvement suggestions, and see a visual bar chart mapping your skills by category.

The entire application runs **100% offline** — no LLMs, no external APIs. All scoring and analysis uses deterministic rule-based heuristics and vectorized NLP pattern matching.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 📤 Resume Upload | Upload PDF or DOCX files for instant analysis |
| 🎯 ATS Score | Overall resume score out of 100 using 4 weighted metrics |
| 🔍 Skill Extraction | Auto-detect 80+ technical, soft, business, and industry skills |
| 💡 Suggestions | Clear, actionable improvement tips based on score deductions |
| 📊 Skill Visualization | Bar chart of skill distribution by taxonomy category |
| 🗂️ Dataset Explorer | Browse and filter thousands of resumes by category or keyword |
| 🌐 Word Cloud | Interactive visual frequency map of skills across the dataset |
| 🔥 Heatmap | Category × skill type correlation matrix |
| ⚡ Fast Analysis | Vectorized pandas skill extraction — ~10× faster than row-by-row |
| 🎨 Modern UI | Glassmorphism blue-themed design with DM Sans typography |

---

## 🛠 Tech Stack

| Library | Version | Purpose |
|---|---|---|
| `streamlit` | ≥ 1.28.0 | Web application framework |
| `pandas` | ≥ 2.0.0 | Data manipulation and vectorized text operations |
| `numpy` | ≥ 1.24.0 | Numerical computations |
| `plotly` | ≥ 5.0.0 | Interactive charts (bar, histogram, heatmap) |
| `matplotlib` | ≥ 3.6.0 | Static chart rendering (word cloud canvas) |
| `seaborn` | ≥ 0.12.0 | Statistical visualization helpers |
| `scikit-learn` | ≥ 1.3.0 | ML utilities |
| `nltk` | ≥ 3.8.0 | NLP support utilities |
| `wordcloud` | ≥ 1.9.0 | Skill cloud generation |
| `pdfplumber` | ≥ 0.10.0 | PDF text extraction |
| `docx2txt` | ≥ 0.8 | DOCX text extraction |
| `jupyter` | ≥ 1.0.0 | Notebook-based exploration |
| `ipykernel` | ≥ 6.25.0 | Jupyter kernel support |

---

## 📁 Project Structure

```
Resume-Analyzer-System/
│
├── src/
│   ├── app.py                  # Main Streamlit dashboard application
│   ├── single_analyzer.py      # Single-resume upload & scoring engine
│   ├── resume_analyzer.py      # Bulk dataset analysis module
│   ├── resume_analysis.ipynb   # Jupyter notebook for exploration
│   └── style.css               # Custom CSS — glassmorphism blue theme
│
├── Dataset/
│   ├── Resume/
│   │   └── Resume.csv          # Main resume dataset (CSV format)
│   └── data/                   # Additional data files
│
├── run.py                      # Interactive CLI runner menu
├── demo.py                     # Quick demo script (100-resume sample)
├── requirements.txt            # Python package dependencies
├── skill_analysis.png          # Static chart output (generated)
├── resume_dashboard.html       # Interactive HTML dashboard (generated)
└── README.md                   # This file
```

---

## ⚙️ Installation & Setup

### Prerequisites

- Python **3.9+** (3.11 recommended)
- `pip` package manager
- A working internet connection for the first-time Google Fonts load in the browser

### Step 1 — Clone or Download the Project

```bash
# If using git
git clone <your-repo-url>
cd Resume-Analyzer-System

# Or simply navigate to the project folder
cd "c:\Users\Admin\Desktop\Resume-Analyzer\Resume-Analyzer-System"
```

### Step 2 — (Recommended) Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install All Dependencies

```bash
pip install -r requirements.txt
```

This installs all 13 required packages. The two resume parsing libraries (`pdfplumber` and `docx2txt`) will also be installed automatically.

### Step 4 — Verify Dataset Location

Ensure the resume dataset CSV exists at the correct path:

```
Dataset/Resume/Resume.csv
```

The CSV must contain at minimum two columns:
- `ID` — Unique identifier per resume
- `Category` — Job/industry category label
- `Resume_str` — Full plain text of the resume

> ⚠️ **Common Issue:** If you see a nested `Dataset/Dataset/Resume/Resume.csv` structure, the files need to be moved up one level so the path resolves correctly. Run the following to fix it automatically:
> ```python
> python -c "
> import os, shutil
> src = 'Dataset/Dataset'
> dest = 'Dataset'
> for item in os.listdir(src):
>     shutil.move(os.path.join(src, item), dest)
> os.rmdir(src)
> "
> ```

---

## ▶️ Running the Application

### Option A — Streamlit Dashboard (Recommended)

```bash
# From inside the Resume-Analyzer-System directory
python -m streamlit run src/app.py
```

The app will open automatically at **http://localhost:8501** in your default browser.

### Option B — Interactive CLI Runner

```bash
python run.py
```

This presents a numbered menu:
```
1. Run core analysis (generates reports and visualizations)
2. Launch interactive web dashboard
3. Open Jupyter notebook for exploration
4. Install/update dependencies
5. Exit
```

### Option C — Quick Demo (No Dataset Required)

```bash
python demo.py
```

Runs a lightweight analysis on the first 100 rows of the dataset and prints skill frequency results to the console. Useful for verifying the setup is working without opening the full dashboard.

### Option D — Jupyter Notebook

```bash
python -m jupyter notebook src/resume_analysis.ipynb
```

Opens the full exploration notebook in your browser for step-by-step analysis.

---

## 🖥️ Dashboard Tabs

### 1. Overview Tab

**Purpose:** High-level statistics and distributions of the loaded resume dataset.

**How to use:**
1. Click **"Load dataset"** in the sidebar — this loads up to 5,000 resumes from `Resume.csv` into memory (cached after first load).
2. Four metric cards appear: Total Resumes, Category Count, Average Resume Length, Top Category.
3. An interactive horizontal bar chart shows the distribution of resumes across all job categories.
4. A histogram visualises the character-length distribution of resumes to understand verbosity patterns.

**Sidebar Stats:** After loading, the sidebar displays total resume count and category count.

---

### 2. Skills Tab

**Purpose:** Analyse the frequency and spread of skills across all loaded resumes.

**How to use:**
1. First load the dataset (Overview tab), then click **"Analyse skills"** in the sidebar.
2. The analysis uses vectorized pandas `str.contains` matching — it processes all 5,000 resumes per keyword simultaneously rather than row-by-row.
3. A progress bar tracks analysis by keyword (approximately 80 keywords total).

**Charts displayed:**
- **Skill type share:** A donut chart showing the percentage breakdown of skill types.
- **Skill type breakdown:** Bar chart showing total mentions by type (Technical, Soft, Business, Industry).
- **Top skills by type:** Select a skill type from the dropdown, adjust the top-N slider (5–30), and see the most frequently occurring skills ranked horizontally.
- **Top 5 skills per type:** A grouped bar chart offering a side-by-side comparison across all taxonomies.
- **Skill diversity by category:** A horizontal bar chart ranking job categories by the number of unique skills they demand.
- **Category × Skill type heatmap:** A Blues-colorscale heatmap with numeric annotations showing how skill types correlate with job categories across the top 12 categories.

---

### 3. Skill Cloud Tab

**Purpose:** A visually engaging word cloud rendering of skill keyword frequencies.

**Controls:**
- **Skill type selector:** Filter the cloud to a specific taxonomy (All / Technical / Soft / Business / Industry).
- **Max words slider:** Control the density of the cloud (30–200 words).

The word cloud uses the **Blues** Matplotlib colormap on the dark navy background to maintain visual harmony with the app theme.

---

### 4. Explorer Tab

**Purpose:** Search and browse individual resume records from the dataset.

**Filters available:**
| Filter | Description |
|---|---|
| Category dropdown | Filter by job category (e.g., "Data Science", "HR") |
| Skill keyword search | Free-text search across extracted skill names |
| Min skills count | Show only resumes with at least N detected skills |

A result count badge updates dynamically. Up to **8 resumes** are shown at a time, each expandable to see:
- Detected skills grouped by type (Technical, Soft, Business, Industry) in columns
- A scrollable monospace preview of raw resume text (first 900 characters)

---

### 5. Analyzer Tab

**Purpose:** Upload and score your own personal resume in real time.

**Workflow:**
1. Click "Browse files" and select a `.pdf` or `.docx` resume.
2. The system extracts the raw text using `pdfplumber` (PDF) or `docx2txt` (DOCX).
3. Analysis runs immediately — no loading buttons needed.
4. Results appear in three sections:

**Score Cards (4 columns):**
- **Overall Score / 100** — color-coded: bright blue ≥80, medium blue 60–79, light blue <60
- **Word Count** — raw word count of extracted text
- **Skills Found** — total number of matched skill keywords
- **Action Verbs** — total number of strong impact verbs detected

**Graphical Scoring:**
- **ATS Compatibility Gauge:** A visual dial showing your score against a target threshold of 70.
- **Score Dimensions Radar:** A spider chart breaking down your performance across the 4 scoring metrics.

**Section Status:**
- Visual ✅/❌ cards verifying the detection of Education, Experience, and Skills sections.

**Suggestions Panel:**
- Actionable, real-time improvement tips based on specific score deductions.

**Visual Insights & Data:**
- **Skills by Category (Bar):** Plotly bar chart showing skill counts per taxonomy.
- **Skill Distribution (Donut):** Pie chart showing the percentage split of your skills.
- **Extracted Skills:** Scrollable panel listing all detected skills grouped by category.
- **Detected Action Verbs:** A pill-badge layout of all identified impact words.

---

## 🎯 Resume Scoring Algorithm

The score is computed out of **100 points** across four independent dimensions:

### 1. Word Count Score (Max 20 pts)

| Condition | Points | Reason |
|---|---|---|
| 200–800 words | **20** | Ideal ATS-friendly length |
| < 200 words | **10** | Too brief; lacks detail |
| > 800 words | **10** | Too long; dilutes impact |

### 2. Skills Score (Max 40 pts)

| Skills Detected | Points | Feedback |
|---|---|---|
| ≥ 15 skills | **40** | Excellent keyword density |
| 8–14 skills | **30** | Good, but room to add more |
| < 8 skills | **15** | Too few; likely to fail ATS filters |

### 3. Action Verbs Score (Max 20 pts)

| Verbs Detected | Points | Feedback |
|---|---|---|
| ≥ 5 action verbs | **20** | Strong impact language |
| 2–4 action verbs | **10** | Moderate; improve wording |
| 0–1 action verbs | **5** | Weak; needs improvement |

Recognised action verbs include: `achieved`, `improved`, `trained`, `managed`, `developed`, `led`, `designed`, `built`, `implemented`, `optimized`, `spearheaded`, `orchestrated`, and more.

### 4. Formatting / Structure Score (Max 20 pts)

| Section | Points | Detection Pattern |
|---|---|---|
| Education section | **7** | Matches: `education`, `university`, `bachelor`, `master`, `phd`, `degree`, `college` |
| Experience section | **7** | Matches: `experience`, `work history`, `employment`, `career` |
| Skills section | **6** | Matches: `skills`, `technologies`, `tools` |

> All pattern matching uses **word-boundary regex lookarounds** (`(?<![a-z0-9])keyword(?![a-z0-9])`) to ensure precise matching and avoid false positives (e.g., `"go"` would not match `"good"`).

---

## 🏷️ Skill Taxonomy

The system recognises **80+ keywords** across four categories:

### Technical Skills
`python`, `java`, `javascript`, `c++`, `c#`, `php`, `ruby`, `go`, `rust`, `sql`, `mysql`, `postgresql`, `mongodb`, `redis`, `docker`, `kubernetes`, `aws`, `azure`, `gcp`, `linux`, `git`, `html`, `css`, `react`, `angular`, `vue`, `node.js`, `django`, `flask`, `spring`, `tensorflow`, `pytorch`, `machine learning`, `data science`, `api`, `rest`, `graphql`

### Soft Skills
`communication`, `leadership`, `teamwork`, `problem solving`, `critical thinking`, `time management`, `adaptability`, `creativity`, `empathy`, `collaboration`, `project management`, `agile`, `scrum`, `presentation`, `negotiation`

### Business Skills
`marketing`, `sales`, `finance`, `accounting`, `strategy`, `analytics`, `business development`, `customer service`, `operations`, `supply chain`, `e-commerce`, `crm`, `erp`, `budgeting`, `forecasting`

### Industry Keywords
`healthcare`, `banking`, `retail`, `manufacturing`, `education`, `consulting`, `automotive`, `aviation`, `construction`, `energy`, `telecom`, `media`

---

## 📦 Dataset Format

The application expects a CSV file at `Dataset/Resume/Resume.csv` with these columns:

| Column | Type | Description |
|---|---|---|
| `ID` | int | Unique numeric identifier for each resume |
| `Category` | str | Job category label (e.g., `"Data Science"`, `"HR"`) |
| `Resume_str` | str | Full plain text content of the resume |

The dataset is Kaggle's **Resume Dataset** — a widely used NLP benchmark containing 2,400+ labelled resumes across 24 professional categories.

By default the app samples up to **5,000 rows** on load (configurable via `_cached_load_data(sample_size=5000)`). Results are cached for the session so re-loading is instant.

---

## 🎨 Color Palette & Design System

The application uses a **Midnight Blue glassmorphism** design system.

| Token | Hex | CSS Variable | Usage |
|---|---|---|---|
| Midnight Blue | `#243A5E` | `--c0` | Primary background, deepest layer |
| Dusty Denim | `#5F86A6` | `--c1` | Card & panel backgrounds |
| Calm Ocean | `#9FB6D8` | `--c2` | Borders, dividers, accent outlines |
| Powder Sky | `#CFE3F1` | `--c3` | Muted labels, axis text, sub-headings |
| Cloud Blue | `#EDF4FA` | `--c4` | Primary text, headings, values |

**Glassmorphism tokens:**
```css
--glass-bg:     rgba(95, 134, 166, 0.18)
--glass-border: rgba(207, 227, 241, 0.22)
--glass-blur:   blur(14px)
--glass-shadow: 0 4px 28px rgba(36, 58, 94, 0.35)
```

**Font:** [DM Sans](https://fonts.google.com/specimen/DM+Sans) — weights 300, 400, 500, 600

Glassmorphism is applied strategically (not globally) to: sidebar, metric cards, expander panels, score cards, inputs, and the file uploader — preserving usability and readability.

---

## ⚡ Performance Optimizations

### Vectorized Skill Extraction
The original implementation used Python `iterrows()` — looping over 5,000 resumes × 80 keywords = **400,000 individual regex calls**.

The optimised approach inverts the loop:
```python
# For each keyword → apply across ALL rows at once using pandas vectorized str.contains
mask = texts.str.contains(pattern, regex=True)  # C-level execution, ~10× faster
```

This runs **~80 vectorized pandas calls** instead of 400,000 Python-level iterations.

### Caching Strategy
```python
@st.cache_data   # Dataset load — cached by function arguments
@st.cache_data   # Skill extraction — cached by (df_hash, keyword_tuple)
@st.cache_data   # CSS loading — cached permanently per session
```

- The dataset is only read from disk once per session.
- Skill extraction results are memoized — clicking "Analyse skills" twice does not reprocess.
- CSS is cached to avoid repeated file I/O on every Streamlit rerender.

### Progress Bar Throttling
The progress bar during skill analysis updates only every **5 keywords** (instead of every row), dramatically reducing Streamlit UI overhead during the analysis loop.

---

## 📖 File-by-File Description

### `src/app.py`
The main Streamlit application. Contains:
- Global palette constants (`C0`–`C4`) and Plotly theme layout (`LAYOUT`)
- Cached data-loading and skill-extraction functions
- `ResumeApp` class with 5 tab methods: `_tab_overview`, `_tab_skills`, `_tab_wordcloud`, `_tab_explorer`, `_tab_analyzer`
- The `SKILL_KEYWORDS` dictionary shared between dataset analysis and single-resume analysis

### `src/single_analyzer.py`
The single-resume analysis engine. Contains the `SingleResumeAnalyzer` class:
- `extract_text(file_bytes, file_name)` — dispatches to `pdfplumber` or `docx2txt` based on extension
- `analyze(raw_text)` — runs the full 4-metric scoring algorithm and returns a results dict
- Pre-compiles all regex patterns at `__init__` time for maximum per-call speed

### `src/resume_analyzer.py`
The standalone bulk analysis module used by `run.py` option 1. Contains the `ResumeAnalyzer` class with methods to load data, extract skills, generate static matplotlib charts (`skill_analysis.png`), and write an interactive HTML dashboard (`resume_dashboard.html`).

### `src/style.css`
All custom CSS for the application. Defines:
- CSS custom properties (variables) for the full colour palette and glassmorphism tokens
- Background gradient for `.stApp`
- Glassmorphism styles on sidebar, metric cards, expanders, inputs, file uploader
- Responsive breakpoints for mobile at `max-width: 768px`

### `src/resume_analysis.ipynb`
Jupyter notebook providing an interactive, step-by-step walkthrough of the resume dataset analysis pipeline — suitable for exploration, experimentation, and extending the analysis.

### `run.py`
A command-line launcher that detects virtual environment activation, validates required files are present, then presents a 5-option menu to run the analysis, start the dashboard, open the notebook, or install dependencies.

### `demo.py`
A quick sanity-check script that reads the first 100 rows of `Resume.csv`, runs basic skill extraction using a simple keyword list, and prints the top 10 skills to the console. Useful for verifying setup without launching Streamlit.

### `requirements.txt`
Pinned minimum versions for all 13 required Python packages.

---

## 🔧 Troubleshooting

### ❌ "Could not load data" error
- Verify the dataset path: `Dataset/Resume/Resume.csv` must exist relative to the project root.
- Check for nested directory issues — if the extracted archive created `Dataset/Dataset/Resume/Resume.csv`, run the fix script documented in [Step 4 of Installation](#step-4--verify-dataset-location).

### ❌ ModuleNotFoundError for `pdfplumber` or `docx2txt`
```bash
pip install pdfplumber>=0.10.0 docx2txt>=0.8
```
Or reinstall all dependencies:
```bash
pip install -r requirements.txt
```

### ❌ Streamlit not found
```bash
pip install streamlit>=1.28.0
```

### ❌ Word cloud not rendering
```bash
pip install wordcloud>=1.9.0 matplotlib>=3.6.0
```

### ❌ "Analyse skills" button is greyed out
Load the dataset first by clicking **"Load dataset"** in the sidebar. The Analyse skills button is disabled until data is in memory.

### ❌ Upload returns "Could not analyze" error
- Ensure the file is a valid, non-password-protected PDF or DOCX.
- Very scanned/image-based PDFs (no embedded text layer) will return empty text. Use a text-native PDF.

### ❌ Characters appear garbled / encoding issues on Windows
Run the app from a terminal that supports UTF-8:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
python -m streamlit run src/app.py
```

---

## 🚀 Future Improvements

- [ ] **Job Description Matching** — Paste a JD and see a gap analysis between your resume skills and required skills
- [ ] **Multi-Resume Comparison** — Upload two resumes and compare their scores side-by-side
- [ ] **Radar Chart** — Spider/radar chart for the 4 scoring dimensions per resume
- [ ] **Export Report** — Download a formatted PDF summary of the analysis results
- [ ] **Industry Trend Comparison** — Compare extracted skills against the live frequency data from the loaded dataset
- [ ] **Skill Suggestions by Category** — Recommend top missing skills based on the user's detected job industry
- [ ] **Dark/Light Theme Toggle** — Allow users to switch between colour schemes
- [ ] **Resume History** — Store past analysis results in session state for comparison across multiple uploads

---

## 📄 License

This project is for educational and personal use. The resume dataset originates from [Kaggle](https://www.kaggle.com/) and is subject to its respective terms of use.

---

*Built with ❤️ using Python, Streamlit, and Plotly.*
