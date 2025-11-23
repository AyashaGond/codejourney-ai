import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="CodeJourney AI",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
    }
    .feature-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🚀 CodeJourney AI</h1>', unsafe_allow_html=True)
st.markdown("### Your GitHub Career Analytics Platform - MCA 3rd Semester Project")

# Sidebar
with st.sidebar:
    st.header("🔍 Analysis Settings")
    username = st.text_input("GitHub Username", "torvalds")
    analyze_btn = st.button("🚀 Analyze Career Journey")
    
    st.markdown("---")
    st.header("📊 Project Info")
    st.write("""
    **CodeJourney AI** analyzes your GitHub profile to provide:
    - Career Pattern Detection
    - Skill Proficiency Analysis  
    - Learning Journey Timeline
    - Growth Recommendations
    """)

# Main analysis function
def analyze_github_profile(username):
    try:
        # Fetch user repositories
        response = requests.get(f"https://api.github.com/users/{username}/repos")
        if response.status_code != 200:
            return {"error": f"User '{username}' not found or API limit exceeded"}
        
        repos = response.json()
        if not repos:
            return {"error": "No repositories found"}
        
        # Analyze languages and timeline
        language_analysis = {}
        yearly_data = {}
        
        for repo in repos[:15]:  # Limit to 15 repos for performance
            # Get repo creation year
            created_date = datetime.strptime(repo['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            year = created_date.year
            
            # Initialize year data
            if year not in yearly_data:
                yearly_data[year] = {"languages": {}, "repo_count": 0}
            yearly_data[year]["repo_count"] += 1
            
            # Get languages for this repo
            lang_response = requests.get(repo['languages_url'])
            if lang_response.status_code == 200:
                repo_languages = lang_response.json()
                
                # Update language analysis
                for lang, bytes_used in repo_languages.items():
                    language_analysis[lang] = language_analysis.get(lang, 0) + bytes_used
                    
                    # Update yearly data
                    yearly_data[year]["languages"][lang] = yearly_data[year]["languages"].get(lang, 0) + bytes_used
        
        # Calculate language percentages
        total_bytes = sum(language_analysis.values())
        language_percentages = {lang: (bytes_used/total_bytes)*100 for lang, bytes_used in language_analysis.items()}
        
        # Determine career archetype
        language_count = len(language_analysis)
        if language_count <= 3:
            archetype = "🧠 Specialist"
            description = "Deep expertise in few technologies with focused learning"
        elif language_count >= 8:
            archetype = "🔍 Explorer" 
            description = "Enjoys experimenting with diverse technologies and frameworks"
        else:
            archetype = "🚀 Evolver"
            description = "Balanced approach with strategic technology progression"
        
        # Generate recommendations
        top_languages = sorted(language_percentages.items(), key=lambda x: x[1], reverse=True)[:3]
        primary_lang = top_languages[0][0] if top_languages else "Unknown"
        
        recommendations = [
            f"Deepen your expertise in {primary_lang} with advanced projects",
            f"Learn complementary technologies to expand your skill set",
            "Contribute to open-source projects to build your portfolio"
        ]
        
        return {
            "success": True,
            "username": username,
            "total_repos": len(repos),
            "language_analysis": language_analysis,
            "language_percentages": language_percentages,
            "yearly_data": yearly_data,
            "archetype": archetype,
            "description": description,
            "recommendations": recommendations,
            "top_languages": top_languages
        }
    
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

# Main application logic
if analyze_btn and username:
    with st.spinner("🔍 Analyzing GitHub profile and detecting career patterns..."):
        result = analyze_github_profile(username)
        
        if "error" in result:
            st.error(f"❌ {result['error']}")
        else:
            st.success(f"✅ Successfully analyzed {result['username']}'s GitHub profile!")
            
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Timeline Analysis", "🎯 Career Insights"])
            
            with tab1:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📈 Language Distribution")
                    if result['language_percentages']:
                        # Create bar chart
                        lang_df = pd.DataFrame({
                            'Language': list(result['language_percentages'].keys()),
                            'Percentage': list(result['language_percentages'].values())
                        }).head(8)  # Top 8 languages
                        
                        fig = px.bar(lang_df, x='Language', y='Percentage', 
                                   title="Top Programming Languages")
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("👤 Profile Summary")
                    st.metric("Total Repositories", result['total_repos'])
                    st.metric("Languages Used", len(result['language_analysis']))
                    st.metric("Career Archetype", result['archetype'])
                    
                    st.subheader("🏆 Top Languages")
                    for lang, percentage in result['top_languages']:
                        st.progress(int(percentage), text=f"{lang}: {percentage:.1f}%")
            
            with tab2:
                st.subheader("📅 Learning Journey Timeline")
                
                if result['yearly_data']:
                    # Prepare timeline data
                    years = sorted(result['yearly_data'].keys())
                    repo_counts = [result['yearly_data'][year]['repo_count'] for year in years]
                    
                    timeline_df = pd.DataFrame({
                        'Year': years,
                        'Repositories Created': repo_counts
                    })
                    
                    fig = px.line(timeline_df, x='Year', y='Repositories Created',
                                title='Repository Creation Timeline', markers=True)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Yearly language breakdown
                    st.subheader("Yearly Language Focus")
                    for year in years[-3:]:  # Last 3 years
                        year_langs = result['yearly_data'][year]['languages']
                        if year_langs:
                            top_year_lang = max(year_langs.items(), key=lambda x: x[1])[0]
                            st.write(f"**{year}:** Primary focus on **{top_year_lang}**")
                else:
                    st.info("No timeline data available")
            
            with tab3:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🎭 Career Archetype")
                    st.markdown(f"### {result['archetype']}")
                    st.write(result['description'])
                    
                    st.subheader("📊 Pattern Analysis")
                    st.write(f"• **Languages Mastered:** {len(result['language_analysis'])}")
                    st.write(f"• **Primary Language:** {result['top_languages'][0][0] if result['top_languages'] else 'N/A'}")
                    st.write(f"• **Code Diversity:** {'High' if len(result['language_analysis']) > 5 else 'Medium' if len(result['language_analysis']) > 2 else 'Low'}")
                
                with col2:
                    st.subheader("💡 Growth Recommendations")
                    for i, recommendation in enumerate(result['recommendations'], 1):
                        st.markdown(f"**{i}.** {recommendation}")
                    
                    st.subheader("🚀 Next Steps")
                    st.info("""
                    Continue your learning journey by:
                    - Building projects with new technologies
                    - Contributing to open-source communities  
                    - Learning system design and architecture
                    - Networking with other developers
                    """)

else:
    # Default view when no analysis is done
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.subheader("🔍 Career Pattern Detection")
        st.write("Identify your learning style: Specialist, Explorer, or Evolver")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.subheader("📊 Skill Proficiency Analysis")
        st.write("Measure your expertise across different programming languages")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.subheader("🚀 Growth Recommendations")
        st.write("Get personalized suggestions for career advancement")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🎯 How to Use")
    st.write("""
    1. Enter any GitHub username in the sidebar
    2. Click 'Analyze Career Journey' 
    3. View comprehensive career insights across multiple tabs
    4. Explore language trends, timeline analysis, and growth recommendations
    """)
    
    st.subheader("👥 Try These Example Users")
    example_users = ["torvalds", "gaearon", "yyx990803", "sindresorhus"]
    cols = st.columns(4)
    for i, user in enumerate(example_users):
        with cols[i]:
            if st.button(f"@{user}", key=user):
                st.experimental_set_query_params(username=user)
                st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>CodeJourney AI - MCA 3rd Semester Project | Built with Streamlit & GitHub API</p>
</div>
""", unsafe_allow_html=True)