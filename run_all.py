#!/usr/bin/env python3
"""
AI Resume Evaluator - Startup Script
This script initializes the resume analysis system and starts the Flask server.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        sys.exit(1)
    logger.info(f"Python version: {sys.version}")

def setup_environment():
    """Setup environment variables and directories"""
    # Ensure required directories exist
    directories = ['uploads', 'data', 'static/css', 'static/js', 'templates', 'modules']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory ensured: {directory}")
    
    # Set default environment variables if not present
    env_vars = {
        'SESSION_SECRET': 'dev-secret-key-change-in-production',
        'FLASK_ENV': 'development',
        'FLASK_DEBUG': '1'
    }
    
    for key, default_value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = default_value
            logger.info(f"Set environment variable: {key}")

def check_dependencies():
    """Check if required Python packages are available"""
    required_packages = [
        'flask',
        'spacy',
        'scikit-learn',
        'pandas',
        'numpy',
        'PyMuPDF',
        'reportlab',
        'sentence-transformers',
        'textstat',
        'language-tool-python'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"✓ Package available: {package}")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"✗ Package missing: {package}")
    
    if missing_packages:
        logger.error("Missing required packages. Please install them using:")
        logger.error(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def download_spacy_models():
    """Download required spaCy models if not available"""
    models = ['en_core_web_sm', 'en_core_web_md']
    
    for model in models:
        try:
            import spacy
            spacy.load(model)
            logger.info(f"✓ spaCy model available: {model}")
        except OSError:
            logger.info(f"Downloading spaCy model: {model}")
            try:
                subprocess.run([sys.executable, '-m', 'spacy', 'download', model], 
                             check=True, capture_output=True)
                logger.info(f"✓ Downloaded spaCy model: {model}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to download {model}: {e}")

def initialize_data():
    """Initialize data files and models"""
    # Check if Resume dataset exists
    resume_csv_path = Path('data/Resume.csv')
    if not resume_csv_path.exists():
        logger.warning("Resume.csv not found in data directory")
        logger.info("The system will use fallback exemplars")
    else:
        logger.info("✓ Resume dataset found")
    
    # Create models cache directory
    models_dir = Path('data/.models')
    models_dir.mkdir(parents=True, exist_ok=True)
    logger.info("✓ Models cache directory ready")

def start_flask_server():
    """Start the Flask development server"""
    logger.info("Starting AI Resume Evaluator...")
    logger.info("Server will be available at: http://localhost:5000")
    logger.info("Press Ctrl+C to stop the server")
    
    try:
        # Import and run the Flask app
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

def print_banner():
    """Print startup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                   AI Resume Evaluator                        ║
    ║              Advanced NLP-Powered Analysis                   ║
    ╚══════════════════════════════════════════════════════════════╝
    
    Features:
    • PDF Resume Processing with PyMuPDF
    • Advanced NLP Analysis with spaCy
    • ATS Compatibility Scoring
    • Interactive Visualizations
    • Professional PDF Reports
    • Job Role Predictions
    • Improvement Recommendations
    
    """
    print(banner)

def main():
    """Main startup function"""
    try:
        print_banner()
        
        logger.info("Initializing AI Resume Evaluator...")
        
        # System checks
        check_python_version()
        setup_environment()
        
        if not check_dependencies():
            logger.error("Dependency check failed. Please install missing packages.")
            sys.exit(1)
        
        # Model and data initialization
        download_spacy_models()
        initialize_data()
        
        logger.info("✓ System initialization complete")
        
        # Start the server
        start_flask_server()
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
