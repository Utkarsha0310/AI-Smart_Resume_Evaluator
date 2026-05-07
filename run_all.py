
#!/usr/bin/env python3
"""
AI Resume Evaluator - Complete Startup Script
This script handles everything: dependencies, models, and Flask server startup.
"""

import os
import sys
import logging
import subprocess
import time
from pathlib import Path
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """Print startup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                   AI Resume Evaluator                        ║
    ║              Complete Auto-Setup & Launch                   ║
    ╚══════════════════════════════════════════════════════════════╝
    
    🚀 Starting complete system initialization...
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        sys.exit(1)
    logger.info(f"✓ Python version: {sys.version.split()[0]}")

def setup_directories():
    """Setup all required directories"""
    directories = [
        'uploads', 'data', 'data/.models', 'static/css', 'static/js', 
        'templates', 'modules', 'reports'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Directory ready: {directory}")

def setup_environment():
    """Setup environment variables"""
    env_vars = {
        'SESSION_SECRET': 'ai-resume-evaluator-secret-key-2024',
        'FLASK_ENV': 'development',
        'FLASK_DEBUG': '1',
        'PYTHONPATH': os.getcwd()
    }
    
    for key, default_value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = default_value
            logger.info(f"✓ Environment variable set: {key}")

def install_dependencies():
    """Install all required dependencies"""
    logger.info("Installing Python dependencies...")
    
    try:
        # Use uv if available, fallback to pip
        result = subprocess.run(['uv', 'sync'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✓ Dependencies installed with uv")
        else:
            # Fallback to pip
            packages = [
                'flask>=3.1.2',
                'spacy>=3.8.7',
                'scikit-learn>=1.7.1',
                'pandas>=2.3.2',
                'numpy>=2.3.2',
                'PyMuPDF>=1.26.4',
                'reportlab>=4.4.3',
                'textstat>=0.7.10',
                'language-tool-python>=2.9.4',
                'email-validator>=2.3.0',
                'werkzeug>=3.1.3',
                'matplotlib>=3.10.6',
                'gunicorn>=23.0.0'
            ]
            
            for package in packages:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                             capture_output=True)
            
            logger.info("✓ Dependencies installed with pip")
            
    except Exception as e:
        logger.error(f"Dependency installation failed: {e}")

def download_spacy_models():
    """Download and setup spaCy models"""
    logger.info("Setting up spaCy models...")
    
    models = ['en_core_web_sm', 'en_core_web_md']
    
    for model in models:
        try:
            import spacy
            spacy.load(model)
            logger.info(f"✓ spaCy model available: {model}")
        except OSError:
            logger.info(f"⏳ Downloading spaCy model: {model}")
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'spacy', 'download', model
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    logger.info(f"✓ Downloaded spaCy model: {model}")
                else:
                    logger.warning(f"Failed to download {model}: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                logger.warning(f"Timeout downloading {model}")
            except Exception as e:
                logger.warning(f"Error downloading {model}: {e}")

def setup_language_tool():
    """Setup Language Tool for grammar checking"""
    logger.info("Setting up Language Tool...")
    
    try:
        import language_tool_python
        tool = language_tool_python.LanguageTool('en-US')
        # Test with a simple sentence
        tool.check("This is a test.")
        tool.close()
        logger.info("✓ Language Tool ready")
    except Exception as e:
        logger.warning(f"Language Tool setup issue: {e}")

def check_dataset():
    """Check and setup dataset"""
    logger.info("Checking dataset...")
    
    resume_csv_path = Path('data/Resume.csv')
    if resume_csv_path.exists():
        logger.info("✓ Resume dataset found")
    else:
        logger.warning("⚠ Resume.csv not found - will use fallback exemplars")
    
    # Ensure exemplar cache directory exists
    Path('data/.models').mkdir(parents=True, exist_ok=True)
    logger.info("✓ Model cache directory ready")

def verify_system():
    """Verify all system components"""
    logger.info("Verifying system components...")
    
    # Test imports
    required_modules = [
        ('flask', 'Flask'),
        ('spacy', 'spaCy'),
        ('sklearn', 'scikit-learn'),
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy'),
        ('fitz', 'PyMuPDF'),
        ('reportlab', 'ReportLab'),
        ('textstat', 'TextStat')
    ]
    
    all_good = True
    for module, name in required_modules:
        try:
            __import__(module)
            logger.info(f"✓ {name} ready")
        except ImportError:
            logger.error(f"✗ {name} not available")
            all_good = False
    
    # Test Flask app import
    try:
        from app import app
        logger.info("✓ Flask app ready")
    except Exception as e:
        logger.error(f"✗ Flask app import failed: {e}")
        all_good = False
    
    if not all_good:
        logger.error("System verification failed")
        return False
    
    logger.info("✓ All system components verified")
    return True

def start_server():
    """Start the Flask server"""
    logger.info("🚀 Starting AI Resume Evaluator server...")
    logger.info("Server will be available at: http://127.0.0.1:8080")
    logger.info("Press Ctrl+C to stop the server")
    
    try:
        from app import app
        app.run(host='127.0.0.1', port=8080, debug=True, threaded=True)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        sys.exit(1)

def main():
    """Main startup function - runs everything"""
    try:
        print_banner()
        
        # System setup
        logger.info("🔧 Setting up system...")
        check_python_version()
        setup_directories()
        setup_environment()
        
        # Dependencies and models
        logger.info("📦 Installing dependencies...")
        install_dependencies()
        
        logger.info("🤖 Setting up AI models...")
        download_spacy_models()
        setup_language_tool()
        
        # Data setup
        logger.info("📊 Setting up data...")
        check_dataset()
        
        # Verification
        logger.info("🔍 Verifying system...")
        if not verify_system():
            logger.error("System verification failed. Please check errors above.")
            sys.exit(1)
        
        logger.info("✅ System initialization complete!")
        logger.info("=" * 60)
        
        # Start server
        start_server()
        
    except KeyboardInterrupt:
        logger.info("Startup cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
