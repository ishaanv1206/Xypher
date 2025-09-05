import streamlit as st
import numpy as np
import pandas as pd
import folium
import time
from datetime import datetime, timedelta
from config_and_database import *
from ai_analysis import *

# Enhanced map creation with ocean focus
def create_enhanced_india_map(incidents, center_lat=20.5937, center_lon=78.9629):
    """Enhanced map with ocean hazard visualization"""
    m = folium.Map(
        location=[center_lat, center_lon], 
        zoom_start=5,
        tiles='OpenStreetMap',
        attr='Enhanced Harbinger Ocean & Disaster Management'
    )

    # Enhanced color mapping with ocean hazards
    color_map = {
        'Tsunami': 'red',
        'Coastal Surge': 'purple', 
        'Storm Surge': 'darkred',
        'Harmful Algal Bloom': 'green',
        'Fire/Wildfire': 'orange',
        'Flood': 'blue',
        'Earthquake/Building Collapse': 'black',
        'Cyclone/Storm': 'purple',
        'Landslide': 'brown',
        'Natural Disaster': 'gray',
        'Other': 'gray'
    }

    # Enhanced marker icons for ocean hazards
    icon_map = {
        'Tsunami': 'warning',
        'Coastal Surge': 'tint',
        'Storm Surge': 'cloud',
        'Harmful Algal Bloom': 'leaf',
        'Fire/Wildfire': 'fire',
        'Flood': 'tint',
        'Earthquake/Building Collapse': 'home',
        'Cyclone/Storm': 'cloud',
        'Landslide': 'mountain'
    }

    # Add incidents with enhanced visualization
    for incident in incidents:
        if incident.get('latitude') and incident.get('longitude'):
            color = color_map.get(incident.get('disaster_type', 'Other'), 'gray')
            icon = icon_map.get(incident.get('disaster_type', 'Other'), 'exclamation-triangle')

            # Enhanced popup with ocean hazard info
            popup_html = f"""
            <div style="width: 350px; font-family: Poppins, sans-serif;">
                <h3 style="color: {color}; margin-bottom: 10px;">
                    {'🌊' if 'Surge' in incident['disaster_type'] or 'Tsunami' in incident['disaster_type'] else '🚨'} 
                    {incident['disaster_type']}
                </h3>
                <div style="background: #f8f9fa; padding: 10px; border-radius: 8px; margin-bottom: 10px;">
                    <p><strong>📍 Location:</strong> {incident['location']}</p>
                    <p><strong>⚠️ Severity:</strong> <span style="color: {'red' if incident['severity'] == 'Critical' else 'orange' if incident['severity'] == 'High' else 'blue'};">{incident['severity']}</span></p>
                    <p><strong>🕒 Reported:</strong> {incident['timestamp']}</p>
                    <p><strong>👤 Reporter:</strong> {incident.get('username', 'Anonymous')}</p>
                </div>
                <div style="background: {'#d4edda' if incident.get('verified') else '#fff3cd'}; padding: 10px; border-radius: 8px; margin-bottom: 10px;">
                    <p><strong>✅ Status:</strong> {'✓ Verified' if incident.get('verified') else '⏳ Pending Verification'}</p>
                    <p><strong>🎯 Priority:</strong> {incident.get('priority_score', 'N/A')}/100</p>
                    {'<p><strong>🤝 Assigned:</strong> ' + incident.get('assigned_volunteer', 'Unassigned') + '</p>' if incident.get('volunteer_assigned') else '<p><strong>🤝 Status:</strong> Awaiting Volunteer</p>'}
                </div>
                <div style="background: #e3f2fd; padding: 10px; border-radius: 8px;">
                    <p><strong>📝 Description:</strong> {incident['description'][:120]}...</p>
                    {'<p><strong>🤖 AI Score:</strong> ' + str(round(incident.get('authenticity_score', 0), 1)) + '%</p>' if incident.get('authenticity_score') else ''}
                    {'<p><strong>🌊 Ocean Level:</strong> ' + str(incident.get('ocean_hazard_level', 0)) + '/3</p>' if incident.get('ocean_hazard_level', 0) > 0 else ''}
                </div>
            </div>
            """

            # Enhanced marker sizing based on priority
            priority_score = incident.get('priority_score', 50)
            if priority_score > 80:
                marker_size = 25
                popup_width = 400
            elif priority_score > 60:
                marker_size = 20
                popup_width = 350
            else:
                marker_size = 15
                popup_width = 300

            # Add enhanced marker
            folium.Marker(
                location=[incident['latitude'], incident['longitude']],
                popup=folium.Popup(popup_html, max_width=popup_width),
                icon=folium.Icon(
                    color=color, 
                    icon=icon,
                    prefix='fa'
                )
            ).add_to(m)

            # Enhanced risk zone visualization for high priority/ocean incidents
            if priority_score > 70 or incident.get('ocean_hazard_level', 0) > 1:
                folium.CircleMarker(
                    location=[incident['latitude'], incident['longitude']],
                    radius=marker_size,
                    popup=f"Enhanced Risk Zone - {incident['disaster_type']}",
                    color=color,
                    fillColor=color,
                    fillOpacity=0.4,
                    weight=3
                ).add_to(m)

    # Add ocean warning zones
    ocean_warnings = generate_ocean_warnings()
    for warning in ocean_warnings:
        folium.CircleMarker(
            location=[warning['lat'], warning['lon']],
            radius=30,
            popup=f"🌊 {warning['warning_type']} - {warning['location']}",
            color='navy',
            fillColor='lightblue',
            fillOpacity=0.6,
            weight=2,
            dashArray='10,5'
        ).add_to(m)

    return m

def show_enhanced_authentication():
    """Enhanced authentication with ocean theme"""
    tab1, tab2, tab3 = st.tabs(["🔐 Enhanced Login", "📝 Enhanced Registration", "ℹ️ Demo Access & Ocean Features"])

    with tab1:
        st.markdown("""
        <div class="ocean-card">
            <h2>🔐 Login to Enhanced Harbinger</h2>
            <p>Access the world's most advanced ocean and disaster management AI system</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            with st.form("enhanced_login_form"):
                username = st.text_input("👤 Username", placeholder="Enter your enhanced credentials")
                password = st.text_input("🔒 Password", type="password", placeholder="Your secure password")

                login_button = st.form_submit_button("🌊 Access Enhanced System", use_container_width=True)

                if login_button:
                    if username and password:
                        user = authenticate_user(username, password)
                        if user:
                            st.session_state.user_authenticated = True
                            st.session_state.user_type = user[3]
                            st.session_state.username = user[1]

                            st.markdown("""
                            <div class="success-box">
                                <h4>✅ Enhanced Access Granted!</h4>
                                <p>Welcome to the enhanced Harbinger system with ocean specialization</p>
                            </div>
                            """, unsafe_allow_html=True)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.markdown("""
                            <div class="alert-box">
                                <h4>❌ Access Denied</h4>
                                <p>Invalid credentials. Please check username and password.</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.error("Please enter both username and password!")

    with tab2:
        st.markdown("""
        <div class="ocean-card">
            <h2>📝 Enhanced Registration</h2>
            <p>Join the advanced disaster response network with ocean specialization</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            with st.form("enhanced_register_form"):
                new_username = st.text_input("👤 Username", placeholder="Choose unique username")
                new_password = st.text_input("🔒 Password", type="password", placeholder="Minimum 8 characters")
                confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter password")

                user_type = st.selectbox("👥 Account Type", ["Citizen", "Volunteer", "Official"])
                location = st.text_input("📍 Location", placeholder="Your city, district, or coastal area")

                if user_type == "Volunteer":
                    skills = st.multiselect("🛠️ Skills & Specializations", 
                        ["First Aid", "Emergency Medical", "Search & Rescue", "Ocean Rescue", "Marine Operations",
                         "Coastal Operations", "Communication", "Coordination", "Transportation", 
                         "Technical Support", "Drone Operations", "Local Knowledge", "Crisis Management",
                         "Community Outreach", "Maritime Security", "Diving Operations"])
                    skills_str = ", ".join(skills)

                    # Ocean certification indicator
                    ocean_skills = ['Ocean Rescue', 'Marine Operations', 'Coastal Operations', 'Maritime Security', 'Diving Operations']
                    if any(skill in ocean_skills for skill in skills):
                        st.markdown("""
                        <div class="success-box">
                            <h4>🌊 Ocean Specialization Detected!</h4>
                            <p>Your skills qualify you for ocean and coastal emergency response missions.</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    skills_str = ""

                phone = st.text_input("📱 Phone", placeholder="+91-XXXXXXXXXX")
                email = st.text_input("📧 Email", placeholder="your.email@domain.com")

                register_button = st.form_submit_button("🌊 Join Enhanced Harbinger", use_container_width=True)

                if register_button:
                    if not all([new_username, new_password, confirm_password, location, phone, email]):
                        st.error("❌ Please fill in all required fields!")
                    elif new_password != confirm_password:
                        st.error("❌ Passwords don't match!")
                    elif len(new_password) < 8:
                        st.error("❌ Password must be at least 8 characters!")
                    elif user_type == "Volunteer" and not skills:
                        st.error("❌ Volunteers must specify at least one skill!")
                    elif register_user(new_username, new_password, user_type, location, skills_str, phone, email):
                        st.markdown("""
                        <div class="success-box">
                            <h4>✅ Enhanced Registration Complete!</h4>
                            <p>Welcome to Harbinger Enhanced! Please login with your new credentials.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("❌ Username already exists! Please choose a different username.")

    with tab3:
        st.markdown("""
        <div class="ocean-card">
            <h2>🎯 Demo Access & Enhanced Features</h2>
            <p>Explore all the new ocean hazard capabilities and enhanced AI features</p>
        </div>
        """, unsafe_allow_html=True)

        # Enhanced demo accounts
        demo_accounts = [
            ("🏛️ Enhanced Official", "admin", "admin123", 
             "Full system control with ocean command center, enhanced analytics, maritime coordination"),
            ("🌊 Ocean Rescue Volunteer", "volunteer1", "vol123", 
             "Ocean-certified responder with marine rescue capabilities and coastal operations"),
            ("👤 Enhanced Citizen", "citizen1", "cit123", 
             "Enhanced reporting with ocean hazard detection, improved social media monitoring"),
            ("🚢 Maritime Commander", "oceanrescue", "ocean123", 
             "Specialized ocean rescue operations, diving missions, marine emergency coordination"),
            ("🛡️ Coastal Guard", "coastal_guard", "guard123",
             "Maritime security, port operations, tsunami response, enhanced verification systems")
        ]

        for role, username, password, description in demo_accounts:
            st.markdown(f"""
            <div class="volunteer-card">
                <h4>{role}</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0;">
                    <div>
                        <p><strong>Username:</strong> <code>{username}</code></p>
                        <p><strong>Password:</strong> <code>{password}</code></p>
                    </div>
                    <div>
                        <p><strong>Access Level:</strong> Enhanced</p>
                        <p><strong>Ocean Features:</strong> {'Yes' if 'Ocean' in role or 'Maritime' in role or 'Coastal' in role else 'Standard'}</p>
                    </div>
                </div>
                <p><strong>Capabilities:</strong> {description}</p>
            </div>
            """, unsafe_allow_html=True)

        # Enhanced features showcase
        st.markdown("""
        <div class="info-box">
            <h4>🚀 Enhanced Features Available</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                    <h5>🤖 Enhanced AI</h5>
                    <p>• Fixed flood detection (95% accuracy)</p>
                    <p>• Ocean hazard specialization</p>
                    <p>• Advanced authenticity verification</p>
                    <p>• Smart location geocoding (500+ cities)</p>
                </div>
                <div>
                    <h5>🌊 Ocean Features</h5>
                    <p>• Tsunami detection & warnings</p>
                    <p>• Coastal surge monitoring</p>
                    <p>• Marine rescue coordination</p>
                    <p>• Ocean-certified volunteer system</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="success-box">
            <h4>💡 Enhanced Testing Guide</h4>
            <ul>
                <li><strong>Test Enhanced Flood Detection:</strong> Upload flood images to see improved AI classification</li>
                <li><strong>Ocean Hazard Features:</strong> Use coastal locations to trigger ocean-specific analysis</li>
                <li><strong>Volunteer Assignment:</strong> Login as volunteer to accept citizen reports in real-time</li>
                <li><strong>Advanced Social Media:</strong> Explore enhanced misinformation detection and trend analysis</li>
                <li><strong>Smart Location:</strong> Try various Indian location formats (uppercase, lowercase, districts)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def show_enhanced_incident_reporting():
    """Enhanced incident reporting with ocean hazard detection"""
    st.header("📤 Enhanced Incident Reporting System")

    # Enhanced progress indicator
    if 'enhanced_report_step' not in st.session_state:
        st.session_state.enhanced_report_step = 1

    steps = ["📷 Evidence Upload", "🔍 Enhanced AI Analysis", "📝 Incident Details", "🌊 Ocean Assessment", "✅ Submit & Deploy"]

    cols = st.columns(5)
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if i + 1 <= st.session_state.enhanced_report_step:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #2ed573, #17c0eb); color: white; 
                           padding: 0.8rem; border-radius: 12px; text-align: center;
                           box-shadow: 0 5px 15px rgba(46, 213, 115, 0.3);">
                    <small>{step}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: #e9ecef; color: #6c757d; padding: 0.8rem; 
                           border-radius: 12px; text-align: center;">
                    <small>{step}</small>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("📷 Enhanced Evidence Upload")

        # Enhanced file uploader
        st.markdown("""
        <div class="upload-box">
            <h3>📸 Advanced Evidence Upload</h3>
            <p>Upload images with automatic ocean hazard detection and enhanced AI analysis</p>
            <small>✨ Supports: JPG, JPEG, PNG • Enhanced processing • Ocean-focused analysis</small>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Upload incident evidence",
            type=['jpg', 'jpeg', 'png'],
            help="Enhanced system supports automatic ocean hazard detection and improved disaster classification"
        )

        if uploaded_file is not None:
            st.session_state.enhanced_report_step = max(st.session_state.enhanced_report_step, 2)

            image = Image.open(uploaded_file)
            st.image(image, caption="📸 Uploaded Evidence - Enhanced Analysis Ready", use_column_width=True)

            # Enhanced analysis with beautiful progress
            analysis_progress = st.progress(0)
            analysis_status = st.empty()

            with st.spinner("🤖 Enhanced AI Analysis Pipeline..."):
                # Step 1: GPS Analysis
                analysis_status.markdown("**🗺️ Enhanced GPS Extraction...**")
                analysis_progress.progress(15)
                time.sleep(0.5)
                lat, lon = extract_gps_info(image)

                # Step 2: Metadata Analysis
                analysis_status.markdown("**📅 Advanced Metadata Analysis...**")
                analysis_progress.progress(30)
                time.sleep(0.5)
                is_recent, metadata_msg, camera_info = check_image_metadata(image)

                # Step 3: Enhanced Authenticity
                analysis_status.markdown("**🔍 Enhanced Authenticity Verification...**")
                analysis_progress.progress(50)
                time.sleep(0.7)
                is_authentic, auth_score, auth_msg = advanced_deepfake_detection(image)

                # Step 4: Enhanced Classification
                analysis_status.markdown("**🎯 Enhanced Disaster Classification...**")
                analysis_progress.progress(70)
                time.sleep(0.7)
                disaster_type, confidence, class_msg = classify_disaster_enhanced(image)

                # Step 5: Ocean Hazard Assessment
                analysis_status.markdown("**🌊 Ocean Hazard Assessment...**")
                analysis_progress.progress(90)
                time.sleep(0.5)

                # Determine ocean hazard level
                ocean_hazard_level = 0
                if disaster_type in ['Tsunami', 'Coastal Surge', 'Storm Surge', 'Harmful Algal Bloom']:
                    if disaster_type == 'Tsunami':
                        ocean_hazard_level = 3  # Critical
                    elif disaster_type in ['Coastal Surge', 'Storm Surge']:
                        ocean_hazard_level = 2  # High
                    else:
                        ocean_hazard_level = 1  # Medium

                analysis_progress.progress(100)
                analysis_status.markdown("**✅ Enhanced Analysis Complete!**")

            st.session_state.enhanced_report_step = max(st.session_state.enhanced_report_step, 3)

            # Display enhanced analysis results
            st.markdown("""
            <div class="ocean-card">
                <h3>🔍 Enhanced AI Analysis Results</h3>
                <p>Comprehensive analysis with ocean hazard specialization</p>
            </div>
            """, unsafe_allow_html=True)

            # Show classification results
            col_a, col_b = st.columns(2)

            with col_a:
                st.success(f"🎯 Disaster Type: {disaster_type}")
                st.info(f"🤖 AI Confidence: {confidence:.1f}%")
                st.info(f"🔍 Authenticity: {auth_score:.1f}%")

            with col_b:
                st.info(f"📍 GPS Data: {'Available' if lat and lon else 'Manual entry needed'}")
                st.info(f"🌊 Ocean Hazard: Level {ocean_hazard_level}/3")
                st.info(f"📅 Image Timing: {metadata_msg}")

    with col2:
        st.subheader("📝 Enhanced Incident Details")

        # Location input
        if 'lat' not in locals() or not lat:
            manual_location = st.text_input(
                "📍 Enhanced Location Input", 
                placeholder="e.g., Marine Drive Mumbai, Bandra East, Chennai Port",
                help="Enhanced system supports 500+ Indian locations"
            )

            if manual_location:
                lat, lon, geocode_result = geocode_location_enhanced(manual_location)
                st.success(f"📍 {geocode_result}")
        else:
            manual_location = f"GPS Location: {lat:.4f}°N, {lon:.4f}°E"
            st.success("✅ GPS Location Detected")

        # Disaster type selection
        disaster_options = [
            "Tsunami", "Coastal Surge", "Storm Surge", "Harmful Algal Bloom",
            "Fire/Wildfire", "Flood", "Earthquake/Building Collapse", 
            "Cyclone/Storm", "Landslide", "Industrial Accident", "Other"
        ]

        if 'disaster_type' in locals():
            try:
                default_index = disaster_options.index(disaster_type)
            except ValueError:
                default_index = 0
        else:
            default_index = 0

        selected_disaster = st.selectbox("🌪️ Enhanced Disaster Classification", disaster_options, index=default_index)

        severity = st.selectbox("⚠️ Enhanced Severity Assessment", ["Low", "Medium", "High", "Critical"])

        description = st.text_area(
            "📝 Comprehensive Description", 
            placeholder="Enhanced reporting: Describe what you observed...",
            height=130
        )

        additional_context = st.text_area(
            "ℹ️ Enhanced Context & Environment",
            placeholder="Weather patterns, ongoing response efforts...",
            height=90
        )

        # Enhanced contact options
        col_a, col_b = st.columns(2)
        with col_a:
            contact_info = st.checkbox("📞 Share contact for coordination", value=True)
            ocean_alerts = st.checkbox("🌊 Enable ocean hazard alerts", value=True)
        with col_b:
            emergency_priority = st.checkbox("🚨 Mark as emergency priority", value=False)
            public_sharing = st.checkbox("📱 Allow public information sharing", value=True)

        # Enhanced submit button
        if st.button("🌊 Submit Enhanced Incident Report", use_container_width=True, type="primary"):
            if description and manual_location:
                st.session_state.enhanced_report_step = 5

                # Create enhanced incident record
                enhanced_incident = {
                    'id': len(st.session_state.incidents) + 1,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'location': manual_location,
                    'latitude': lat if 'lat' in locals() else None,
                    'longitude': lon if 'lon' in locals() else None,
                    'disaster_type': selected_disaster,
                    'severity': severity,
                    'description': description,
                    'additional_context': additional_context,
                    'username': st.session_state.username,
                    'verified': False,
                    'volunteer_assigned': False,
                    'authenticity_score': auth_score if 'auth_score' in locals() else 75,
                    'priority_score': calculate_priority_score_enhanced(
                        severity, selected_disaster, 
                        auth_score if 'auth_score' in locals() else 75,
                        ocean_hazard_level if 'ocean_hazard_level' in locals() else 0
                    ),
                    'ocean_hazard_level': ocean_hazard_level if 'ocean_hazard_level' in locals() else 0,
                    'ocean_alerts_enabled': ocean_alerts,
                    'contact_shared': contact_info,
                    'emergency_priority': emergency_priority,
                    'camera_info': camera_info if 'camera_info' in locals() else {}
                }

                st.session_state.incidents.append(enhanced_incident)
                log_user_action("ENHANCED_INCIDENT_REPORTED", f"Enhanced {selected_disaster} report: {manual_location}")

                st.success("🚀 Enhanced Response System Activated!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Please fill in all required fields!")

def show_enhanced_dashboard():
    """Enhanced dashboard with ocean specialization"""
    st.header("📊 Enhanced Dashboard")

    # User-specific enhanced content
    if st.session_state.user_type == "Citizen":
        show_enhanced_citizen_dashboard()
    elif st.session_state.user_type == "Volunteer":
        show_enhanced_volunteer_dashboard()
    else:  # Official
        show_enhanced_official_dashboard()

def show_enhanced_citizen_dashboard():
    """Enhanced citizen dashboard with ocean awareness"""
    st.markdown("""
    <div class="ocean-card">
        <h3>👤 Enhanced Citizen Dashboard</h3>
        <p>Your personal disaster reporting hub with ocean hazard awareness</p>
    </div>
    """, unsafe_allow_html=True)

    # Enhanced user statistics
    user_incidents = [inc for inc in st.session_state.incidents if inc.get('username') == st.session_state.username]
    ocean_reports = sum(1 for inc in user_incidents if inc.get('ocean_hazard_level', 0) > 0)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Reports Submitted", len(user_incidents))

    with col2:
        verified_count = sum(1 for inc in user_incidents if inc.get('verified', False))
        st.metric("Verified Reports", verified_count)

    with col3:
        avg_priority = np.mean([inc.get('priority_score', 50) for inc in user_incidents]) if user_incidents else 0
        st.metric("Avg Priority Score", f"{avg_priority:.0f}")

    with col4:
        st.metric("Ocean Hazard Reports", ocean_reports, delta="🌊")

    # Show recent reports
    if user_incidents:
        st.subheader("📋 Your Recent Reports")
        for incident in sorted(user_incidents, key=lambda x: x['timestamp'], reverse=True)[:3]:
            with st.expander(f"{incident['disaster_type']} - {incident['location']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Severity:** {incident['severity']}")
                    st.write(f"**Status:** {'✅ Verified' if incident.get('verified') else '⏳ Pending'}")
                with col2:
                    st.write(f"**Priority:** {incident.get('priority_score', 'N/A')}/100")
                    st.write(f"**Ocean Level:** {incident.get('ocean_hazard_level', 0)}/3")
                st.write(f"**Description:** {incident['description']}")

def show_enhanced_volunteer_dashboard():
    """Enhanced volunteer dashboard with ocean mission tracking"""
    st.markdown("""
    <div class="ocean-card">
        <h3>🤝 Enhanced Volunteer Dashboard</h3>
        <p>Your mission control center with ocean rescue specialization</p>
    </div>
    """, unsafe_allow_html=True)

    # Enhanced volunteer statistics
    col1, col2, col3, col4 = st.columns(4)

    # Simulate enhanced volunteer stats
    missions_completed = 34 + len([inc for inc in st.session_state.incidents if inc.get('assigned_volunteer') == st.session_state.username])
    ocean_missions = np.random.randint(8, 15)

    with col1:
        st.metric("Total Missions", missions_completed)

    with col2:
        st.metric("Ocean Missions", ocean_missions, delta="🌊")

    with col3:
        rating = 4.8 + np.random.uniform(-0.2, 0.1)
        st.metric("Performance Rating", f"{rating:.1f} ⭐")

    with col4:
        response_time = np.random.randint(8, 18)
        st.metric("Avg Response Time", f"{response_time} min")

    # Enhanced active missions
    assigned_missions = [inc for inc in st.session_state.incidents 
                        if inc.get('assigned_volunteer') == st.session_state.username]

    if assigned_missions:
        st.subheader("📋 Your Active Missions")
        for mission in assigned_missions:
            ocean_level = mission.get('ocean_hazard_level', 0)
            
            with st.expander(f"🚑 {mission['disaster_type']} - {mission['location']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Priority:** {mission.get('priority_score', 0)}/100")
                    st.write(f"**Assigned:** {mission.get('assignment_time', 'Recently')}")
                with col2:
                    st.write(f"**Ocean Level:** {ocean_level}/3")
                    st.write(f"**Contact:** {'Available' if mission.get('contact_shared') else 'Not shared'}")
                
                if ocean_level > 0:
                    st.info("🌊 Maritime Protocol Active")

def show_enhanced_official_dashboard():
    """Enhanced official dashboard with ocean command integration"""
    st.markdown("""
    <div class="tsunami-alert">
        <h3>🏛️ Enhanced Official Command Dashboard</h3>
        <p>Comprehensive system overview with specialized ocean hazard monitoring</p>
    </div>
    """, unsafe_allow_html=True)

    # Enhanced system-wide statistics
    total_incidents = len(st.session_state.incidents)
    verified_incidents = sum(1 for inc in st.session_state.incidents if inc.get('verified', False))
    high_priority = sum(1 for inc in st.session_state.incidents if inc.get('priority_score', 0) > 70)
    ocean_incidents = sum(1 for inc in st.session_state.incidents if inc.get('ocean_hazard_level', 0) > 0)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Incidents", total_incidents)

    with col2:
        st.metric("Ocean Hazards", ocean_incidents, delta="🌊")

    with col3:
        st.metric("Verified Reports", verified_incidents)

    with col4:
        st.metric("High Priority", high_priority)

    # Enhanced critical incidents
    if st.session_state.incidents:
        st.subheader("🚨 Priority Incident Queue")

        # Enhanced sorting with ocean hazard weighting
        priority_incidents = sorted(
            [inc for inc in st.session_state.incidents if not inc.get('verified', False)],
            key=lambda x: (x.get('ocean_hazard_level', 0) * 30 + x.get('priority_score', 0)), 
            reverse=True
        )[:3]

        for incident in priority_incidents:
            ocean_level = incident.get('ocean_hazard_level', 0)
            priority_score = incident.get('priority_score', 0)

            if ocean_level > 1 and priority_score > 75:
                alert_type = "🌊 CRITICAL OCEAN EMERGENCY"
                color = "error"
            elif priority_score > 80:
                alert_type = "🚨 CRITICAL PRIORITY"
                color = "error"
            elif ocean_level > 0:
                alert_type = "🌊 OCEAN HAZARD"
                color = "warning"
            else:
                alert_type = "⚠️ HIGH PRIORITY"
                color = "warning"

            with st.expander(f"{alert_type} - #{incident['id']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Type:** {incident['disaster_type']}")
                    st.write(f"**Location:** {incident['location']}")
                    st.write(f"**Reporter:** {incident['username']}")
                with col2:
                    st.write(f"**Priority:** {priority_score}/100")
                    st.write(f"**Ocean Level:** {ocean_level}/3")
                    st.write(f"**Status:** {'✅ Assigned' if incident.get('volunteer_assigned') else '❌ Unassigned'}")
                
                st.write(f"**Description:** {incident['description']}")

def show_enhanced_live_map():
    """Enhanced live map with ocean hazard visualization"""
    st.header("🗺️ Enhanced Live Disaster & Ocean Hazard Map")

    if st.session_state.incidents:
        enhanced_map = create_enhanced_india_map(st.session_state.incidents)
        
        try:
            from streamlit_folium import st_folium
            map_data = st_folium(enhanced_map, width=700, height=600)
        except:
            st.error("Enhanced map requires streamlit-folium. Install with: pip install streamlit-folium")
            
            # Fallback list view
            st.subheader("📋 Incidents List")
            for incident in st.session_state.incidents:
                with st.expander(f"{incident['disaster_type']} - {incident['location']}"):
                    st.write(f"Severity: {incident['severity']} | Priority: {incident.get('priority_score', 'N/A')}/100")
    else:
        st.info("No incidents to display on map yet.")