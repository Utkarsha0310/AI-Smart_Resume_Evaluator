# AI-Smart Resume Evaluator

A robust, AI-powered Flask web application that analyzes PDF resumes and provides detailed, actionable feedback. By leveraging Natural Language Processing (NLP) techniques, the system evaluates resumes for grammar, readability, ATS compatibility, structure, and keyword optimization to help users land their dream jobs.

![Live Demo](https://img.shields.io/badge/Live_Demo-Render-46E3B7?style=for-the-badge&logo=render)

**Live App:** [https://ai-smart-resume-evaluator.onrender.com](https://ai-smart-resume-evaluator.onrender.com) *(Note: As this is hosted on a free Render tier, the initial load may take 30-50 seconds if the instance has spun down.)*

---

## ✨ Features

- **📄 PDF Text Extraction:** Accurately extracts text from uploaded PDF resumes using PyMuPDF.
- **🧠 Advanced NLP Analysis:** Uses pure Python (`spaCy` + Regex) to detect grammar errors, passive voice, repetition, and structural issues without heavy Java dependencies.
- **🤖 ATS Compatibility Check:** Evaluates formatting, section presence, and keyword density to ensure resumes pass Applicant Tracking Systems.
- **📊 Comprehensive Scoring:** Generates composite scores based on Grammar, Readability (Flesch metrics), Formatting, and Keywords.
- **🎯 Job Role Prediction:** Matches resume content against industry profiles to suggest the best-fitting job roles.
- **📈 Interactive Visualizations:** Displays data in intuitive radar charts and keyword clouds.
- **💾 PDF Report Generation:** Allows users to download a detailed analysis report in PDF format.
- **⚡ Memory Optimized:** Designed to run efficiently on low-memory cloud tiers (512MB RAM) using singleton model loading and Gunicorn preloading.

---

## 🛠️ Technology Stack

- **Backend:** Python 3.12, Flask, Gunicorn
- **NLP & Machine Learning:** spaCy (`en_core_web_sm`), scikit-learn (TF-IDF)
- **Document Processing:** PyMuPDF (`fitz`), ReportLab (for generating output PDFs)
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript (Chart.js)
- **Deployment:** Docker, Render

---

## 🚀 Local Development Setup

Follow these steps to run the application on your local machine.

### 1. Clone the repository
```bash
git clone https://github.com/Utkarsha0310/AI-Smart_Resume_Evaluator.git
cd AI-Smart_Resume_Evaluator
```

### 2. Create a virtual environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Set Environment Variables
```bash
# On Windows (PowerShell)
$env:SESSION_SECRET="your-super-secret-key"

# On macOS/Linux
export SESSION_SECRET="your-super-secret-key"
```

### 5. Run the application
```bash
python app.py
```
Visit `http://localhost:8080` in your browser.

---

## 🐳 Docker Setup

You can also run the application using Docker, ensuring an environment identical to production.

```bash
# Build the image
docker build -t resume-evaluator .

# Run the container
docker run -p 10000:10000 -e PORT=10000 -e SESSION_SECRET="dev-secret" resume-evaluator
```
Visit `http://localhost:10000` in your browser.

---

## ☁️ Deployment (Render)

This project is configured for seamless deployment on Render using Infrastructure-as-Code (`render.yaml`).

1. Fork or clone this repository to your GitHub account.
2. Sign in to **[Render](https://render.com/)**.
3. Go to the dashboard and connect your GitHub repository.
4. Render will automatically detect the `render.yaml` file and configure the service as a Docker container.
5. In the Render Dashboard, generate a value for the `SESSION_SECRET` environment variable.
6. Deploy!

### 💡 Optimization Notes for Free Tiers
- **No Java:** `language_tool_python` was replaced with a custom `spaCy` implementation to drop RAM usage by ~300MB.
- **Singleton Model:** The NLP model loads once at startup (`--preload` in Gunicorn) rather than per request.
- **Worker Limits:** Configured to run `1` worker with `2` threads to comfortably fit inside Render's 512MB RAM limit.

---

## 📁 Project Structure

```text
├── app.py                      # Main Flask application and routing
├── Dockerfile                  # Docker configuration for production
├── render.yaml                 # Render deployment configuration
├── requirements.txt            # Python dependencies
├── modules/
│   ├── nlp_processor.py        # spaCy NLP, grammar, and readability logic
│   ├── resume_analyzer.py      # Core scoring and comparison logic
│   ├── data_processor.py       # Dataset processing logic
│   └── report_generator.py     # PDF report generation
├── templates/                  # HTML templates (Jinja2)
│   ├── index.html
│   ├── results.html
│   ├── improve.html
│   └── visualization.html
└── static/
    ├── css/style.css           # Custom styling
    └── js/main.js              # Frontend logic
```

---

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).
