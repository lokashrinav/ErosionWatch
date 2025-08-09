#!/usr/bin/env python3
"""
Basic functionality test for ErosionWatch
Tests core components without requiring actual image files
"""

import os
import sys
import tempfile
import numpy as np

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import numpy
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        from analysis import analyze_erosion_image, calculate_risk_level
        print("✅ Analysis module imported successfully")
    except ImportError as e:
        print(f"❌ Analysis module import failed: {e}")
        return False
    
    try:
        from exports import generate_csv_report
        print("✅ Exports module imported successfully")
    except ImportError as e:
        print(f"❌ Exports module import failed: {e}")
        return False
    
    return True

def test_analysis_functions():
    """Test analysis functions with synthetic data."""
    print("\n🧪 Testing analysis functions...")
    
    try:
        from analysis import calculate_risk_level, simulate_erosion_measurement
        
        # Test risk level calculation
        assert calculate_risk_level(3.0) == 'Low'
        assert calculate_risk_level(10.0) == 'Medium'  
        assert calculate_risk_level(20.0) == 'High'
        print("✅ Risk level calculation working correctly")
        
        # Test with synthetic image
        synthetic_img = np.ones((480, 640, 3), dtype=np.uint8) * 128  # Gray image
        result = simulate_erosion_measurement(synthetic_img, "test_image.jpg")
        
        assert 'erosion_mm' in result
        assert 'confidence' in result
        assert isinstance(result['erosion_mm'], float)
        print("✅ Image simulation working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis function test failed: {e}")
        return False

def test_csv_export():
    """Test CSV export functionality."""
    print("\n🧪 Testing CSV export...")
    
    try:
        from exports import generate_csv_report
        
        # Create test data
        test_results = [
            {
                'location': 'Test Location 1',
                'filename': 'test1.jpg',
                'erosion_mm': 12.5,
                'risk_level': 'Medium',
                'confidence': 0.85,
                'recommendation': {
                    'action': 'Test action',
                    'description': 'Test description',
                    'priority': 'Test priority',
                    'spacing': 'Test spacing'
                }
            }
        ]
        
        csv_content = generate_csv_report(test_results)
        
        assert 'Location' in csv_content
        assert 'Soil Loss (mm)' in csv_content
        assert '12.5' in csv_content
        print("✅ CSV export working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ CSV export test failed: {e}")
        return False

def test_flask_app():
    """Test Flask app initialization."""
    print("\n🧪 Testing Flask app...")
    
    try:
        from app import app
        
        # Test app configuration
        assert app.config['SECRET_KEY'] is not None
        assert 'UPLOAD_FOLDER' in app.config
        assert 'OUTPUT_FOLDER' in app.config
        
        # Test app can create test client
        with app.test_client() as client:
            # Test that the app responds to root route
            response = client.get('/')
            assert response.status_code == 200
            print("✅ Flask app working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_directories():
    """Test that required directories exist or can be created."""
    print("\n🧪 Testing directory structure...")
    
    required_dirs = [
        'static/uploads',
        'static/outputs',
        'templates'
    ]
    
    all_exist = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ Directory exists: {directory}")
        else:
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"✅ Directory created: {directory}")
            except Exception as e:
                print(f"❌ Cannot create directory {directory}: {e}")
                all_exist = False
    
    return all_exist

def main():
    """Run all tests."""
    print("🌱 ErosionWatch Basic Functionality Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Directory Test", test_directories),
        ("Analysis Functions Test", test_analysis_functions),
        ("CSV Export Test", test_csv_export),
        ("Flask App Test", test_flask_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔧 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! ErosionWatch is ready to use.")
        print("\nTo start the application, run:")
        print("   python run.py")
        print("   or")
        print("   python app.py")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())