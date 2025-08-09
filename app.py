"""
ErosionWatch Web Application
A browser-based tool for measuring soil erosion from post-storm photos
using reference pin analysis and providing actionable recommendations.
"""

import os
import io
import csv
import uuid
from datetime import datetime
from flask import Flask, render_template, request, Response, session, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
import numpy as np
import cv2

# Import our image analysis module
from analysis import analyze_erosion_image, generate_risk_map, calculate_risk_level
from exports import generate_pdf_report, generate_csv_report

app = Flask(__name__)
app.config['SECRET_KEY'] = 'erosion_watch_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload and output directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

def allowed_file(filename):
    """Check if uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the main upload page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle photo upload and process erosion analysis."""
    try:
        # Check if files were uploaded
        if 'files' not in request.files:
            flash('No files uploaded')
            return redirect(request.url)
        
        files = request.files.getlist('files')
        if not files or all(file.filename == '' for file in files):
            flash('No files selected')
            return redirect(request.url)
        
        # Process each uploaded image
        results = []
        uploaded_files = []
        
        for file in files:
            if file and allowed_file(file.filename):
                # Save uploaded file
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                uploaded_files.append(file_path)
                
                # Analyze the image
                try:
                    # Read image using OpenCV
                    img = cv2.imread(file_path)
                    if img is None:
                        flash(f'Could not read image: {filename}')
                        continue
                    
                    # Perform erosion analysis
                    analysis_result = analyze_erosion_image(img, filename)
                    
                    if analysis_result is not None:
                        # Calculate risk level
                        risk_level = calculate_risk_level(analysis_result['erosion_mm'])
                        
                        # Store result
                        result = {
                            'location': analysis_result.get('location', f"Location {len(results)+1}"),
                            'filename': filename,
                            'erosion_mm': analysis_result['erosion_mm'],
                            'risk_level': risk_level,
                            'confidence': analysis_result.get('confidence', 0.8),
                            'original_file': file_path
                        }
                        results.append(result)
                    else:
                        flash(f'Could not analyze image: {filename}')
                
                except Exception as e:
                    flash(f'Error processing {filename}: {str(e)}')
                    continue
        
        if not results:
            flash('No images could be successfully analyzed')
            return redirect(url_for('index'))
        
        # Generate risk map
        try:
            map_filename = f"risk_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            map_path = os.path.join(app.config['OUTPUT_FOLDER'], map_filename)
            generate_risk_map(results, map_path)
            
            # Add recommendations for each location
            for result in results:
                result['recommendation'] = generate_recommendation(result)
            
            # Store results in session for export
            session['analysis_results'] = results
            session['map_filename'] = map_filename
            session['analysis_timestamp'] = datetime.now().isoformat()
            
            return render_template('results.html', 
                                 results=results, 
                                 map_image=f'outputs/{map_filename}',
                                 total_locations=len(results),
                                 high_risk_count=sum(1 for r in results if r['risk_level'] == 'High'))
        
        except Exception as e:
            flash(f'Error generating risk map: {str(e)}')
            return redirect(url_for('index'))
    
    except Exception as e:
        flash(f'Upload error: {str(e)}')
        return redirect(url_for('index'))

def generate_recommendation(result):
    """Generate planting recommendations based on risk level."""
    risk_level = result['risk_level']
    erosion_mm = result['erosion_mm']
    
    # Add some variation to make recommendations less templated
    import random
    
    if risk_level == 'High':
        actions = ['Plant vetiver hedge now', 'Need erosion barrier', 'Stop this erosion']
        descriptions = [
            f'Bad erosion here - {erosion_mm:.1f}mm soil lost. Plant vetiver grass 2-3 meters uphill to stop more loss.',
            f'Lost {erosion_mm:.1f}mm soil - this needs immediate action. Put in a hedge line above this area.',
            f'Heavy erosion - {erosion_mm:.1f}mm gone. Plant vetiver or napier grass upslope right away.'
        ]
        spacings = [
            'Dig shallow trench, plant vetiver every 10cm along the contour',
            'Space vetiver slips about 4 inches apart in a line',
            'Plant dense hedge - 8-12cm between plants'
        ]
        priorities = ['Do this first - next 2 weeks', 'Urgent - before next rains', 'High priority - 2 weeks max']
        
        return {
            'action': random.choice(actions),
            'description': random.choice(descriptions),
            'spacing': random.choice(spacings),
            'priority': random.choice(priorities)
        }
    elif risk_level == 'Medium':
        actions = ['Plant grass strips', 'Add vegetation cover', 'Prevent more erosion']
        descriptions = [
            f'Some erosion starting - {erosion_mm:.1f}mm lost. Plant grass strips uphill to prevent worse damage.',
            f'Moderate loss of {erosion_mm:.1f}mm. Time to add plants before this gets bad.',
            f'{erosion_mm:.1f}mm soil gone - not terrible yet but needs attention soon.'
        ]
        spacings = [
            'Plant grass or cover crops along the slope contours',
            'Make vegetation strips across the slope',
            'Add ground cover - doesn\'t have to be perfect spacing'
        ]
        priorities = ['Next month', 'Within 4-6 weeks', 'When you have time this season']
        
        return {
            'action': random.choice(actions),
            'description': random.choice(descriptions),
            'spacing': random.choice(spacings),
            'priority': random.choice(priorities)
        }
    else:
        actions = ['Keep checking', 'Monitor this area', 'Watch for changes']
        descriptions = [
            f'Small amount lost ({erosion_mm:.1f}mm). Keep existing plants healthy.',
            f'Only {erosion_mm:.1f}mm gone - not bad. Just maintain what you have.',
            f'Minor erosion - {erosion_mm:.1f}mm. Current practices seem to be working.'
        ]
        spacings = [
            'Keep doing what you\'re doing',
            'Maintain existing vegetation',
            'No new planting needed right now'
        ]
        priorities = ['Check again after next big rains', 'Routine monitoring', 'Keep an eye on it']
        
        return {
            'action': random.choice(actions),
            'description': random.choice(descriptions),
            'spacing': random.choice(spacings),
            'priority': random.choice(priorities)
        }

@app.route('/download/csv')
def download_csv():
    """Generate and download CSV report."""
    if 'analysis_results' not in session:
        flash('No analysis results available for download')
        return redirect(url_for('index'))
    
    try:
        csv_data = generate_csv_report(session['analysis_results'])
        
        # Create response
        output = io.StringIO()
        output.write(csv_data)
        output.seek(0)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'erosion_report_{timestamp}.csv'
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment;filename={filename}'}
        )
    
    except Exception as e:
        flash(f'Error generating CSV: {str(e)}')
        return redirect(url_for('index'))

@app.route('/download/pdf')
def download_pdf():
    """Generate and download PDF report."""
    if 'analysis_results' not in session:
        flash('No analysis results available for download')
        return redirect(url_for('index'))
    
    try:
        # Generate PDF
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f'erosion_report_{timestamp}.pdf'
        pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], pdf_filename)
        
        map_path = None
        if 'map_filename' in session:
            map_path = os.path.join(app.config['OUTPUT_FOLDER'], session['map_filename'])
        
        generate_pdf_report(session['analysis_results'], pdf_path, map_path)
        
        return send_file(pdf_path, as_attachment=True, download_name=pdf_filename)
    
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}')
        return redirect(url_for('index'))

@app.route('/download/example/<filename>')
def download_example(filename):
    """Download example images for testing."""
    examples_dir = os.path.join('static', 'examples')
    allowed_files = [
        'location_1_low_erosion.jpg',
        'location_2_medium_erosion.jpg', 
        'location_3_high_erosion.jpg',
        'examples_info.txt'
    ]
    
    if filename not in allowed_files:
        flash('Example file not found')
        return redirect(url_for('index'))
    
    file_path = os.path.join(examples_dir, filename)
    if not os.path.exists(file_path):
        flash('Example file not available')
        return redirect(url_for('index'))
    
    return send_file(file_path, as_attachment=True, download_name=filename)

@app.route('/examples')
def examples_info():
    """Show information about available example images."""
    examples_data = [
        {
            'filename': 'location_1_low_erosion.jpg',
            'title': 'Low Erosion Site',
            'description': 'Minimal soil loss scenario - 8cm pin exposure',
            'risk_level': 'Low',
            'expected_mm': '~80mm',
            'recommendation': 'Continue monitoring'
        },
        {
            'filename': 'location_2_medium_erosion.jpg', 
            'title': 'Medium Erosion Site',
            'description': 'Moderate soil loss requiring preventive action - 15cm pin exposure',
            'risk_level': 'Medium', 
            'expected_mm': '~150mm',
            'recommendation': 'Plan contour vegetation strips'
        },
        {
            'filename': 'location_3_high_erosion.jpg',
            'title': 'High Erosion Site', 
            'description': 'Severe erosion with visible gullying - 25cm pin exposure',
            'risk_level': 'High',
            'expected_mm': '~250mm', 
            'recommendation': 'Immediate intervention required'
        }
    ]
    
    return render_template('examples.html', examples=examples_data)

@app.route('/clear')
def clear_session():
    """Clear analysis results and start over."""
    session.clear()
    return redirect(url_for('index'))

@app.errorhandler(413)
def too_large(e):
    flash('File is too large. Maximum size is 16MB.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Create required directories
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('static/outputs', exist_ok=True)
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)