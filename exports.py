"""
Export functionality for ErosionWatch
Handles PDF and CSV report generation
"""

import csv
import io
import os
from datetime import datetime
from typing import List, Dict, Optional

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.lib.colors import Color, black, red, green, orange
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ReportLab not available. PDF generation will use alternative method.")

def generate_csv_report(results: List[Dict]) -> str:
    """
    Generate CSV report from analysis results.
    
    Args:
        results: List of analysis results
    
    Returns:
        CSV content as string
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Location',
        'Filename', 
        'Soil Loss (mm)',
        'Risk Level',
        'Confidence',
        'Action Required',
        'Recommendation',
        'Priority',
        'Planting Spacing'
    ])
    
    # Write data rows
    for i, result in enumerate(results, 1):
        recommendation = result.get('recommendation', {})
        
        writer.writerow([
            result.get('location', f'Location {i}'),
            result.get('filename', 'Unknown'),
            f"{result.get('erosion_mm', 0):.1f}",
            result.get('risk_level', 'Unknown'),
            f"{result.get('confidence', 0):.2f}",
            recommendation.get('action', 'Monitor'),
            recommendation.get('description', 'Continue monitoring'),
            recommendation.get('priority', 'Routine'),
            recommendation.get('spacing', 'Standard practices')
        ])
    
    # Add summary statistics
    writer.writerow([])  # Empty row
    writer.writerow(['Summary Statistics'])
    writer.writerow(['Total Locations', len(results)])
    writer.writerow(['High Risk Count', sum(1 for r in results if r.get('risk_level') == 'High')])
    writer.writerow(['Medium Risk Count', sum(1 for r in results if r.get('risk_level') == 'Medium')])
    writer.writerow(['Low Risk Count', sum(1 for r in results if r.get('risk_level') == 'Low')])
    writer.writerow(['Average Erosion (mm)', f"{sum(r.get('erosion_mm', 0) for r in results) / len(results):.1f}"])
    writer.writerow(['Report Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    
    return output.getvalue()

def generate_pdf_report(results: List[Dict], output_path: str, map_path: Optional[str] = None) -> None:
    """
    Generate PDF report from analysis results.
    
    Args:
        results: List of analysis results
        output_path: Path where to save the PDF
        map_path: Optional path to the risk map image
    """
    if REPORTLAB_AVAILABLE:
        generate_pdf_reportlab(results, output_path, map_path)
    else:
        generate_pdf_simple(results, output_path, map_path)

def generate_pdf_reportlab(results: List[Dict], output_path: str, map_path: Optional[str] = None) -> None:
    """Generate PDF using ReportLab library."""
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=black
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=black
    )
    
    # Build story (content)
    story = []
    
    # Title
    story.append(Paragraph("ErosionWatch Analysis Report", title_style))
    story.append(Spacer(1, 12))
    
    # Report metadata
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    story.append(Paragraph(f"Total Locations Analyzed: {len(results)}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    
    high_risk_count = sum(1 for r in results if r.get('risk_level') == 'High')
    medium_risk_count = sum(1 for r in results if r.get('risk_level') == 'Medium')
    low_risk_count = sum(1 for r in results if r.get('risk_level') == 'Low')
    avg_erosion = sum(r.get('erosion_mm', 0) for r in results) / len(results) if results else 0
    
    summary_text = f"""
    This report analyzes soil erosion measurements from {len(results)} locations on your farm.
    
    <b>Risk Assessment:</b><br/>
    • High Risk Locations: {high_risk_count}<br/>
    • Medium Risk Locations: {medium_risk_count}<br/>
    • Low Risk Locations: {low_risk_count}<br/>
    
    <b>Average Soil Loss:</b> {avg_erosion:.1f} mm<br/>
    
    {"<b>Immediate Action Required:</b> High-risk areas need urgent intervention with contour planting." if high_risk_count > 0 else "Overall erosion levels are manageable with routine monitoring."}
    """
    
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Risk Map
    if map_path and os.path.exists(map_path):
        story.append(Paragraph("Risk Map", heading_style))
        story.append(Paragraph("Color-coded map showing erosion risk levels across analyzed locations:", styles['Normal']))
        
        try:
            # Add the risk map image
            img = Image(map_path, width=6*inch, height=4.5*inch)
            story.append(img)
            story.append(Spacer(1, 20))
        except Exception as e:
            story.append(Paragraph(f"Risk map could not be embedded: {str(e)}", styles['Normal']))
    
    # Detailed Results Table
    story.append(Paragraph("Detailed Analysis Results", heading_style))
    
    # Create table data
    table_data = [['Location', 'Soil Loss (mm)', 'Risk Level', 'Action Required', 'Priority']]
    
    for i, result in enumerate(results, 1):
        recommendation = result.get('recommendation', {})
        table_data.append([
            result.get('location', f'Location {i}'),
            f"{result.get('erosion_mm', 0):.1f}",
            result.get('risk_level', 'Unknown'),
            recommendation.get('action', 'Monitor'),
            recommendation.get('priority', 'Routine')
        ])
    
    # Create and style table
    table = Table(table_data, colWidths=[1.5*inch, 1*inch, 1*inch, 2*inch, 1.2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), Color(0.8, 0.8, 0.8)),
        ('TEXTCOLOR', (0, 0), (-1, 0), black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), Color(0.95, 0.95, 0.95)),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Recommendations Section
    story.append(Paragraph("Detailed Recommendations", heading_style))
    
    for i, result in enumerate(results, 1):
        recommendation = result.get('recommendation', {})
        location = result.get('location', f'Location {i}')
        
        rec_text = f"""
        <b>{location}</b> (Risk: {result.get('risk_level', 'Unknown')})<br/>
        <b>Action:</b> {recommendation.get('action', 'Monitor')}<br/>
        <b>Description:</b> {recommendation.get('description', 'Continue monitoring')}<br/>
        <b>Planting Details:</b> {recommendation.get('spacing', 'Standard practices')}<br/>
        <b>Timeline:</b> {recommendation.get('priority', 'Routine monitoring')}<br/>
        """
        
        story.append(Paragraph(rec_text, styles['Normal']))
        story.append(Spacer(1, 12))
    
    # Methodology section
    story.append(Paragraph("Methodology", heading_style))
    methodology_text = """
    <b>Analysis Method:</b> ErosionWatch analyzes post-storm photographs containing reference pins 
    or rulers to measure soil erosion. The system detects the reference object in each image, 
    calculates the scale (pixels to millimeters), and measures the exposed length of the pin 
    to determine soil loss.
    
    <b>Risk Categories:</b><br/>
    • <b>Low Risk:</b> < 5mm soil loss - Continue monitoring<br/>
    • <b>Medium Risk:</b> 5-15mm soil loss - Consider preventive measures<br/>
    • <b>High Risk:</b> > 15mm soil loss - Immediate intervention required<br/>
    
    <b>Recommendations:</b> Based on measured erosion levels, the system suggests appropriate 
    erosion control measures, primarily focusing on contour planting of vetiver grass or 
    similar vegetation barriers to prevent further soil loss.
    """
    
    story.append(Paragraph(methodology_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)

def generate_pdf_simple(results: List[Dict], output_path: str, map_path: Optional[str] = None) -> None:
    """Generate simple PDF without ReportLab (fallback method)."""
    try:
        # Try using matplotlib for basic PDF generation
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
        
        with PdfPages(output_path) as pdf:
            # Create a simple text-based report
            fig, ax = plt.subplots(figsize=(8.5, 11))
            ax.axis('off')
            
            # Title
            ax.text(0.5, 0.95, 'ErosionWatch Analysis Report', 
                   horizontalalignment='center', fontsize=20, fontweight='bold')
            
            # Report metadata
            ax.text(0.1, 0.88, f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                   fontsize=12)
            ax.text(0.1, 0.85, f"Total Locations: {len(results)}", fontsize=12)
            
            # Summary statistics
            high_risk_count = sum(1 for r in results if r.get('risk_level') == 'High')
            medium_risk_count = sum(1 for r in results if r.get('risk_level') == 'Medium')
            low_risk_count = sum(1 for r in results if r.get('risk_level') == 'Low')
            
            y_pos = 0.78
            ax.text(0.1, y_pos, "Risk Assessment:", fontsize=14, fontweight='bold')
            y_pos -= 0.04
            ax.text(0.1, y_pos, f"• High Risk: {high_risk_count} locations", fontsize=12)
            y_pos -= 0.03
            ax.text(0.1, y_pos, f"• Medium Risk: {medium_risk_count} locations", fontsize=12)
            y_pos -= 0.03
            ax.text(0.1, y_pos, f"• Low Risk: {low_risk_count} locations", fontsize=12)
            
            # Results table
            y_pos -= 0.08
            ax.text(0.1, y_pos, "Detailed Results:", fontsize=14, fontweight='bold')
            y_pos -= 0.05
            
            # Table headers
            ax.text(0.1, y_pos, "Location", fontsize=10, fontweight='bold')
            ax.text(0.35, y_pos, "Erosion (mm)", fontsize=10, fontweight='bold')
            ax.text(0.55, y_pos, "Risk", fontsize=10, fontweight='bold')
            ax.text(0.7, y_pos, "Action", fontsize=10, fontweight='bold')
            y_pos -= 0.03
            
            # Data rows
            for i, result in enumerate(results):
                if y_pos < 0.1:  # Start new page if needed
                    pdf.savefig(fig, bbox_inches='tight')
                    fig, ax = plt.subplots(figsize=(8.5, 11))
                    ax.axis('off')
                    y_pos = 0.95
                
                location = result.get('location', f'Location {i+1}')
                erosion = result.get('erosion_mm', 0)
                risk = result.get('risk_level', 'Unknown')
                action = result.get('recommendation', {}).get('action', 'Monitor')
                
                ax.text(0.1, y_pos, location[:15], fontsize=9)
                ax.text(0.35, y_pos, f"{erosion:.1f}", fontsize=9)
                ax.text(0.55, y_pos, risk, fontsize=9)
                ax.text(0.7, y_pos, action[:20], fontsize=9)
                y_pos -= 0.03
            
            pdf.savefig(fig, bbox_inches='tight')
            
        return
        
    except ImportError:
        pass
    
    # Final fallback: create a simple text file with PDF extension
    with open(output_path.replace('.pdf', '.txt'), 'w') as f:
        f.write("ErosionWatch Analysis Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n")
        f.write(f"Total Locations: {len(results)}\n\n")
        
        # Summary
        high_risk_count = sum(1 for r in results if r.get('risk_level') == 'High')
        medium_risk_count = sum(1 for r in results if r.get('risk_level') == 'Medium')
        low_risk_count = sum(1 for r in results if r.get('risk_level') == 'Low')
        
        f.write("Risk Assessment:\n")
        f.write(f"• High Risk: {high_risk_count} locations\n")
        f.write(f"• Medium Risk: {medium_risk_count} locations\n")
        f.write(f"• Low Risk: {low_risk_count} locations\n\n")
        
        # Detailed results
        f.write("Detailed Results:\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Location':<20} {'Erosion (mm)':<15} {'Risk':<10} {'Action Required':<30}\n")
        f.write("-" * 80 + "\n")
        
        for i, result in enumerate(results, 1):
            location = result.get('location', f'Location {i}')
            erosion = result.get('erosion_mm', 0)
            risk = result.get('risk_level', 'Unknown')
            action = result.get('recommendation', {}).get('action', 'Monitor')
            
            f.write(f"{location:<20} {erosion:<15.1f} {risk:<10} {action:<30}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("Note: PDF generation requires ReportLab library. ")
        f.write("This report has been saved as a text file instead.\n")

def create_summary_statistics(results: List[Dict]) -> Dict:
    """Create summary statistics from analysis results."""
    if not results:
        return {}
    
    erosion_values = [r.get('erosion_mm', 0) for r in results]
    risk_levels = [r.get('risk_level', 'Unknown') for r in results]
    
    return {
        'total_locations': len(results),
        'high_risk_count': risk_levels.count('High'),
        'medium_risk_count': risk_levels.count('Medium'),
        'low_risk_count': risk_levels.count('Low'),
        'average_erosion': sum(erosion_values) / len(erosion_values),
        'max_erosion': max(erosion_values),
        'min_erosion': min(erosion_values),
        'total_erosion': sum(erosion_values)
    }