# Hoodly-2.0
🥷 Hoodly: AI-Powered Safe Walking in Berkeley
An intelligent route planning application that uses AI to provide safer walking routes in Berkeley, California. Powered by Anthropic's Claude AI for enhanced safety analysis and personalized recommendations.
Features

AI-Enhanced Route Planning: Get personalized safety recommendations beyond what Google Maps offers
Real-time Safety Analysis: Dynamic safety scores based on time of day, location, and user preferences
Interactive Maps: Visual route planning with safety waypoints and alternative paths
Berkeley-Specific Intelligence: Local knowledge of neighborhoods, safety patterns, and time-based considerations
Custom Location Analysis: Get AI-powered safety insights for any Berkeley location

Live Demo
🌐 Try Hoodly Live
Quick Start
Option 1: Use the Live App

Visit the live app link above
Enter your Anthropic API key when prompted
Select your start and end locations
Get AI-powered safety recommendations!

Option 2: Run Locally
bash# Clone the repository
git clone https://github.com/yourusername/hoodly-berkeley-safety.git
cd hoodly-berkeley-safety

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
API Key Setup
You'll need an Anthropic API key to use the AI features:

Get API Key: Visit Anthropic Console and create an API key
For Local Development:

Option A: Enter the key directly in the app's sidebar
Option B: Set environment variable ANTHROPIC_API_KEY


For Streamlit Cloud Deployment: Add your API key in the Streamlit Cloud secrets (see deployment guide below)

How It Works

Location Selection: Choose from 29+ pre-mapped Berkeley locations or enter custom addresses
AI Analysis: Claude AI analyzes route safety based on:

Local crime patterns and neighborhood characteristics
Time of day considerations
Lighting and foot traffic patterns
User safety preferences


Smart Recommendations: Get specific, actionable safety tips and alternative waypoints
Visual Route Planning: Interactive maps with safety-coded routes and waypoints

Technology Stack

Frontend: Streamlit
Maps: Folium + OpenStreetMap
Routing: OSMnx + NetworkX
AI: Anthropic Claude
Geospatial: GeoPy, Geopandas

Local Development
bash# Install dependencies
pip install -r requirements.txt

# Set your API key (optional - can also enter in app)
export ANTHROPIC_API_KEY=your_api_key_here

# Run the application
streamlit run app.py
The app will be available at http://localhost:8501
Deployment on Streamlit Cloud

Fork this repository to your GitHub account
Go to Streamlit Cloud
Create a new app:

Repository: yourusername/hoodly-berkeley-safety
Branch: main
Main file path: app.py


Add your API key:

Go to your app settings in Streamlit Cloud
Navigate to "Secrets"
Add: ANTHROPIC_API_KEY = "your_api_key_here"


Deploy: Your app will be available at https://your-app-name.streamlit.app

Safety Data Sources
The app combines multiple data sources for comprehensive safety analysis:

Local crime statistics and patterns
UC Berkeley safety reports
Community feedback and local knowledge
Time-based incident data
Lighting and infrastructure assessments

Contributing
We welcome contributions! Areas for improvement:

Additional Berkeley locations and safety data
Enhanced AI prompting for better recommendations
Mobile responsiveness improvements
Integration with real-time crime data APIs
Multi-language support

Privacy & Security

API Keys: Never stored or logged - used only for session-based requests
Location Data: No personal location data is stored or tracked
AI Requests: Only route and location data sent to Anthropic for safety analysis

License
MIT License - see LICENSE file for details.
Acknowledgments

Berkeley community for local safety insights
Anthropic for Claude AI capabilities
OpenStreetMap contributors for mapping data
Streamlit for the amazing app framework

Support

🐛 Bug Reports: Open an issue
💡 Feature Requests: Start a discussion
📧 Contact: your.email@example.com


Stay Safe, Walk Smart 🥷
