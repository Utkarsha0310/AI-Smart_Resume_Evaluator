# AI Resume Evaluator

## Overview

The AI Resume Evaluator is a comprehensive Flask-based web application that provides intelligent resume analysis using advanced NLP techniques. The system allows users to upload PDF resumes and receive detailed performance evaluations, including ATS compatibility scoring, improvement recommendations, and interactive visualizations. The application leverages machine learning models, clustering algorithms, and the Kaggle Resume Dataset to compare user resumes against top-performing exemplars and provide actionable insights through a modern, responsive web interface.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework
- **Flask Application**: Core web framework with session management and file upload handling
- **Template Engine**: Jinja2 templating with a base template architecture supporting multiple pages (upload, results, recommendations, visualizations)
- **Static Assets**: Organized CSS/JS structure with Bootstrap 5, Chart.js, and Font Awesome integration
- **Theme System**: Dark/light mode toggle with navy blue color scheme (#0A192F, #1F4068, #162447)

### NLP Processing Pipeline
- **Multi-Mode Analysis**: Supports both lightweight (en_core_web_md, MiniLM) and heavy (en_core_web_trf, all-mpnet-base-v2) processing modes
- **SpaCy Integration**: Advanced text processing for entity recognition, POS tagging, and linguistic analysis
- **Sentence Transformers**: Semantic similarity analysis using transformer models
- **Grammar Analysis**: Language tool integration for grammar and readability scoring
- **Feature Extraction**: TF-IDF vectorization, readability metrics, and content structure analysis

### Data Processing and Machine Learning
- **Resume Dataset Integration**: Utilizes Kaggle Resume Dataset with 2,400+ categorized resumes for benchmarking
- **Clustering System**: K-means clustering with PCA for exemplar identification and resume comparison
- **Feature Engineering**: Text cleaning, skill extraction, keyword density analysis, and structural assessment
- **Caching Strategy**: Model and cluster caching in `/data/.models` directory for performance optimization

### File Processing
- **PDF Extraction**: PyMuPDF (fitz) for robust PDF text extraction with fallback strategies
- **Upload Management**: Secure file handling with 16MB size limit and PDF-only restriction
- **Session Storage**: Analysis results stored in Flask sessions for multi-page navigation

### Report Generation
- **PDF Reports**: Professional multi-page reports using ReportLab with custom styling
- **Interactive Visualizations**: 15+ Chart.js visualizations including score breakdowns, skill gaps, and performance metrics
- **Data Export**: Downloadable PDF reports with comprehensive analysis and recommendations

### Frontend Architecture
- **Responsive Design**: Bootstrap 5-based responsive layout with mobile optimization
- **Interactive Components**: Dynamic file upload areas, progress indicators, and chart controls
- **Animation System**: Canvas confetti animations for positive feedback and engagement
- **Chart Management**: Centralized chart system with theme-aware color schemes and real-time data visualization

### Performance Optimization
- **Async Processing**: Support for background analysis tasks
- **Model Caching**: Pre-loaded NLP models and computed exemplar clusters
- **Lazy Loading**: Progressive content loading for better user experience
- **Error Handling**: Comprehensive fallback strategies to prevent runtime failures

## External Dependencies

### Core Web Stack
- **Flask**: Web framework with Werkzeug utilities for secure file handling
- **Bootstrap 5**: Frontend CSS framework for responsive design
- **Chart.js**: Interactive data visualization library
- **Font Awesome**: Icon library for UI components

### NLP and Machine Learning
- **spaCy**: Natural language processing with multiple model sizes (sm/md/trf)
- **Sentence Transformers**: Semantic similarity analysis (MiniLM, mpnet models)
- **scikit-learn**: Machine learning algorithms for clustering and feature extraction
- **language-tool-python**: Grammar checking and language analysis
- **textstat**: Readability metrics and text complexity analysis

### Data Processing
- **pandas**: Data manipulation and CSV processing for resume dataset
- **numpy**: Numerical computations and array operations
- **PyMuPDF (fitz)**: PDF text extraction and document processing

### Report Generation
- **ReportLab**: PDF generation with professional formatting and styling
- **pickle**: Model serialization for caching processed data

### Frontend Enhancement
- **canvas-confetti**: Animation library for user engagement
- **JavaScript ES6+**: Modern JavaScript for interactive components and theme management

### Development and Deployment
- **Python 3.8+**: Runtime environment with comprehensive logging
- **File System**: Local storage for uploads, models, and generated reports
- **Environment Variables**: Configuration management for secrets and settings