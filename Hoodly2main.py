
import streamlit as st
import folium
from streamlit_folium import st_folium
import networkx as nx
import osmnx as ox
from geopy.distance import geodesic
from streamlit.components.v1 import html
import anthropic
import json
import time
from datetime import datetime

# --- Custom Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #f9fbfc;
        font-family: 'Segoe UI', sans-serif;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        color: white;
        background: #3A7CA5;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background: #2A5A7A;
        transform: translateY(-2px);
    }
    .ai-route-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    .safety-high { color: #28a745; font-weight: bold; }
    .safety-medium { color: #ffc107; font-weight: bold; }
    .safety-low { color: #dc3545; font-weight: bold; }
    .ai-thinking {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
    }
    </style>
""", unsafe_allow_html=True)

# --- Enhanced Berkeley Locations with More Detailed Safety Data ---
locations = {
    "UC Berkeley": (37.8719, -122.2585),
    "Downtown Berkeley BART": (37.8691, -122.2679),
    "Berkeley Marina": (37.8656, -122.3131),
    "North Berkeley BART": (37.8739, -122.2835),
    "Ashby BART": (37.8529, -122.2708),
    "Berkeley Bowl": (37.8563, -122.2731),
    "Fourth Street": (37.8710, -122.3006),
    "Claremont Hotel": (37.8594, -122.2395),
    "Berkeley Art Museum": (37.8703, -122.2602),
    "Berkeley High School": (37.8699, -122.2721),
    "Lawrence Hall of Science": (37.8816, -122.2469),
    "Gourmet Ghetto": (37.8796, -122.2680),
    "Tilden Park Entrance": (37.8955, -122.2592),
    "Shattuck Avenue": (37.8715, -122.2687),
    "Telegraph Avenue": (37.8652, -122.2583),
    "People's Park": (37.8659, -122.2580),
    "César E. Chávez Student Center": (37.8697, -122.2594),
    "Sproul Plaza": (37.8693, -122.2590),
    "RSF (Recreational Sports Facility)": (37.8676, -122.2604),
    "Memorial Stadium": (37.8710, -122.2505),
    "Greek Theatre": (37.8730, -122.2500),
    "Doe Library": (37.8721, -122.2594),
    "Haas Pavilion": (37.8683, -122.2634),
    "Cal Dining Crossroads": (37.8671, -122.2607),
    "Berkeley City College": (37.8694, -122.2665),
    "Elmwood District": (37.8599, -122.2534),
    "Alta Bates Hospital": (37.8567, -122.2567),
    "Hearst Mining Circle": (37.8734, -122.2570),
    "Berkeley Rose Garden": (37.8793, -122.2665)
}

safety_scores = {
    "UC Berkeley": 8,
    "Downtown Berkeley BART": 5,
    "Berkeley Marina": 6,
    "North Berkeley BART": 6,
    "Ashby BART": 4,
    "Berkeley Bowl": 6,
    "Fourth Street": 7,
    "Claremont Hotel": 9,
    "Berkeley Art Museum": 8,
    "Berkeley High School": 6,
    "Lawrence Hall of Science": 9,
    "Gourmet Ghetto": 7,
    "Tilden Park Entrance": 8,
    "Shattuck Avenue": 6,
    "Telegraph Avenue": 5,
    "People's Park": 3,
    "César E. Chávez Student Center": 8,
    "Sproul Plaza": 8,
    "RSF (Recreational Sports Facility)": 7,
    "Memorial Stadium": 8,
    "Greek Theatre": 8,
    "Doe Library": 9,
    "Haas Pavilion": 8,
    "Cal Dining Crossroads": 7,
    "Berkeley City College": 6,
    "Elmwood District": 8,
    "Alta Bates Hospital": 8,
    "Hearst Mining Circle": 9,
    "Berkeley Rose Garden": 8
}

# Enhanced neighborhood safety data for AI analysis
neighborhood_context = {
    "Downtown Berkeley": {"crime_level": "medium", "lighting": "good", "foot_traffic": "high", "time_considerations": "avoid late night"},
    "Telegraph Avenue": {"crime_level": "medium-high", "lighting": "fair", "foot_traffic": "high", "time_considerations": "daytime preferred"},
    "People's Park": {"crime_level": "high", "lighting": "poor", "foot_traffic": "variable", "time_considerations": "avoid after dark"},
    "UC Campus": {"crime_level": "low", "lighting": "excellent", "foot_traffic": "high", "time_considerations": "generally safe"},
    "North Berkeley": {"crime_level": "low", "lighting": "good", "foot_traffic": "medium", "time_considerations": "residential safe"},
    "Elmwood District": {"crime_level": "low", "lighting": "good", "foot_traffic": "medium", "time_considerations": "family-friendly"},
    "Berkeley Hills": {"crime_level": "very low", "lighting": "variable", "foot_traffic": "low", "time_considerations": "well-lit areas preferred"},
    "West Berkeley": {"crime_level": "medium", "lighting": "fair", "foot_traffic": "low", "time_considerations": "industrial area, daytime preferred"},
}

st.title("🥷 Hoodly: AI-Powered Safe Walking in Berkeley")
st.markdown("""
    <h5 style='color: #4d4d4d;'>Powered by Anthropic AI for smarter, safer route planning.
    Get personalized safety recommendations and alternative routes beyond what Google Maps offers.</h5>
""", unsafe_allow_html=True)

# API Key Input
st.sidebar.header("🔑 AI Configuration")
api_key = st.sidebar.text_input("Enter your Anthropic API Key", type="password", help="Your API key is used only for this session and not stored.")

if not api_key:
    st.sidebar.warning("Please enter your Anthropic API key to unlock AI-powered safety features.")

# Time of day consideration
current_hour = datetime.now().hour
time_of_day = st.sidebar.selectbox(
    "🕐 Time of Travel",
    ["Current Time", "Early Morning (6-9 AM)", "Daytime (9 AM-6 PM)", "Evening (6-9 PM)", "Night (9 PM-6 AM)"],
    index=0
)

# User preferences
safety_priority = st.sidebar.slider("🛡️ Safety Priority", 1, 10, 8, help="Higher values prioritize safety over speed")
avoid_areas = st.sidebar.multiselect(
    "🚫 Areas to Avoid",
    ["People's Park", "Telegraph Avenue South", "Downtown BART vicinity", "West Berkeley Industrial"],
    help="Select areas you'd prefer to avoid"
)

col1, col2 = st.columns(2)
with col1:
    start_location = st.selectbox("📍 Start Location", list(locations.keys()), index=0)
with col2:
    end_location = st.selectbox("🏁 Destination", list(locations.keys()), index=1)

# Custom location input
st.markdown("---")
st.subheader("🎯 Or Enter Custom Berkeley Location")
custom_location = st.text_input("Enter any Berkeley neighborhood or address", placeholder="e.g., Bancroft Way, Solano Avenue, Berkeley Hills")

@st.cache_resource
def load_graph():
    return ox.graph_from_place("Berkeley, California, USA", network_type='walk')

def get_time_context(time_selection):
    if time_selection == "Current Time":
        hour = datetime.now().hour
        if 6 <= hour < 9:
            return "early_morning"
        elif 9 <= hour < 18:
            return "daytime"
        elif 18 <= hour < 21:
            return "evening"
        else:
            return "night"
    else:
        return time_selection.lower().split()[0].replace("(", "").replace("-", "_")

def get_safety_class(score):
    if score >= 8:
        return "safety-high"
    elif score >= 6:
        return "safety-medium"
    else:
        return "safety-low"

@st.cache_data
def get_ai_route_analysis(start, end, time_context, safety_priority, avoid_areas, _api_key, custom_loc=None):
    """Get AI-powered route analysis and safety recommendations"""
    if not _api_key:
        return None
    
    try:
        client = anthropic.Anthropic(api_key=_api_key)
        
        location_context = f"from {start} to {end}"
        if custom_loc:
            location_context += f" (custom location: {custom_loc})"
        
        prompt = f"""
        You are a local Berkeley safety expert providing walking route recommendations. 
        
        Route: {location_context}
        Time of travel: {time_context}
        Safety priority (1-10): {safety_priority}
        Areas to avoid: {avoid_areas}
        
        Berkeley neighborhood safety context:
        {json.dumps(neighborhood_context, indent=2)}
        
        Provide a JSON response with:
        1. "safety_analysis": Brief analysis of the route safety
        2. "recommendations": List of 3-4 specific safety tips
        3. "alternative_waypoints": Suggest 2-3 intermediate points for a safer route
        4. "time_specific_advice": Advice based on time of day
        5. "overall_safety_score": Score 1-10 for this specific route
        6. "improvement_suggestions": How to make the route safer
        
        Focus on practical, local Berkeley knowledge that Google Maps wouldn't provide.
        """
        
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse the AI response
        response_text = message.content[0].text
        
        # Try to extract JSON from the response
        try:
            # Look for JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback: create structured response from text
        return {
            "safety_analysis": response_text[:200] + "...",
            "recommendations": ["AI analysis generated", "Check full response below"],
            "alternative_waypoints": [],
            "time_specific_advice": "Consider time of day factors",
            "overall_safety_score": 7,
            "improvement_suggestions": "Full AI response available below",
            "full_response": response_text
        }
        
    except Exception as e:
        st.error(f"AI Analysis Error: {str(e)}")
        return None

# Utility
def get_nearest_node(lat, lon):
    return ox.distance.nearest_nodes(G, lon, lat)

# Load graph
try:
    G = load_graph()
except Exception as e:
    st.error(f"Failed to load Berkeley street network: {e}")
    st.stop()

# Main Route Calculation
if st.button("🚀 Generate AI-Enhanced Safe Route", type="primary"):
    if start_location and end_location and start_location != end_location:
        start_coords = locations[start_location]
        end_coords = locations[end_location]
        
        # AI Analysis
        if api_key:
            with st.spinner("🧠 AI is analyzing the safest route for you..."):
                time_context = get_time_context(time_of_day)
                ai_analysis = get_ai_route_analysis(
                    start_location, end_location, time_context, 
                    safety_priority, avoid_areas, api_key, custom_location
                )
        else:
            ai_analysis = None

        try:
            orig_node = get_nearest_node(*start_coords)
            dest_node = get_nearest_node(*end_coords)

            # Calculate multiple route options
            route = nx.shortest_path(G, orig_node, dest_node, weight='length')
            route_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route]

            # Route metrics
            dist_meters = int(sum(ox.utils_graph.get_route_edge_attributes(G, route, 'length')))
            dist_miles = round(dist_meters * 0.000621371, 2)
            walk_time_min = round((dist_meters / 80), 1)
            avg_safety_score = round((safety_scores[start_location] + safety_scores[end_location]) / 2, 1)

            # Enhanced Map with AI insights
            m = folium.Map(location=start_coords, zoom_start=14, control_scale=True, tiles='CartoDB Positron')
            
            # Add markers
            folium.Marker(start_coords, tooltip=f"Start: {start_location}", 
                         icon=folium.Icon(color='green', icon='play')).add_to(m)
            folium.Marker(end_coords, tooltip=f"End: {end_location}", 
                         icon=folium.Icon(color='red', icon='stop')).add_to(m)
            
            # Main route
            folium.PolyLine(route_coords, color="blue", weight=6, opacity=0.8, 
                           tooltip="Recommended Route").add_to(m)
            
            # Add AI-suggested waypoints if available
            if ai_analysis and 'alternative_waypoints' in ai_analysis:
                for i, waypoint in enumerate(ai_analysis.get('alternative_waypoints', [])):
                    if waypoint in locations:
                        wp_coords = locations[waypoint]
                        folium.Marker(wp_coords, tooltip=f"AI Suggested: {waypoint}", 
                                     icon=folium.Icon(color='purple', icon='star')).add_to(m)

            from streamlit_folium import folium_static 
            folium_static(m, width=725, height=500)


            # Enhanced Metrics Display
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📏 Distance", f"{dist_miles} mi", f"{dist_meters}m")
            with col2:
                st.metric("⏱️ Walk Time", f"{walk_time_min} min")
            with col3:
                safety_class = get_safety_class(avg_safety_score)
                st.markdown(f"**🔐 Base Safety:** <span class='{safety_class}'>{avg_safety_score}/10</span>", 
                           unsafe_allow_html=True)
            with col4:
                if ai_analysis:
                    ai_score = ai_analysis.get('overall_safety_score', avg_safety_score)
                    ai_class = get_safety_class(ai_score)
                    st.markdown(f"**🤖 AI Safety:** <span class='{ai_class}'>{ai_score}/10</span>", 
                               unsafe_allow_html=True)

            # AI Analysis Results
            if ai_analysis:
                st.markdown("---")
                st.markdown("""
                    <div class='ai-route-card'>
                        <h3>🤖 AI Safety Analysis</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🛡️ Safety Recommendations")
                    for i, rec in enumerate(ai_analysis.get('recommendations', []), 1):
                        st.write(f"{i}. {rec}")
                
                with col2:
                    st.subheader("⏰ Time-Specific Advice")
                    st.write(ai_analysis.get('time_specific_advice', 'No specific advice available'))
                
                if ai_analysis.get('safety_analysis'):
                    st.subheader("📊 Route Analysis")
                    st.write(ai_analysis['safety_analysis'])
                
                if ai_analysis.get('improvement_suggestions'):
                    st.subheader("💡 How to Make It Safer")
                    st.write(ai_analysis['improvement_suggestions'])
                
                # Show full AI response if available
                if ai_analysis.get('full_response'):
                    with st.expander("🔍 Full AI Analysis"):
                        st.write(ai_analysis['full_response'])

            # Safety Tips Section
            st.markdown("---")
            st.subheader("🚶‍♀️ General Berkeley Walking Safety Tips")
            
            tips_col1, tips_col2 = st.columns(2)
            
            with tips_col1:
                st.markdown("""
                **🌙 Time-Based Safety:**
                - Avoid People's Park after dark
                - Telegraph Ave is busier (safer) during day
                - UC Campus well-lit at night
                - BART stations vary by time of day
                """)
            
            with tips_col2:
                st.markdown("""
                **🏘️ Neighborhood Insights:**
                - North Berkeley: Quiet, residential
                - Elmwood: Family-friendly area
                - Downtown: Stay on main streets
                - Berkeley Hills: Well-lit paths preferred
                """)

        except Exception as e:
            st.error(f"❌ Failed to calculate route: {e}")
            st.write("This might be due to network connectivity or OpenStreetMap data issues.")
    
    else:
        st.warning("Please select two distinct locations.")

# Custom Location Handler
if custom_location and api_key:
    st.markdown("---")
    st.subheader(f"🎯 AI Analysis for: {custom_location}")
    
    if st.button("Analyze Custom Location Safety"):
        with st.spinner("🧠 AI is analyzing your custom location..."):
            try:
                client = anthropic.Anthropic(api_key=api_key)
                
                custom_prompt = f"""
                Analyze the safety of this Berkeley location for walking: {custom_location}
                
                Consider:
                - Crime statistics and local reputation
                - Lighting and visibility
                - Foot traffic patterns
                - Time of day considerations
                - Nearby landmarks or areas of concern
                
                Provide practical safety advice for walking in this area.
                """
                
                message = client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=600,
                    messages=[{"role": "user", "content": custom_prompt}]
                )
                
                st.markdown("""
                    <div class='ai-thinking'>
                        <h4>🤖 AI Safety Analysis for Your Location</h4>
                    </div>
                """, unsafe_allow_html=True)
                
                st.write(message.content[0].text)
                
            except Exception as e:
                st.error(f"Custom location analysis failed: {e}")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        🥷 <strong>Hoodly</strong> - AI-Powered Berkeley Walking Safety<br>
        Powered by Anthropic Claude AI | Stay Safe, Walk Smart
    </div>
""", unsafe_allow_html=True)
