# 🌱 ErosionWatch Web Application

A browser-based tool for measuring soil erosion from post-storm photos using reference pin analysis and providing actionable recommendations for sustainable agriculture.

## Overview

ErosionWatch helps coffee farmers measure soil erosion after heavy rains. Take photos with a measuring pin or ruler, and the system tells you how much soil washed away and where to plant to stop more erosion.

### Key Features

- **📏 Measures Soil Loss**: Finds rulers or pins in photos and calculates how much soil washed away
- **🗺️ Shows Problem Areas**: Colors your locations green, yellow, or red based on erosion severity  
- **🌿 Planting Advice**: Tells you where to plant vetiver grass to stop more erosion
- **📊 Save Results**: Download PDF reports and data files to keep records
- **💾 Test Photos**: Download sample images to try the system first

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download this repository**
   ```bash
   cd ErosionWatch
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser and go to**
   ```
   http://localhost:5000
   ```

## How to Use

### Option 1: Try with Example Images (Recommended for First Use)

1. **Download Examples**: Visit the application and download demonstration images from the "Example Images" section
2. **Test the System**: Upload the example images to see how ErosionWatch analyzes different erosion scenarios
3. **Review Results**: Compare the automated analysis with the expected values provided
4. **Understand Output**: Examine risk maps, measurements, and recommendations before using your own photos

### Option 2: Use Your Own Photos

1. **Install reference pins**: Drive graduated pins or stakes into your soil at various locations
2. **Take clear photos**: Include the reference pin/ruler in each photo with good lighting
3. **Multiple angles**: Take photos from different locations across your farm for comprehensive analysis

### Using the Web Interface

1. **Choose Your Approach**: Download example images for testing, or upload your own erosion photos
2. **Upload Photos**: Drag and drop or select your images (JPG, PNG, TIFF, BMP)
3. **Automatic Analysis**: The system processes images to detect reference objects and measure soil loss
4. **View Results**: See color-coded risk maps and detailed measurements for each location
5. **Get Recommendations**: Receive specific planting suggestions for erosion control
6. **Export Reports**: Download PDF reports and CSV data for record-keeping

## Technical Architecture

### Backend Components

- **Flask Web Server**: Handles file uploads, processing, and serving results
- **OpenCV Image Processing**: Detects reference pins and measures soil erosion
- **Risk Assessment Engine**: Categorizes locations and generates recommendations
- **Report Generation**: Creates PDF and CSV exports using ReportLab

### Frontend Features

- **Drag-and-Drop Upload**: Modern HTML5 file upload interface
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Feedback**: Progress indicators and error handling
- **Interactive Results**: Color-coded maps and detailed analysis

## File Structure

```
ErosionWatch/
├── app.py                 # Main Flask application
├── analysis.py            # Image analysis and erosion measurement
├── exports.py             # PDF and CSV report generation
├── generate_examples.py   # Script to create demonstration images
├── test_basic.py          # Basic functionality tests
├── run.py                 # Application launcher with dependency checks
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   ├── index.html        # Upload page with example downloads
│   ├── results.html      # Results display page
│   └── examples.html     # Detailed examples page
└── static/
    ├── uploads/          # Uploaded photos (auto-created)
    ├── outputs/          # Generated maps and reports (auto-created)
    └── examples/         # Demo images for testing (auto-created)
```

## Image Analysis Methodology

### Reference Pin Detection

The system uses computer vision to:
1. **Detect Reference Objects**: Locate pins, rulers, or known objects in photos
2. **Calculate Scale**: Determine pixels-to-millimeter ratio from known dimensions
3. **Measure Exposure**: Find the soil line and calculate exposed pin length
4. **Quantify Erosion**: Convert measurements to millimeters of soil loss

### Risk Classification

- **Low Risk**: < 5mm soil loss - Continue monitoring
- **Medium Risk**: 5-15mm soil loss - Consider preventive measures  
- **High Risk**: > 15mm soil loss - Immediate intervention required

### Recommendations

Based on measured erosion levels, the system suggests:
- **Contour Planting**: Vetiver grass hedgerows along slope contours
- **Spacing Guidelines**: 10cm spacing between vetiver slips
- **Timeline**: Urgent (2 weeks), planned (1 month), or routine monitoring

## Deployment Options

### Local Development
```bash
python app.py
```
Access at `http://localhost:5000`

### Production Deployment
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Docker (Optional)
Create a Dockerfile for containerized deployment:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## Troubleshooting

### Common Issues

1. **OpenCV Import Error**
   ```bash
   pip install opencv-python-headless
   ```

2. **PDF Generation Issues**
   ```bash
   pip install reportlab matplotlib
   ```

3. **File Upload Errors**
   - Check file size (max 16MB)
   - Ensure supported formats (JPG, PNG, TIFF, BMP)
   - Verify folder permissions

4. **Port Already in Use**
   - Change port in app.py: `app.run(port=5001)`
   - Or kill existing process on port 5000

### Performance Optimization

- **Image Size**: Resize large images before upload for faster processing
- **Batch Processing**: Upload multiple photos at once for efficiency
- **Memory**: Ensure adequate RAM for image processing (2GB+ recommended)

## Development

### Adding New Features

1. **Image Analysis**: Extend `analysis.py` for new detection methods
2. **Export Formats**: Add new report types in `exports.py`
3. **UI Components**: Modify templates in `templates/` folder
4. **API Endpoints**: Add new routes in `app.py`

### Testing

```bash
pip install pytest pytest-flask
pytest
```

## Support and Documentation

### Scientific Basis

The erosion pin method is based on established field research:
- Used in agricultural studies for quantifying soil movement
- Validated against traditional erosion measurement techniques
- Provides millimeter-scale precision for farm-level monitoring

### Agricultural Context

Designed specifically for:
- **Mountain coffee farms** with steep slopes prone to erosion
- **Post-storm assessment** for rapid damage evaluation
- **Sustainable agriculture** practices using living barriers
- **Farmer-friendly tools** requiring minimal technical knowledge

## License

This project is designed for educational and agricultural use. Please respect the open-source community and contribute improvements back to the project.

## Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with clear documentation

## Contact

For questions, suggestions, or support, please create an issue in the project repository.

---

**ErosionWatch** - Protecting soil, sustaining agriculture 🌱