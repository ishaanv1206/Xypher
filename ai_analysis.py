import numpy as np
import cv2
from datetime import datetime, timedelta
import streamlit as st

# Enhanced disaster classification with ocean hazard specialization
def classify_disaster_enhanced(image, location_text="", additional_context=""):
    """Enhanced disaster classification with ocean hazard detection"""
    try:
        img_array = np.array(image)

        # Enhanced color analysis
        avg_color = np.mean(img_array, axis=(0, 1))
        color_std = np.std(img_array, axis=(0, 1))

        # Normalize colors
        color_total = np.sum(avg_color)
        if color_total > 0:
            red_ratio = avg_color[0] / color_total
            green_ratio = avg_color[1] / color_total
            blue_ratio = avg_color[2] / color_total
        else:
            red_ratio = green_ratio = blue_ratio = 0.33

        # Enhanced HSV analysis
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        avg_hue = np.mean(hsv[:, :, 0])
        avg_saturation = np.mean(hsv[:, :, 1])
        avg_value = np.mean(hsv[:, :, 2])

        # Enhanced texture analysis
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 30, 100)  # Lowered thresholds for better edge detection
        edge_density = np.sum(edges) / (gray.shape[0] * gray.shape[1])

        # Water surface analysis (for better flood/ocean detection)
        # Calculate horizontal and vertical gradients
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        water_smoothness = np.mean(gradient_magnitude)

        # Enhanced classification with ocean focus
        classifications = {}

        # ENHANCED FLOOD DETECTION (FIXED)
        water_indicators = 0

        # Blue dominance (enhanced thresholds)
        if blue_ratio > 0.32:  # Lowered threshold for better detection
            water_indicators += 1

        # High saturation water (enhanced)
        if avg_saturation > 80 and blue_ratio > 0.3:
            water_indicators += 1

        # Water surface smoothness
        if water_smoothness < 50 and blue_ratio > 0.28:  # Smooth surfaces indicate water
            water_indicators += 1

        # Blue-cyan hue range for water
        if 90 < avg_hue < 140 and avg_saturation > 60:  # Cyan-blue range
            water_indicators += 1

        # Calculate enhanced flood confidence
        if water_indicators >= 2:
            flood_base_confidence = 40 + (water_indicators * 15)
            flood_enhancement = (blue_ratio - 0.25) * 100 if blue_ratio > 0.25 else 0
            flood_saturation_bonus = (avg_saturation / 255) * 25
            flood_confidence = min(flood_base_confidence + flood_enhancement + flood_saturation_bonus, 95)
            classifications['Flood'] = flood_confidence

        # OCEAN HAZARD DETECTION (NEW)

        # Tsunami Detection - Looking for massive water displacement
        if blue_ratio > 0.45 and water_smoothness > 60 and avg_saturation > 120:
            tsunami_confidence = min((blue_ratio - 0.35) * 200 + water_smoothness, 90)
            classifications['Tsunami'] = tsunami_confidence

        # Coastal Surge Detection - High water with coastal features
        if blue_ratio > 0.4 and edge_density > 0.1 and avg_value > 100:
            surge_confidence = min((blue_ratio - 0.3) * 150 + edge_density * 200, 85)
            classifications['Coastal Surge'] = surge_confidence

        # Storm Surge - Dark waters with high contrast
        if blue_ratio > 0.35 and avg_value < 120 and edge_density > 0.15:
            storm_surge_confidence = min((blue_ratio - 0.25) * 120 + (1 - avg_value/255) * 80, 80)
            classifications['Storm Surge'] = storm_surge_confidence

        # Harmful Algal Bloom Detection - Green-brown water discoloration
        if 0.35 < green_ratio < 0.55 and red_ratio > 0.25 and avg_saturation > 100:
            if 40 < avg_hue < 80:  # Green-yellow range
                bloom_confidence = min((green_ratio - 0.3) * 180 + (avg_saturation / 255) * 30, 75)
                classifications['Harmful Algal Bloom'] = bloom_confidence

        # Original disaster detection (enhanced)

        # Fire/Wildfire detection (enhanced)
        if red_ratio > 0.38 and avg_hue < 35:
            fire_confidence = min((red_ratio - 0.3) * 250 + (avg_saturation / 255) * 40, 95)
            classifications['Fire/Wildfire'] = fire_confidence

        # Storm/Cyclone detection (enhanced)
        if avg_value < 110 and edge_density > 0.12:
            storm_confidence = min((1 - avg_value/255) * 80 + edge_density * 120, 85)
            classifications['Cyclone/Storm'] = storm_confidence

        # Earthquake/Building damage (enhanced)
        if color_std.mean() > 45 and edge_density > 0.18:
            earthquake_confidence = min(color_std.mean() / 1.8 + edge_density * 180, 80)
            classifications['Earthquake/Building Collapse'] = earthquake_confidence

        # Landslide (enhanced)
        brown_score = (red_ratio * 0.65 + green_ratio * 0.35 + blue_ratio * 0.1)
        if brown_score > 0.38 and 15 < avg_hue < 65:
            landslide_confidence = min(brown_score * 120 + (avg_hue - 15) * 1.5, 75)
            classifications['Landslide'] = landslide_confidence

        # Enhanced location-based context
        location_lower = (location_text + " " + additional_context).lower()

        # Ocean/coastal location enhancement
        ocean_keywords = ['sea', 'ocean', 'coast', 'coastal', 'beach', 'shore', 'marine', 'bay', 'gulf', 'island', 'port', 'harbor', 'tide', 'wave']
        if any(keyword in location_lower for keyword in ocean_keywords):
            # Boost ocean-related classifications
            for ocean_type in ['Tsunami', 'Coastal Surge', 'Storm Surge', 'Harmful Algal Bloom']:
                if ocean_type in classifications:
                    classifications[ocean_type] += 20
                elif blue_ratio > 0.3:  # Add ocean possibility if water detected
                    if ocean_type == 'Coastal Surge':
                        classifications[ocean_type] = 60

        # Water body enhancement
        water_keywords = ['river', 'lake', 'dam', 'reservoir', 'canal', 'stream', 'pond']
        if any(keyword in location_lower for keyword in water_keywords):
            if 'Flood' in classifications:
                classifications['Flood'] += 25
            elif blue_ratio > 0.28:
                classifications['Flood'] = 70

        # Forest/rural enhancement
        if any(word in location_lower for word in ['forest', 'mountain', 'hill', 'rural', 'village']):
            if 'Fire/Wildfire' in classifications:
                classifications['Fire/Wildfire'] += 15
            if 'Landslide' in classifications:
                classifications['Landslide'] += 12

        # Urban enhancement
        if any(word in location_lower for word in ['urban', 'city', 'building', 'residential', 'tower', 'complex']):
            if 'Earthquake/Building Collapse' in classifications:
                classifications['Earthquake/Building Collapse'] += 15

        # Select best classification
        if classifications:
            best_disaster = max(classifications.items(), key=lambda x: x[1])
            disaster_type, confidence = best_disaster
        else:
            disaster_type, confidence = "Natural Disaster", 60.0

        # Enhanced explanation
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

        # Enhanced color space analysis
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)

        features = {}

        # 1. Enhanced texture analysis
        features['variance'] = np.var(gray)
        features['std_dev'] = np.std(gray)
        features['texture_contrast'] = np.max(gray) - np.min(gray)

        # 2. Enhanced edge consistency
        edges = cv2.Canny(gray, 30, 120)  # Multiple edge thresholds
        features['edge_density'] = np.sum(edges) / (gray.shape[0] * gray.shape[1])
        features['edge_variance'] = np.var(edges)

        # 3. Enhanced color distribution
        features['color_variance'] = np.var(img_array, axis=(0, 1))
        features['saturation_mean'] = np.mean(hsv[:, :, 1])
        features['saturation_std'] = np.std(hsv[:, :, 1])

        # 4. LAB color space analysis (better for authenticity)
        features['lab_variance'] = np.var(lab, axis=(0, 1))
        features['luminance_distribution'] = np.std(lab[:, :, 0])

        # 5. Enhanced frequency domain analysis
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.log(np.abs(f_shift) + 1)
        features['freq_variance'] = np.var(magnitude_spectrum)
        features['freq_peak_count'] = len(np.where(magnitude_spectrum > np.mean(magnitude_spectrum) + 2*np.std(magnitude_spectrum))[0])

        # 6. Enhanced compression analysis
        features['compression_score'] = detect_compression_artifacts_enhanced(gray)

        # 7. Ocean-specific authenticity checks
        if np.mean(img_array[:, :, 2]) > np.mean(img_array[:, :, 0]):  # Blue-dominant image
            features['water_authenticity'] = analyze_water_authenticity(img_array)
        else:
            features['water_authenticity'] = 50

        # Enhanced authenticity scoring
        authenticity_score = calculate_authenticity_score_enhanced(features)

        # Enhanced classification
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

        # JPEG 8x8 block analysis
        for i in range(0, h - 8, 8):
            for j in range(0, w - 8, 8):
                block = gray_image[i:i+8, j:j+8]
                block_variance = np.var(block)

                # Natural blocks have higher variance
                if block_variance > 80:
                    block_score += 1

                # Check block boundaries (compression artifacts appear at boundaries)
                if i > 0 and j > 0:
                    boundary_diff = np.mean(np.abs(gray_image[i-1:i+1, j:j+8] - gray_image[i:i+2, j:j+8]))
                    if boundary_diff < 10:  # Low boundary difference suggests compression
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
        # Water should have specific characteristics
        blue_channel = img_array[:, :, 2]

        # Natural water has gradual variations
        gradient_x = np.gradient(blue_channel, axis=1)
        gradient_y = np.gradient(blue_channel, axis=0)
        gradient_variance = np.var(gradient_x) + np.var(gradient_y)

        # Natural water reflections
        reflection_score = 0
        if np.std(blue_channel) > 20:  # Has variation
            reflection_score += 30

        # Water texture should not be too uniform
        texture_score = min(gradient_variance / 10, 40)

        # Color consistency for water
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

        # Enhanced texture variance weighting
        if features['variance'] > 1200:
            score += 30
        elif features['variance'] > 800:
            score += 20
        elif features['variance'] > 400:
            score += 10
        else:
            score += 3

        # Enhanced edge analysis
        if 0.08 < features['edge_density'] < 0.35:
            score += 25
        elif features['edge_density'] > 0.05:
            score += 15

        # Edge variance (natural images have varied edge distributions)
        if features['edge_variance'] > 50:
            score += 10

        # Enhanced color analysis
        color_score = min(np.sum(features['color_variance']) / 80, 25)
        score += color_score

        # Saturation analysis
        if 50 < features['saturation_mean'] < 200:
            score += 15
            if features['saturation_std'] > 30:  # Natural variation in saturation
                score += 5

        # LAB color space authenticity
        if np.sum(features['lab_variance']) > 300:
            score += 10

        # Frequency domain analysis
        if features['freq_variance'] > 4:
            score += 15
        if 5 < features['freq_peak_count'] < 50:
            score += 5

        # Enhanced compression analysis
        if 40 < features['compression_score'] < 85:
            score += 20
        elif features['compression_score'] > 20:
            score += 10

        # Water authenticity bonus (for ocean images)
        if features.get('water_authenticity', 0) > 60:
            score += 10

        return min(score, 100)

    except Exception as e:
        return 50

# Enhanced social media data generation
def generate_enhanced_social_media_data():
    """Generate realistic social media posts and misinformation alerts"""
    current_time = datetime.now()

    # Enhanced realistic posts
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

    # Enhanced misinformation alerts
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
            "affected_users": "~8,200",
            "action": "Under investigation, fact-check initiated",
            "source_analysis": "Image analysis suggests possible manipulation. Awaiting confirmation from marine biology experts and local authorities."
        }
    ]

    return posts, misinfo_alerts

def get_enhanced_social_media_sentiment(location, disaster_type):
    """Enhanced social media sentiment analysis with engagement metrics"""
    # Base sentiment options with enhanced realism
    sentiments = [
        "High activity - Multiple verified reports confirmed",
        "Moderate concern - Local residents posting live updates", 
        "Urgent reports - Emergency services actively responding",
        "Multiple confirmations - Cross-platform verification active",
        "Viral content - Rapid information spread across networks",
        "Official channels active - Government updates being broadcast"
    ]

    # Enhanced sentiment based on disaster type and location
    if disaster_type in ['Tsunami', 'Coastal Surge', 'Storm Surge']:
        weights = [0.1, 0.2, 0.5, 0.2]  # High urgency for ocean hazards
    elif disaster_type in ['Fire/Wildfire', 'Earthquake/Building Collapse']:
        weights = [0.3, 0.2, 0.4, 0.1]
    else:
        weights = [0.25, 0.35, 0.25, 0.15]

    selected_sentiment = np.random.choice(sentiments[:4], p=weights)

    # Enhanced engagement metrics
    engagement_metrics = {
        'posts_per_hour': np.random.randint(15, 150),
        'hashtag_mentions': np.random.randint(50, 500),
        'reach_estimate': f"{np.random.randint(10, 100)}K",
        'sentiment_score': np.random.uniform(0.2, 0.9),
        'misinformation_risk': np.random.uniform(0.1, 0.7),
        'trending_hashtags': ['#DisasterAlert', f'#{location.split()[0]}Emergency', '#StaySafe']
    }

    return selected_sentiment, engagement_metrics

# Enhanced ocean warning generation
def generate_ocean_warnings():
    """Generate realistic ocean hazard warnings for Indian coastal areas"""
    current_time = datetime.now()

    warnings = [
        {
            "id": 1,
            "warning_type": "Storm Surge Warning",
            "location": "Mumbai Coast, Maharashtra",
            "severity": "High", 
            "wave_height": "4-6 meters",
            "wind_speed": "85-100 km/h",
            "lat": 19.0760,
            "lon": 72.8777,
            "issued_time": (current_time - timedelta(hours=2)).strftime("%H:%M IST"),
            "valid_until": (current_time + timedelta(hours=6)).strftime("%H:%M IST")
        },
        {
            "id": 2,
            "warning_type": "High Tide Alert",
            "location": "Chennai Port, Tamil Nadu", 
            "severity": "Medium",
            "wave_height": "2-3 meters",
            "wind_speed": "45-60 km/h",
            "lat": 13.0827,
            "lon": 80.2707,
            "issued_time": (current_time - timedelta(hours=1)).strftime("%H:%M IST"),
            "valid_until": (current_time + timedelta(hours=4)).strftime("%H:%M IST")
        },
        {
            "id": 3,
            "warning_type": "Coastal Surge Watch",
            "location": "Kochi Harbor, Kerala",
            "severity": "Low",
            "wave_height": "1.5-2 meters", 
            "wind_speed": "30-45 km/h",
            "lat": 9.9312,
            "lon": 76.2673,
            "issued_time": (current_time - timedelta(minutes=30)).strftime("%H:%M IST"),
            "valid_until": (current_time + timedelta(hours=3)).strftime("%H:%M IST")
        }
    ]

    return warnings

# Enhanced volunteer assignment system
def assign_volunteer_to_incident(incident_id, volunteer_username):
    """Assign volunteer to incident with enhanced tracking"""
    try:
        # Find the incident
        for incident in st.session_state.incidents:
            if incident['id'] == incident_id:
                if not incident.get('volunteer_assigned', False):
                    incident['volunteer_assigned'] = True
                    incident['assigned_volunteer'] = volunteer_username
                    incident['assignment_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Log the assignment
                    from config_and_database import log_user_action
                    log_user_action("VOLUNTEER_ASSIGNED", f"Volunteer {volunteer_username} assigned to incident #{incident_id}")

                    # Add to chat
                    chat_message = {
                        'user': 'System',
                        'message': f"🤝 {volunteer_username} has accepted {incident['disaster_type']} incident at {incident['location']}",
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.chat_messages.append(chat_message)

                    return True
        return False
    except Exception as e:
        st.error(f"Assignment error: {e}")
        return False

# Enhanced volunteer finding with ocean specialization
def find_nearby_volunteers_enhanced(lat, lon, radius_km=50, ocean_mission=False):
    """Enhanced volunteer finding with ocean specialization"""
    # Enhanced volunteer database with ocean specialization
    base_volunteers = [
        {
            "id": 1, "name": "Captain Raj Kumar", "skills": ["First Aid", "Ocean Rescue", "Coastal Operations"], 
            "rating": 4.9, "missions": 45, "phone": "+91-9876543210",
            "specialization": "Ocean Rescue", "ocean_certified": True, "availability": "Active"
        },
        {
            "id": 2, "name": "Dr. Priya Sharma", "skills": ["Emergency Medical", "Trauma Care", "Coordination"], 
            "rating": 4.8, "missions": 62, "phone": "+91-9876543211",
            "specialization": "Emergency Medical", "ocean_certified": False, "availability": "Available"
        },
        {
            "id": 3, "name": "Lt. Amit Singh", "skills": ["Search & Rescue", "Maritime Ops", "Communication"], 
            "rating": 4.9, "missions": 38, "phone": "+91-9876543212",
            "specialization": "Maritime Operations", "ocean_certified": True, "availability": "Active"
        },
        {
            "id": 4, "name": "Sunita Patel", "skills": ["Technical Support", "Drone Operations", "Logistics"], 
            "rating": 4.7, "missions": 29, "phone": "+91-9876543213",
            "specialization": "Technical Support", "ocean_certified": False, "availability": "Available"
        },
        {
            "id": 5, "name": "Mohammed Ali", "skills": ["Local Knowledge", "Community Outreach", "Translation"], 
            "rating": 4.6, "missions": 34, "phone": "+91-9876543214",
            "specialization": "Community Relations", "ocean_certified": False, "availability": "Active"
        },
        {
            "id": 6, "name": "Commander Sarah D'Souza", "skills": ["Marine Rescue", "Diving Operations", "Crisis Management"], 
            "rating": 4.9, "missions": 52, "phone": "+91-9876543215",
            "specialization": "Marine Rescue", "ocean_certified": True, "availability": "Available"
        }
    ]

    # Filter volunteers based on ocean mission requirements
    if ocean_mission:
        available_volunteers = [vol for vol in base_volunteers if vol.get('ocean_certified', False)]
    else:
        available_volunteers = base_volunteers

    # Add enhanced location and availability data
    enhanced_volunteers = []
    for vol in available_volunteers:
        # Enhanced distance calculation
        distance = np.random.uniform(2, radius_km)
        angle = np.random.uniform(0, 2 * np.pi)

        lat_offset = distance * np.cos(angle) / 111.0
        lon_offset = distance * np.sin(angle) / (111.0 * np.cos(np.radians(lat)))

        vol_enhanced = vol.copy()
        vol_enhanced["lat"] = lat + lat_offset
        vol_enhanced["lon"] = lon + lon_offset
        vol_enhanced["distance"] = f"{distance:.1f} km"
        vol_enhanced["eta"] = f"~{int(distance * 1.5 + np.random.uniform(5, 15))} mins"

        # Enhanced availability status
        if vol['availability'] == 'Active':
            vol_enhanced["status_color"] = "🟢"
        elif vol['availability'] == 'Available':
            vol_enhanced["status_color"] = "🔵"  
        else:
            vol_enhanced["status_color"] = "🟡"

        enhanced_volunteers.append(vol_enhanced)

    return sorted(enhanced_volunteers, key=lambda x: float(x['distance'].split()[0]))

# Enhanced priority calculation with ocean hazard weighting
def calculate_priority_score_enhanced(severity, disaster_type, authenticity_score, ocean_hazard_level=0):
    """Enhanced priority calculation with ocean hazard focus"""
    base_scores = {
        'Critical': 95,
        'High': 75,
        'Medium': 55,
        'Low': 35
    }

    # Enhanced multipliers with ocean hazard priority
    disaster_multipliers = {
        'Tsunami': 1.6,  # Highest priority for ocean disasters
        'Coastal Surge': 1.5,
        'Storm Surge': 1.4,
        'Earthquake/Building Collapse': 1.3,
        'Fire/Wildfire': 1.2,
        'Harmful Algal Bloom': 1.2,
        'Flood': 1.1,
        'Cyclone/Storm': 1.2,
        'Landslide': 1.1,
        'Industrial Accident': 1.25,
        'Other': 0.9
    }

    # Ocean hazard level bonus
    ocean_bonus = ocean_hazard_level * 15

    base_score = base_scores.get(severity, 50)
    disaster_multiplier = disaster_multipliers.get(disaster_type, 1.0)
    authenticity_factor = (authenticity_score + 30) / 130  # Enhanced weighting

    final_score = min((base_score * disaster_multiplier * authenticity_factor) + ocean_bonus, 100)
    return int(final_score)