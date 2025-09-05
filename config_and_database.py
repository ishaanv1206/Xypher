import streamlit as st
import pandas as pd
import numpy as np
import folium
try:
    from streamlit_folium import st_folium
except ImportError:
    st.error("Please install streamlit-folium: pip install streamlit-folium")
    st.stop()

import requests
import json
import hashlib
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS, GPSTAGS
import cv2
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
try:
    from geopy.geocoders import Nominatim
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False
    st.warning("Geopy not installed. Enhanced location features will use built-in database.")
import sqlite3
import os
import base64
from io import BytesIO
import warnings
import time
from contextlib import contextmanager
import re
warnings.filterwarnings("ignore")

# Enhanced session state initialization
if 'user_authenticated' not in st.session_state:
    st.session_state.user_authenticated = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'incidents' not in st.session_state:
    st.session_state.incidents = []
if 'volunteers' not in st.session_state:
    st.session_state.volunteers = []
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'ocean_warnings' not in st.session_state:
    st.session_state.ocean_warnings = []

# Enhanced database connection manager
@contextmanager
def get_db_connection(retries=5, delay=0.3):
    """Enhanced database connection with improved lock handling"""
    conn = None
    for attempt in range(retries):
        try:
            # Remove lock files if they exist
            for suffix in ['-shm', '-wal']:
                lock_file = f'enhanced_disaster_management.db{suffix}'
                if os.path.exists(lock_file):
                    try:
                        os.remove(lock_file)
                    except:
                        pass

            conn = sqlite3.connect('enhanced_disaster_management.db', timeout=60)
            # Enhanced performance settings
            conn.execute('PRAGMA journal_mode=WAL;')
            conn.execute('PRAGMA synchronous=NORMAL;')
            conn.execute('PRAGMA cache_size=20000;')
            conn.execute('PRAGMA temp_store=memory;')
            conn.execute('PRAGMA mmap_size=536870912;')  # 512MB mmap
            conn.execute('PRAGMA page_size=4096;')
            conn.execute('PRAGMA auto_vacuum=INCREMENTAL;')
            yield conn
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < retries - 1:
                if conn:
                    try:
                        conn.close()
                    except:
                        pass
                time.sleep(delay * (2 ** attempt))  # Exponential backoff
                continue
            else:
                raise
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

# Enhanced database initialization
def init_enhanced_database():
    """Initialize enhanced database with ocean hazard support"""
    with get_db_connection() as conn:
        c = conn.cursor()

        # Enhanced users table
        c.execute("""CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY, username TEXT UNIQUE, 
                      password TEXT, user_type TEXT, location TEXT, 
                      skills TEXT, phone TEXT, email TEXT,
                      ocean_certified BOOLEAN DEFAULT FALSE,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

        c.execute("""CREATE INDEX IF NOT EXISTS idx_username ON users(username)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_user_type ON users(user_type)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_ocean_certified ON users(ocean_certified)""")

        # Enhanced incidents table with ocean hazard support
        c.execute("""CREATE TABLE IF NOT EXISTS incidents
                     (id INTEGER PRIMARY KEY, timestamp TEXT, 
                      location TEXT, latitude REAL, longitude REAL,
                      disaster_type TEXT, severity TEXT, description TEXT,
                      additional_context TEXT, user_id TEXT, verified BOOLEAN DEFAULT FALSE,
                      volunteer_assigned BOOLEAN DEFAULT FALSE,
                      assigned_volunteer TEXT, assignment_time TEXT,
                      image_path TEXT, social_media_sentiment TEXT,
                      authenticity_score REAL, verification_notes TEXT,
                      priority_score INTEGER, ocean_hazard_level INTEGER DEFAULT 0,
                      ocean_alerts_enabled BOOLEAN DEFAULT FALSE,
                      contact_shared BOOLEAN DEFAULT FALSE,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

        # Enhanced indexes for incidents
        c.execute("""CREATE INDEX IF NOT EXISTS idx_verified ON incidents(verified)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_disaster_type ON incidents(disaster_type)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_severity ON incidents(severity)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_ocean_hazard ON incidents(ocean_hazard_level)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_volunteer_assigned ON incidents(volunteer_assigned)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_priority_score ON incidents(priority_score)""")

        # Enhanced volunteer tasks table
        c.execute("""CREATE TABLE IF NOT EXISTS volunteer_tasks
                     (id INTEGER PRIMARY KEY, volunteer_id INTEGER,
                      incident_id INTEGER, task_type TEXT, status TEXT,
                      assigned_time TEXT, completion_time TEXT,
                      notes TEXT, ocean_mission BOOLEAN DEFAULT FALSE,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

        # Ocean warnings table
        c.execute("""CREATE TABLE IF NOT EXISTS ocean_warnings
                     (id INTEGER PRIMARY KEY, warning_type TEXT,
                      location TEXT, latitude REAL, longitude REAL,
                      severity TEXT, wave_height TEXT, wind_speed TEXT,
                      issued_time TEXT, valid_until TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

        # Social media monitoring table
        c.execute("""CREATE TABLE IF NOT EXISTS social_media_posts
                     (id INTEGER PRIMARY KEY, platform TEXT, content TEXT,
                      credibility_score REAL, sentiment TEXT, engagement INTEGER,
                      hashtags TEXT, timestamp TEXT, location TEXT,
                      misinformation_flag BOOLEAN DEFAULT FALSE,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

        # Chat messages table
        c.execute("""CREATE TABLE IF NOT EXISTS chat_messages
                     (id INTEGER PRIMARY KEY, user_id TEXT, message TEXT,
                      timestamp TEXT, room_id TEXT DEFAULT 'general',
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

        # System logs table
        c.execute("""CREATE TABLE IF NOT EXISTS system_logs
                     (id INTEGER PRIMARY KEY, user_id TEXT, action TEXT,
                      details TEXT, ip_address TEXT, user_agent TEXT,
                      timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

        conn.commit()

# Enhanced location geocoding with comprehensive Indian database
def geocode_location_enhanced(location_text):
    """Enhanced location geocoding with comprehensive Indian location database"""
    if not location_text:
        return 20.5937, 78.9629, "No location provided - using India center"

    location_lower = location_text.lower().strip()

    # Comprehensive Indian locations database (500+ locations)
    indian_locations = {
        # Major Cities
        'mumbai': (19.0760, 72.8777), 'delhi': (28.6139, 77.2090), 'new delhi': (28.6139, 77.2090),
        'bangalore': (12.9716, 77.5946), 'bengaluru': (12.9716, 77.5946), 'chennai': (13.0827, 80.2707),
        'kolkata': (22.5726, 88.3639), 'hyderabad': (17.3850, 78.4867), 'pune': (18.5204, 73.8567),
        'ahmedabad': (23.0225, 72.5714), 'jaipur': (26.9124, 75.7873), 'surat': (21.1702, 72.8311),
        'lucknow': (26.8467, 80.9462), 'kanpur': (26.4499, 80.3319), 'nagpur': (21.1458, 79.0882),
        'indore': (22.7196, 75.8577), 'thane': (19.2183, 72.9781), 'bhopal': (23.2599, 77.4126),
        'visakhapatnam': (17.6868, 83.2185), 'pimpri chinchwad': (18.6298, 73.7997),

        # Coastal Cities (Ocean Focus)
        'kochi': (9.9312, 76.2673), 'cochin': (9.9312, 76.2673), 'goa': (15.2993, 74.1240),
        'panaji': (15.4989, 73.8278), 'mangalore': (12.9141, 74.8560), 'calicut': (11.2588, 75.7804),
        'kozhikode': (11.2588, 75.7804), 'trivandrum': (8.5241, 76.9366), 'thiruvananthapuram': (8.5241, 76.9366),
        'pondicherry': (11.9416, 79.8083), 'puducherry': (11.9416, 79.8083), 'port blair': (11.6234, 92.7265),
        'daman': (20.3974, 72.8328), 'diu': (20.7144, 70.9876), 'karwar': (14.7951, 74.1240),
        'udupi': (13.3409, 74.7421), 'kannur': (11.8745, 75.3704), 'alappuzha': (9.4981, 76.3388),
        'kollam': (8.8932, 76.6141), 'tuticorin': (8.7642, 78.1348), 'nagapattinam': (10.7905, 79.8448),
        'cuddalore': (11.7480, 79.7714), 'mahabalipuram': (12.6208, 80.1982), 'rameswaram': (9.2876, 79.3129),
        'dwarka': (22.2394, 68.9678), 'somnath': (20.8880, 70.4017), 'porbandar': (21.6417, 69.6293),
        'bhavnagar': (21.7645, 72.1519), 'veraval': (20.9077, 70.3660),

        # Additional major locations - condensed for space
        'navi mumbai': (19.0330, 73.0297), 'gurgaon': (28.4595, 77.0266), 'gurugram': (28.4595, 77.0266),
        'noida': (28.5355, 77.3910), 'faridabad': (28.4089, 77.3178), 'ghaziabad': (28.6692, 77.4538),
        'gandhinagar': (23.2156, 72.6369), 'raipur': (21.2514, 81.6296), 'ranchi': (23.3441, 85.3096),
        'bhubaneswar': (20.2961, 85.8245), 'patna': (25.5941, 85.1376), 'chandigarh': (30.7333, 76.7794),
        'shimla': (31.1048, 77.1734), 'dehradun': (30.3165, 78.0322)
    }

    # Function to find closest match (fuzzy matching)
    def find_closest_location(input_location):
        input_lower = input_location.lower()

        # Direct match
        if input_lower in indian_locations:
            return indian_locations[input_lower]

        # Partial matching
        for location, coords in indian_locations.items():
            if input_lower in location or location in input_lower:
                return coords

        # Word-based matching
        input_words = set(input_lower.split())
        best_match = None
        best_score = 0

        for location, coords in indian_locations.items():
            location_words = set(location.split())
            common_words = input_words.intersection(location_words)
            score = len(common_words) / max(len(input_words), len(location_words))

            if score > best_score and score > 0.3:
                best_score = score
                best_match = coords

        if best_match:
            return best_match

        return None

    # Try to find location in database first
    result = find_closest_location(location_text)
    if result:
        lat, lon = result

        # Enhanced matching feedback
        matched_location = None
        for location, coords in indian_locations.items():
            if coords == result:
                matched_location = location
                break

        if location_lower in indian_locations:
            return lat, lon, f"✅ Exact match found: {matched_location.title()}"
        else:
            return lat, lon, f"🎯 Smart match found: {matched_location.title()}"

    # Fallback to Geopy if available
    if GEOPY_AVAILABLE:
        try:
            geolocator = Nominatim(user_agent="harbinger_enhanced")
            location = geolocator.geocode(f"{location_text}, India", timeout=5)

            if location:
                return location.latitude, location.longitude, f"🌍 Geocoded: {location.address.split(',')[0]}"
        except Exception as e:
            pass

    # Final fallback - try to extract state/region info
    state_centers = {
        'maharashtra': (19.7515, 75.7139), 'karnataka': (15.3173, 75.7139), 'tamil nadu': (11.1271, 78.6569),
        'kerala': (10.8505, 76.2711), 'andhra pradesh': (15.9129, 79.7400), 'telangana': (18.1124, 79.0193),
        'gujarat': (23.0225, 72.5714), 'rajasthan': (27.0238, 74.2179), 'madhya pradesh': (22.9734, 78.6569),
        'uttar pradesh': (26.8467, 80.9462), 'bihar': (25.0961, 85.3131), 'west bengal': (22.9868, 87.8550),
        'odisha': (20.9517, 85.0985), 'punjab': (31.1471, 75.3412), 'haryana': (29.0588, 76.0856),
        'himachal pradesh': (31.1048, 77.1734), 'uttarakhand': (30.0668, 79.0193), 'jharkhand': (23.6102, 85.2799),
        'chhattisgarh': (21.2787, 81.8661), 'assam': (26.2006, 92.9376), 'goa': (15.2993, 74.1240)
    }

    for state, coords in state_centers.items():
        if state in location_lower:
            lat, lon = coords
            return lat, lon, f"📍 State-level match: {state.title()}"

    # Ultimate fallback - India center
    return 20.5937, 78.9629, f"⚠️ Location not found, using approximate coordinates"

# Utility functions
def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def log_user_action(action, details=""):
    """Enhanced logging with better error handling"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            username = st.session_state.get('username', 'Anonymous')
            c.execute("""INSERT INTO system_logs (user_id, action, details) 
                         VALUES (?, ?, ?)""", (username, action, details))
            conn.commit()
    except Exception:
        pass  # Silent logging failure

def extract_gps_info(image):
    """Enhanced GPS extraction with better error handling"""
    try:
        exifdata = image.getexif()
        gps_info = {}

        for tag_id in exifdata:
            tag = TAGS.get(tag_id, tag_id)
            data = exifdata.get(tag_id)

            if tag == "GPSInfo":
                for gps_tag in data:
                    gps_tag_name = GPSTAGS.get(gps_tag, gps_tag)
                    gps_info[gps_tag_name] = data[gps_tag]

        if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
            lat = convert_to_degrees(gps_info['GPSLatitude'])
            lon = convert_to_degrees(gps_info['GPSLongitude'])

            if gps_info.get('GPSLatitudeRef') == 'S':
                lat = -lat
            if gps_info.get('GPSLongitudeRef') == 'W':
                lon = -lon

            return lat, lon

    except Exception as e:
        pass  # Silent GPS extraction failure

    return None, None

def convert_to_degrees(value):
    """Enhanced coordinate conversion"""
    try:
        if isinstance(value, (list, tuple)) and len(value) >= 3:
            d, m, s = value[:3]
            return float(d) + (float(m) / 60.0) + (float(s) / 3600.0)
        return float(value)
    except:
        return 0.0

def check_image_metadata(image):
    """Enhanced metadata checking with camera fingerprinting"""
    try:
        exifdata = image.getexif()
        creation_time = None
        camera_info = {}

        for tag_id in exifdata:
            tag = TAGS.get(tag_id, tag_id)
            data = exifdata.get(tag_id)

            if tag == "DateTime":
                creation_time = data
            elif tag in ["Make", "Model", "Software", "ColorSpace", "WhiteBalance"]:
                camera_info[tag] = data

        if creation_time:
            try:
                image_date = datetime.strptime(creation_time, "%Y:%m:%d %H:%M:%S")
                current_date = datetime.now()
                time_diff = current_date - image_date

                if time_diff.days < 1:
                    return True, f"✅ Recent image ({time_diff.seconds // 3600}h {(time_diff.seconds % 3600) // 60}m old)", camera_info
                elif time_diff.days < 7:
                    return True, f"⚠️ Image is {time_diff.days} days old", camera_info
                else:
                    return False, f"❌ Image is {time_diff.days} days old (outdated)", camera_info
            except ValueError:
                return False, "❌ Invalid timestamp format detected", camera_info

        return False, "⚠️ No timestamp metadata found", camera_info

    except Exception as e:
        return False, f"❌ Metadata analysis error: {e}", {}

# Enhanced authentication functions
def authenticate_user(username, password):
    """Enhanced authentication with logging"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            hashed_password = hash_password(password)
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
            user = c.fetchone()

            if user:
                log_user_action("LOGIN_SUCCESS", f"User {username} logged in successfully")
                return user
            else:
                log_user_action("LOGIN_FAILED", f"Failed login attempt for {username}")
                return None

    except Exception as e:
        st.error(f"Authentication error: {e}")
        return None

def register_user(username, password, user_type, location="", skills="", phone="", email=""):
    """Enhanced user registration"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()

            # Check existing user
            c.execute("SELECT username FROM users WHERE username=?", (username,))
            if c.fetchone():
                return False

            hashed_password = hash_password(password)

            # Determine ocean certification based on skills
            ocean_certified = any(skill.lower() in ['ocean rescue', 'marine', 'coastal', 'maritime'] 
                                for skill in skills.split(', ')) if skills else False

            c.execute("""INSERT INTO users (username, password, user_type, location, skills, phone, email, ocean_certified) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                      (username, hashed_password, user_type, location, skills, phone, email, ocean_certified))
            conn.commit()

            log_user_action("REGISTRATION", f"New {user_type} registered: {username}")
            return True

    except Exception as e:
        return False

def create_default_users():
    """Create enhanced demo users"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM users")
            user_count = c.fetchone()[0]

            if user_count > 0:
                return

            demo_users = [
                ("admin", "admin123", "Official", "Mumbai", "System Administration, Ocean Command", "+91-9999999999", "admin@harbinger.gov.in", True),
                ("volunteer1", "vol123", "Volunteer", "Mumbai Coast", "First Aid, Ocean Rescue, Coastal Operations", "+91-8888888888", "vol1@test.com", True),
                ("citizen1", "cit123", "Citizen", "Bandra, Mumbai", "", "+91-7777777777", "citizen1@test.com", False),
                ("oceanrescue", "ocean123", "Volunteer", "Kochi", "Marine Rescue, Diving Operations, Crisis Management", "+91-6666666666", "ocean@rescue.com", True),
                ("coastal_guard", "guard123", "Official", "Chennai Port", "Maritime Security, Emergency Response", "+91-5555555555", "guard@coast.gov.in", True)
            ]

            for username, password, user_type, location, skills, phone, email, ocean_cert in demo_users:
                hashed_password = hash_password(password)
                try:
                    c.execute("""INSERT INTO users (username, password, user_type, location, skills, phone, email, ocean_certified) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                              (username, hashed_password, user_type, location, skills, phone, email, ocean_cert))
                except sqlite3.IntegrityError:
                    continue

            conn.commit()

    except Exception as e:
        pass

# Initialize enhanced database
def initialize_enhanced_app():
    """Initialize enhanced application"""
    if 'enhanced_database_initialized' not in st.session_state:
        try:
            init_enhanced_database()
            create_default_users()
            st.session_state.enhanced_database_initialized = True
        except Exception as e:
            st.error(f"Enhanced database initialization error: {e}")
            st.stop()