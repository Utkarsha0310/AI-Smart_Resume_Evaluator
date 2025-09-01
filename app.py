import os
import logging
from flask import Flask, render_template, request, jsonify, session, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import json
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Import modules after app creation to avoid circular imports
from modules.resume_analyzer import ResumeAnalyzer
from modules.report_generator import ReportGenerator

# Initialize global analyzer
analyzer = ResumeAnalyzer()
report_generator = ReportGenerator()

@app.route('/')
def index():
    """Main upload page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    """Handle resume upload and redirect to results"""
    try:
        if 'resume' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        file = request.files['resume']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        if file and file.filename and allowed_file(file.filename):
            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # Get analysis mode from form
            heavy_mode = request.form.get('heavy_mode') == 'on'
            
            # Analyze resume
            analysis_results = analyzer.analyze_resume(filepath, heavy_mode=heavy_mode)
            
            # Store results in session
            session['analysis_results'] = analysis_results
            session['filename'] = filename
            session['filepath'] = filepath
            
            return redirect(url_for('results'))
        else:
            flash('Invalid file type. Please upload a PDF file.', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        flash('An error occurred while processing your resume. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/results')
def results():
    """Display analysis results"""
    if 'analysis_results' not in session:
        flash('No analysis results found. Please upload a resume first.', 'error')
        return redirect(url_for('index'))
    
    results = session['analysis_results']
    filename = session.get('filename', 'Unknown')
    
    return render_template('results.html', results=results, filename=filename)

@app.route('/improve')
def improve():
    """Display improvement recommendations"""
    if 'analysis_results' not in session:
        flash('No analysis results found. Please upload a resume first.', 'error')
        return redirect(url_for('index'))
    
    results = session['analysis_results']
    filename = session.get('filename', 'Unknown')
    
    return render_template('improve.html', results=results, filename=filename)

@app.route('/visualization')
def visualization():
    """Display interactive charts and visualizations"""
    if 'analysis_results' not in session:
        flash('No analysis results found. Please upload a resume first.', 'error')
        return redirect(url_for('index'))
    
    results = session['analysis_results']
    filename = session.get('filename', 'Unknown')
    
    return render_template('visualization.html', results=results, filename=filename)

@app.route('/api/chart-data/<chart_type>')
def get_chart_data(chart_type):
    """API endpoint to get chart data"""
    if 'analysis_results' not in session:
        return jsonify({'error': 'No analysis results found'}), 404
    
    results = session['analysis_results']
    
    try:
        chart_data = analyzer.get_chart_data(results, chart_type)
        return jsonify(chart_data)
    except Exception as e:
        logging.error(f"Chart data error: {str(e)}")
        return jsonify({'error': 'Failed to generate chart data'}), 500

@app.route('/download-report')
def download_report():
    """Generate and download PDF report"""
    if 'analysis_results' not in session:
        flash('No analysis results found. Please upload a resume first.', 'error')
        return redirect(url_for('index'))
    
    try:
        results = session['analysis_results']
        filename = session.get('filename', 'resume')
        
        # Generate PDF report
        report_path = report_generator.generate_report(results, filename)
        
        return send_file(
            report_path,
            as_attachment=True,
            download_name=f"resume_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logging.error(f"Report generation error: {str(e)}")
        flash('An error occurred while generating the report. Please try again.', 'error')
        return redirect(url_for('results'))

@app.route('/api/toggle-theme', methods=['POST'])
def toggle_theme():
    """Toggle between light and dark theme"""
    current_theme = session.get('theme', 'dark')
    new_theme = 'light' if current_theme == 'dark' else 'dark'
    session['theme'] = new_theme
    return jsonify({'theme': new_theme})

@app.route('/api/get-theme')
def get_theme():
    """Get current theme"""
    theme = session.get('theme', 'dark')
    return jsonify({'theme': theme})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('base.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html', error="Internal server error"), 500

@app.errorhandler(413)
def too_large(error):
    flash('File too large. Please upload a file smaller than 16MB.', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
