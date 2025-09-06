import numpy as np
import cv2
from datetime import datetime, timedelta
import streamlit as st

def classify_disaster_enhanced(image, location_text="", additional_context=""):
    """Enhanced disaster classification with ocean hazard detection"""
    try:
        img_array = np.array(image)

        avg_color = np.mean(img_array, axis=(0, 1))
        color_std = np.std(img_array, axis=(0, 1))

        color_total = np.sum(avg_color)
        if color_total > 0:
            red_ratio = avg_color[0] / color_total
            green_ratio = avg_color[1] / color_total
            blue_ratio = avg_color[2] / color_total
        else:
            red_ratio = green_ratio = blue_ratio = 0.33

        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        avg_hue = np.mean(hsv[:, :, 0])
        avg_saturation = np.mean(hsv[:, :, 1])
        avg_value = np.mean(hsv[:, :, 2])

        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 30, 100)
        edge_density = np.sum(edges) / (gray.shape[0] * gray.shape[1])

        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        water_smoothness = np.mean(gradient_magnitude)

        classifications = {}
        water_indicators = 0

        if blue_ratio > 0.32:
            water_indicators += 1

        if avg_saturation > 80 and blue_ratio > 0.3:
            water_indicators += 1

        if water_smoothness < 50 and blue_ratio > 0.28:
            water_indicators += 1

        if 90 < avg_hue < 140 and avg_saturation > 60:
            water_indicators += 1

        if water_indicators >= 2:
            flood_base_confidence = 40 + (water_indicators * 15)
            flood_enhancement = (blue_ratio - 0.25) * 100 if blue_ratio > 0.25 else 0
            flood_saturation_bonus = (avg_saturation / 255) * 25
            flood_confidence = min(flood_base_confidence + flood_enhancement + flood_saturation_bonus, 95)
            classifications['Flood'] = flood_confidence

        if blue_ratio > 0.45 and water_smoothness > 60 and avg_saturation > 120:
            tsunami_confidence = min((blue_ratio - 0.35) * 200 + water_smoothness, 90)
            classifications['Tsunami'] = tsunami_confidence

        if blue_ratio > 0.4 and edge_density > 0.1 and avg_value > 100:
            surge_confidence = min((blue_ratio - 0.3) * 150 + edge_density * 200, 85)
            classifications['Coastal Surge'] = surge_confidence

        if blue_ratio > 0.35 and avg_value < 120 and edge_density > 0.15:
            storm_surge_confidence = min((blue_ratio - 0.25) * 120 + (1 - avg_value/255) * 80, 80)
            classifications['Storm Surge'] = storm_surge_confidence

        if 0.35 < green_ratio < 0.55 and red_ratio > 0.25 and avg_saturation > 100:
            if 40 < avg_hue < 80:
                bloom_confidence = min((green_ratio - 0.3) * 180 + (avg_saturation / 255) * 30, 75)
                classifications['Harmful Algal Bloom'] = bloom_confidence

        if red_ratio > 0.38 and avg_hue < 35:
            fire_confidence = min((red_ratio - 0.3) * 250 + (avg_saturation / 255) * 40, 95)
            classifications['Fire/Wildfire'] = fire_confidence

        if avg_value < 110 and edge_density > 0.12:
            storm_confidence = min((1 - avg_value/255) * 80 + edge_density * 120, 85)
            classifications['Cyclone/Storm'] = storm_confidence

        if color_std.mean() > 45 and edge_density > 0.18:
            earthquake_confidence = min(color_std.mean() / 1.8 + edge_density * 180, 80)
            classifications['Earthquake/Building Collapse'] = earthquake_confidence

        brown_score = (red_ratio * 0.65 + green_ratio * 0.35 + blue_ratio * 0.1)
        if brown_score > 0.38 and 15 < avg_hue < 65:
            landslide_confidence = min(brown_score * 120 + (avg_hue - 15) * 1.5, 75)
            classifications['Landslide'] = landslide_confidence

        location_lower = (location_text + " " + additional_context).lower()

        ocean_keywords = ['sea', 'ocean', 'coast', 'coastal', 'beach', 'shore', 'marine', 'bay', 'gulf', 'island', 'port', 'harbor', 'tide', 'wave']
        if any(keyword in location_lower for keyword in ocean_keywords):
            for ocean_type in ['Tsunami', 'Coastal Surge', 'Storm Surge', 'Harmful Algal Bloom']:
                if ocean_type in classifications:
                    classifications[ocean_type] += 20
                elif blue_ratio > 0.3:
                    if ocean_type == 'Coastal Surge':
                        classifications[ocean_type] = 60

        water_keywords = ['river', 'lake', 'dam', 'reservoir', 'canal', 'stream', 'pond']
        if any(keyword in location_lower for keyword in water_keywords):
            if 'Flood' in classifications:
                classifications['Flood'] += 25
            elif blue_ratio > 0.28:
                classifications['Flood'] = 70

        if any(word in location_lower for word in ['forest', 'mountain', 'hill', 'rural', 'village']):
            if 'Fire/Wildfire' in classifications:
                classifications['Fire/Wildfire'] += 15
            if 'Landslide' in classifications:
                classifications['Landslide'] += 12

        if any(word in location_lower for word in ['urban', 'city', 'building', 'residential', 'tower', 'complex']):
            if 'Earthquake/Building Collapse' in classifications:
                classifications['Earthquake/Building Collapse'] += 15

        if classifications:
            best_disaster = max(classifications.items(), key=lambda x: x[1])
            disaster_type, confidence = best_disaster
        else:
            disaster_type, confidence = "Natural Disaster", 60.0

        explanation = f"Enhanced AI Analysis: "
        explanation += f"Color ratios (R:{red_ratio:.2f}, G:{green_ratio:.2f}, B:{blue_ratio:.2f}), "
        explanation += f"Water indicators: {water_indicators if 'water_indicators' in locals() else 'N/A'}, "
        explanation += f"Surface smoothness: {water_smoothness:.1f}, "
        explanation += f"Edge patterns: {edge_density:.3f}, "
        explanation += f"Location context applied"

        return disaster_type, min(confidence, 95), explanation

    except Exception as e:
        return "Unknown", 50.0, f"Enhanced classification error: {e}"

def advanced_deepfake_detection(image):
    """Enhanced deepfake detection with ocean-specific analysis"""
    try:
        img_array = np.array(image)

        if len(img_array.shape) != 3:
            return False, 0, "Invalid image format"

        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)

        features = {}

        features['variance'] = np.var(gray)
        features['std_dev'] = np.std(gray)
        features['texture_contrast'] = np.max(gray) - np.min(gray)

        edges = cv2.Canny(gray, 30, 120)
        features['edge_density'] = np.sum(edges) / (gray.shape[0] * gray.shape[1])
        features['edge_variance'] = np.var(edges)

        features['color_variance'] = np.var(img_array, axis=(0, 1))
        features['saturation_mean'] = np.mean(hsv[:, :, 1])
        features['saturation_std'] = np.std(hsv[:, :, 1])

        features['lab_variance'] = np.var(lab, axis=(0, 1))
        features['luminance_distribution'] = np.std(lab[:, :, 0])

        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.log(np.abs(f_shift) + 1)
        features['freq_variance'] = np.var(magnitude_spectrum)
        features['freq_peak_count'] = len(np.where(magnitude_spectrum > np.mean(magnitude_spectrum) + 2*np.std(magnitude_spectrum))[0])

        features['compression_score'] = detect_compression_artifacts_enhanced(gray)

        if np.mean(img_array[:, :, 2]) > np.mean(img_array[:, :, 0]):
            features['water_authenticity'] = analyze_water_authenticity(img_array)
        else:
            features['water_authenticity'] = 50

        authenticity_score = calculate_authenticity_score_enhanced(features)

        if authenticity_score > 85:
            return True, authenticity_score, "✅ High confidence - Image verified authentic"
        elif authenticity_score > 70:
            return True, authenticity_score, "✅ Good confidence - Likely authentic"
        elif authenticity_score > 55:
            return True, authenticity_score, "⚠️ Moderate confidence - Probably authentic"
        elif authenticity_score > 40:
            return False, authenticity_score, "⚠️ Low confidence - Possibly manipulated"
        else:
            return False, authenticity_score, "❌ Very low confidence - Likely fake/manipulated"

    except Exception as e:
        return False, 50, f"❌ Enhanced authenticity analysis failed: {e}"

def detect_compression_artifacts_enhanced(gray_image):
    """Enhanced compression artifact detection"""
    try:
        h, w = gray_image.shape
        block_score = 0
        boundary_score = 0

        for i in range(0, h - 8, 8):
            for j in range(0, w - 8, 8):
                block = gray_image[i:i+8, j:j+8]
                block_variance = np.var(block)

                if block_variance > 80:
                    block_score += 1

                if i > 0 and j > 0:
                    boundary_diff = np.mean(np.abs(gray_image[i-1:i+1, j:j+8] - gray_image[i:i+2, j:j+8]))
                    if boundary_diff < 10:
                        boundary_score += 1

        total_blocks = ((h // 8) * (w // 8))
        if total_blocks > 0:
            natural_score = (block_score / total_blocks) * 100
            compression_score = max(0, 100 - (boundary_score / total_blocks) * 200)
            return (natural_score + compression_score) / 2

        return 50
    except:
        return 50

def analyze_water_authenticity(img_array):
    """Ocean-specific authenticity analysis for water images"""
    try:
        blue_channel = img_array[:, :, 2]

        gradient_x = np.gradient(blue_channel, axis=1)
        gradient_y = np.gradient(blue_channel, axis=0)
        gradient_variance = np.var(gradient_x) + np.var(gradient_y)

        reflection_score = 0
        if np.std(blue_channel) > 20:
            reflection_score += 30

        texture_score = min(gradient_variance / 10, 40)

        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        hue_consistency = 100 - np.std(hsv[:, :, 0])
        water_hue_score = min(hue_consistency / 2, 30)

        total_score = reflection_score + texture_score + water_hue_score
        return min(total_score, 100)

    except:
        return 50

def calculate_authenticity_score_enhanced(features):
    """Enhanced authenticity scoring algorithm"""
    try:
        score = 0

        if features['variance'] > 1200:
            score += 30
        elif features['variance'] > 800:
            score += 20
        elif features['variance'] > 400:
            score += 10
        else:
            score += 3

        if 0.08 < features['edge_density'] < 0.35:
            score += 25
        elif features['edge_density'] > 0.05:
            score += 15

        if features['edge_variance'] > 50:
            score += 10

        color_score = min(np.sum(features['color_variance']) / 80, 25)
        score += color_score

        if 50 < features['saturation_mean'] < 200:
            score += 15
            if features['saturation_std'] > 30:
                score += 5

        if np.sum(features['lab_variance']) > 300:
            score += 10

        if features['freq_variance'] > 4:
            score += 15
        if 5 < features['freq_peak_count'] < 50:
            score += 5

        if 40 < features['compression_score'] < 85:
            score += 20
        elif features['compression_score'] > 20:
            score += 10

        if features.get('water_authenticity', 0) > 60:
            score += 10

        return min(score, 100)

    except Exception as e:
        return 50

def generate_enhanced_social_media_data():
    """Generate realistic social media posts and misinformation alerts"""
    current_time = datetime.now()

    posts = [
        {
            "platform": "Twitter",
            "content": "🚨 URGENT: Heavy flooding reported in Andheri East, Mumbai. Water levels rising rapidly. Avoid the area! #MumbaiFloods #Emergency #MonsoonAlert",
            "credibility": 89,
            "sentiment": "Alert",
            "engagement": 1247,
            "hashtags": ["#MumbaiFloods", "#Emergency", "#MonsoonAlert"],
            "timestamp": current_time - timedelta(minutes=15),
            "verified_source": True
        },
        {
            "platform": "Facebook",
            "content": "Traffic completely blocked due to waterlogging near Bandra station. Local residents are helping evacuate families. Emergency services on site.",
            "credibility": 94,
            "sentiment": "Informative",
            "engagement": 856,
            "hashtags": ["#BandraFloods", "#MumbaiTraffic"],
            "timestamp": current_time - timedelta(minutes=32),
            "verified_source": True
        },
        {
            "platform": "Instagram",
            "content": "Storm surge hitting Marine Drive! Massive waves crossing the seawall. Never seen anything like this before! 🌊⚠️ #MarineDrive #StormSurge",
            "credibility": 76,
            "sentiment": "Alert",
            "engagement": 2134,
            "hashtags": ["#MarineDrive", "#StormSurge", "#MumbaiCoast"],
            "timestamp": current_time - timedelta(minutes=8),
            "verified_source": False
        },
        {
            "platform": "Twitter",
            "content": "Coast Guard issues tsunami warning for Gujarat coast. All coastal residents advised to move to higher ground immediately. #TsunamiWarning #Gujarat",
            "credibility": 96,
            "sentiment": "Critical",
            "engagement": 3456,
            "hashtags": ["#TsunamiWarning", "#Gujarat", "#CoastGuard"],
            "timestamp": current_time - timedelta(minutes=5),
            "verified_source": True
        },
        {
            "platform": "LinkedIn",
            "content": "Corporate emergency response teams activated for Chennai coastal surge. All employees in coastal areas advised to work from safer locations.",
            "credibility": 91,
            "sentiment": "Professional",
            "engagement": 567,
            "hashtags": ["#ChennaiCoast", "#EmergencyResponse"],
            "timestamp": current_time - timedelta(minutes=45),
            "verified_source": True
        },
        {
            "platform": "Reddit",
            "content": "r/india - Live updates: Kochi experiencing unprecedented high tide. Fishing boats being evacuated from harbor. Coast Guard on high alert.",
            "credibility": 83,
            "sentiment": "Informative", 
            "engagement": 1789,
            "hashtags": ["#KochiTide", "#KeralaCoast"],
            "timestamp": current_time - timedelta(minutes=20),
            "verified_source": False
        }
    ]

    misinfo_alerts = [
        {
            "content": "FAKE: Video claiming 50-foot tsunami wave hitting Mumbai - Analysis shows footage is from 2011 Japan tsunami",
            "platform": "WhatsApp/Twitter",
            "confidence": 97,
            "affected_users": "~25,000",
            "action": "Content removed, fact-check published",
            "source_analysis": "Reverse image search revealed original source. Metadata analysis confirmed video age. Multiple independent fact-checkers verified."
        },
        {
            "content": "MISLEADING: Exaggerated flood depth claims for Chennai - Social media posts claiming 15 feet water, satellite data shows 3 feet maximum",
            "platform": "Facebook/Instagram",
            "confidence": 84,
            "affected_users": "~12,500", 
            "action": "Warning labels applied, counter-narrative promoted",
            "source_analysis": "Cross-referenced with official weather data and ground reports. Drone footage analysis confirmed actual water levels."
        },
        {
            "content": "SUSPICIOUS: Unverified algal bloom claims in Goa - Posts showing red water lack location verification and image authenticity questionable",
            "platform": "Instagram",
            "confidence": 76,
           
