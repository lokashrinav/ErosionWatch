#!/usr/bin/env python3
"""
Generate example images for ErosionWatch demonstration
Creates realistic sample photos with reference pins showing different erosion scenarios
"""

import cv2
import numpy as np
import os
from datetime import datetime

def create_soil_texture(width, height, base_color, variation=30):
    """Create realistic soil texture using noise."""
    # Create base soil color
    soil = np.full((height, width, 3), base_color, dtype=np.uint8)
    
    # Add noise for texture
    noise = np.random.randint(-variation, variation, (height, width, 3))
    soil = np.clip(soil.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # Add some random soil clumps and texture
    for _ in range(20):
        x = np.random.randint(0, width-20)
        y = np.random.randint(0, height-20)
        w = np.random.randint(5, 15)
        h = np.random.randint(5, 15)
        color_shift = np.random.randint(-20, 20, 3)
        new_color = np.clip(base_color + color_shift, 0, 255)
        cv2.ellipse(soil, (x+w//2, y+h//2), (w//2, h//2), 0, 0, 360, new_color.tolist(), -1)
    
    return soil

def draw_measuring_pin(img, pin_x, soil_level_y, pin_top_y, pin_length_mm=300, exposed_mm=150):
    """Draw a measuring pin with graduations."""
    height, width = img.shape[:2]
    
    # Pin shaft (metal color)
    pin_color = (180, 180, 160)  # Metallic gray
    pin_width = 8
    
    # Draw pin shaft from top to bottom
    cv2.line(img, (pin_x, pin_top_y), (pin_x, soil_level_y + 100), pin_color, pin_width)
    
    # Draw measurement markings every 10mm equivalent
    pixels_per_mm = (soil_level_y - pin_top_y) / exposed_mm
    marking_interval_mm = 10
    marking_interval_px = int(marking_interval_mm * pixels_per_mm)
    
    for i in range(0, int(exposed_mm // marking_interval_mm) + 1):
        mark_y = pin_top_y + i * marking_interval_px
        if mark_y <= soil_level_y:
            # Alternating long and short marks
            mark_length = 15 if i % 5 == 0 else 8
            cv2.line(img, (pin_x - mark_length//2, mark_y), (pin_x + mark_length//2, mark_y), (0, 0, 0), 2)
            
            # Add numbers every 50mm
            if i % 5 == 0 and i > 0:
                cv2.putText(img, f"{i*10}", (pin_x + 20, mark_y + 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
    # Add pin top cap
    cv2.circle(img, (pin_x, pin_top_y), 12, (255, 100, 100), -1)  # Red cap
    cv2.circle(img, (pin_x, pin_top_y), 12, (0, 0, 0), 2)  # Black outline

def draw_ruler(img, ruler_x, ruler_y, length_cm=30):
    """Draw a measuring ruler for scale reference."""
    ruler_width = 40
    ruler_height = length_cm * 10  # 10 pixels per cm
    
    # Draw ruler background (yellow)
    cv2.rectangle(img, (ruler_x, ruler_y), (ruler_x + ruler_width, ruler_y + ruler_height), 
                 (100, 200, 255), -1)
    cv2.rectangle(img, (ruler_x, ruler_y), (ruler_x + ruler_width, ruler_y + ruler_height), 
                 (0, 0, 0), 2)
    
    # Draw centimeter markings
    for cm in range(length_cm + 1):
        y_pos = ruler_y + cm * 10
        # Major marks every cm
        cv2.line(img, (ruler_x, y_pos), (ruler_x + ruler_width, y_pos), (0, 0, 0), 1)
        
        # Numbers every 5cm
        if cm % 5 == 0 and cm > 0:
            cv2.putText(img, f"{cm}", (ruler_x + 5, y_pos - 3), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        # Minor marks every 5mm
        if cm < length_cm:
            y_mid = y_pos + 5
            cv2.line(img, (ruler_x, y_mid), (ruler_x + ruler_width//2, y_mid), (0, 0, 0), 1)

def create_sample_image(scenario_name, erosion_level, output_path):
    """Create a sample erosion measurement image."""
    width, height = 800, 600
    
    # Soil color variations for different scenarios
    soil_colors = {
        'clay': (120, 140, 160),      # Grayish clay
        'sandy': (150, 180, 200),     # Sandy brown
        'loam': (100, 120, 140),      # Dark loam
        'disturbed': (80, 100, 120)   # Darker disturbed soil
    }
    
    # Choose soil type based on scenario
    if 'location_1' in scenario_name.lower():
        soil_type = 'clay'
    elif 'location_2' in scenario_name.lower():
        soil_type = 'sandy'
    else:
        soil_type = 'loam'
    
    # Create soil background
    img = create_soil_texture(width, height, np.array(soil_colors[soil_type]))
    
    # Add some grass/vegetation patches for realism
    for _ in range(5):
        x = np.random.randint(0, width-30)
        y = np.random.randint(0, height//3)  # Top third only
        w = np.random.randint(20, 40)
        h = np.random.randint(10, 25)
        grass_color = (60, 150, 60)  # Green
        cv2.ellipse(img, (x+w//2, y+h//2), (w//2, h//2), 0, 0, 360, grass_color, -1)
    
    # Calculate pin exposure based on erosion level
    pin_x = width // 2 + 50
    pin_top_y = 50
    
    if erosion_level == 'low':
        exposed_mm = 80   # 8cm exposed = low erosion
        soil_level_y = pin_top_y + 200
    elif erosion_level == 'medium':
        exposed_mm = 150  # 15cm exposed = medium erosion
        soil_level_y = pin_top_y + 300
    else:  # high
        exposed_mm = 250  # 25cm exposed = high erosion
        soil_level_y = pin_top_y + 400
    
    # Draw the measuring pin
    draw_measuring_pin(img, pin_x, soil_level_y, pin_top_y, exposed_mm=exposed_mm)
    
    # Draw a ruler for additional reference
    ruler_x = width // 4
    ruler_y = height // 3
    draw_ruler(img, ruler_x, ruler_y)
    
    # Add some environmental details
    # Small rocks
    for _ in range(8):
        x = np.random.randint(0, width-10)
        y = np.random.randint(height//2, height-10)
        size = np.random.randint(3, 8)
        cv2.circle(img, (x, y), size, (80, 90, 100), -1)
    
    # Add water erosion channels for high erosion scenario
    if erosion_level == 'high':
        # Draw some erosion gullies
        for _ in range(3):
            start_x = np.random.randint(0, width//2)
            start_y = np.random.randint(0, height//3)
            end_x = start_x + np.random.randint(100, 200)
            end_y = start_y + np.random.randint(150, 250)
            
            # Create erosion channel
            channel_width = np.random.randint(5, 15)
            darker_soil = tuple(max(0, c - 30) for c in soil_colors[soil_type])
            cv2.line(img, (start_x, start_y), (end_x, end_y), darker_soil, channel_width)
    
    # Add photo metadata overlay (like a camera would)
    timestamp = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
    cv2.rectangle(img, (10, height-40), (300, height-10), (0, 0, 0), -1)
    cv2.putText(img, f"ErosionWatch Demo - {timestamp}", (15, height-20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Save the image
    cv2.imwrite(output_path, img)
    print(f"Generated: {output_path}")

def main():
    """Generate all example images."""
    examples_dir = "static/examples"
    os.makedirs(examples_dir, exist_ok=True)
    
    # Define example scenarios
    scenarios = [
        ("location_1_low_erosion", "low", "Low erosion example - minimal soil loss"),
        ("location_2_medium_erosion", "medium", "Medium erosion example - moderate intervention needed"),
        ("location_3_high_erosion", "high", "High erosion example - urgent action required"),
    ]
    
    print("Generating ErosionWatch example images...")
    
    for scenario_name, erosion_level, description in scenarios:
        output_path = os.path.join(examples_dir, f"{scenario_name}.jpg")
        create_sample_image(scenario_name, erosion_level, output_path)
    
    # Create a metadata file with descriptions
    metadata_path = os.path.join(examples_dir, "examples_info.txt")
    with open(metadata_path, 'w') as f:
        f.write("ErosionWatch Example Images\n")
        f.write("=" * 50 + "\n\n")
        f.write("These images demonstrate different erosion scenarios for testing the analysis system.\n\n")
        
        for scenario_name, erosion_level, description in scenarios:
            f.write(f"• {scenario_name}.jpg\n")
            f.write(f"  Risk Level: {erosion_level.title()}\n")
            f.write(f"  Description: {description}\n")
            f.write(f"  Expected Analysis: ~{80 if erosion_level=='low' else 150 if erosion_level=='medium' else 250}mm exposed pin\n\n")
        
        f.write("Usage Instructions:\n")
        f.write("1. Download one or more example images\n")
        f.write("2. Upload them to the ErosionWatch analysis system\n")
        f.write("3. Review the automated measurements and recommendations\n")
        f.write("4. Use these as a baseline to understand the system capabilities\n")
    
    print(f"Generated {len(scenarios)} example images and metadata file.")
    print("Example images are ready for use!")

if __name__ == "__main__":
    main()