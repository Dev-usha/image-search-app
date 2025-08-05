import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.api_client import APIClient

def show_health_interface():
    """Main health tracking interface"""
    st.markdown("### 📊 Health Tracking")
    st.markdown("Monitor your vital signs, wellness metrics, and health trends.")
    
    # Tabs for different health functions
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Log Health", "📈 Health Trends", "🎯 Daily Goals", "📋 Health Summary"])
    
    with tab1:
        show_health_logging()
    
    with tab2:
        show_health_trends()
    
    with tab3:
        show_daily_goals()
    
    with tab4:
        show_health_summary()

def show_health_logging():
    """Interface for logging health metrics"""
    st.markdown("#### 📝 Log Your Health Metrics")
    
    # Quick log buttons
    st.markdown("##### 🚀 Quick Log")
    show_quick_health_buttons()
    
    st.divider()
    
    # Detailed health entry form
    st.markdown("##### 📋 Detailed Entry")
    
    with st.form("health_entry_form"):
        # Health metric type
        metric_type = st.selectbox(
            "Health Metric",
            options=[
                "Blood Pressure",
                "Heart Rate", 
                "Temperature",
                "Weight",
                "Blood Sugar",
                "Water Intake",
                "Sleep Hours",
                "Exercise Minutes",
                "Mood Score",
                "Pain Level",
                "Energy Level",
                "Medication Taken"
            ],
            help="Select the type of health metric to log"
        )
        
        # Value and unit based on metric type
        col1, col2 = st.columns(2)
        
        with col1:
            if metric_type == "Blood Pressure":
                systolic = st.number_input("Systolic (top number)", min_value=70, max_value=250, value=120)
                diastolic = st.number_input("Diastolic (bottom number)", min_value=40, max_value=150, value=80)
                value = f"{systolic}/{diastolic}"
                unit = "mmHg"
            
            elif metric_type == "Heart Rate":
                value = st.number_input("Heart Rate", min_value=30, max_value=200, value=72)
                unit = "bpm"
            
            elif metric_type == "Temperature":
                value = st.number_input("Temperature", min_value=95.0, max_value=110.0, value=98.6, step=0.1)
                unit = "°F"
            
            elif metric_type == "Weight":
                value = st.number_input("Weight", min_value=50, max_value=500, value=150)
                unit = "lbs"
            
            elif metric_type == "Blood Sugar":
                value = st.number_input("Blood Sugar", min_value=50, max_value=400, value=100)
                unit = "mg/dL"
            
            elif metric_type == "Water Intake":
                value = st.number_input("Glasses of Water", min_value=0, max_value=20, value=1)
                unit = "glasses"
            
            elif metric_type == "Sleep Hours":
                value = st.number_input("Hours of Sleep", min_value=0.0, max_value=24.0, value=8.0, step=0.5)
                unit = "hours"
            
            elif metric_type == "Exercise Minutes":
                value = st.number_input("Exercise Minutes", min_value=0, max_value=480, value=30)
                unit = "minutes"
            
            elif metric_type in ["Mood Score", "Pain Level", "Energy Level"]:
                value = st.slider(f"{metric_type} (1-10)", min_value=1, max_value=10, value=5)
                unit = "scale 1-10"
            
            elif metric_type == "Medication Taken":
                medication_name = st.text_input("Medication Name", placeholder="e.g., Aspirin, Vitamin D")
                dosage = st.text_input("Dosage", placeholder="e.g., 81mg, 1 tablet")
                value = f"{medication_name} - {dosage}" if medication_name and dosage else medication_name
                unit = ""
            
            else:
                value = st.text_input("Value")
                unit = st.text_input("Unit", placeholder="e.g., mg, ml, units")
        
        with col2:
            # Time of measurement
            measurement_time = st.time_input(
                "Time of Measurement",
                value=datetime.now().time(),
                help="When was this measurement taken?"
            )
            
            # Date of measurement
            measurement_date = st.date_input(
                "Date",
                value=datetime.now().date(),
                help="Date of measurement"
            )
        
        # Additional notes
        notes = st.text_area(
            "Notes (Optional)",
            placeholder="Any additional observations, symptoms, or context...",
            help="Add any relevant details about this measurement"
        )
        
        # Submit button
        submitted = st.form_submit_button("📊 Log Health Metric", type="primary", use_container_width=True)
        
        if submitted:
            if value:
                save_health_metric(metric_type, str(value), unit, notes, measurement_date, measurement_time)
            else:
                st.error("Please enter a value for the health metric.")

def show_quick_health_buttons():
    """Show quick health logging buttons"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🚰 Log Water", key="quick_water", use_container_width=True):
            quick_log_health("Water Intake", "1", "glasses", "Quick water intake log")
    
    with col2:
        if st.button("💊 Took Medication", key="quick_med", use_container_width=True):
            quick_log_health("Medication Taken", "Medication taken as prescribed", "", "Quick medication log")
    
    with col3:
        if st.button("🏃 Exercise Done", key="quick_exercise", use_container_width=True):
            quick_log_health("Exercise Minutes", "30", "minutes", "Quick exercise log")
    
    with col4:
        if st.button("😊 Good Mood", key="quick_mood", use_container_width=True):
            quick_log_health("Mood Score", "8", "scale 1-10", "Feeling good today")

def quick_log_health(metric_type, value, unit, notes):
    """Quick log a health metric"""
    save_health_metric(metric_type, value, unit, notes, datetime.now().date(), datetime.now().time())

def save_health_metric(metric_type, value, unit, notes, date, time):
    """Save a health metric"""
    try:
        api_client = st.session_state.api_client
        
        result = api_client.log_health_metric(
            metric_type=metric_type.lower().replace(" ", "_"),
            value=value,
            unit=unit,
            notes=notes
        )
        
        if result.get("status") == "success":
            st.success(f"✅ {metric_type} logged successfully!")
            
            # Show confirmation
            with st.expander("Logged Entry", expanded=True):
                st.markdown(f"**Metric:** {metric_type}")
                st.markdown(f"**Value:** {value} {unit}")
                st.markdown(f"**Date/Time:** {date.strftime('%B %d, %Y')} at {time.strftime('%I:%M %p')}")
                if notes:
                    st.markdown(f"**Notes:** {notes}")
        else:
            st.error("Failed to log health metric. Please try again.")
            
    except Exception as e:
        st.error(f"Error logging health metric: {e}")

def show_health_trends():
    """Show health trends and charts"""
    st.markdown("#### 📈 Health Trends")
    
    # Time period selector
    col1, col2 = st.columns(2)
    
    with col1:
        time_period = st.selectbox(
            "Time Period",
            options=[7, 30, 90, 365],
            format_func=lambda x: f"Last {x} days",
            index=1,
            key="trends_period"
        )
    
    with col2:
        if st.button("🔄 Refresh Charts", key="refresh_trends"):
            st.rerun()
    
    try:
        api_client = st.session_state.api_client
        
        # Get health statistics
        health_stats = api_client.get_health_stats(days=time_period)
        
        if health_stats.get('total_entries', 0) > 0:
            # Show overall metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Entries", health_stats['total_entries'])
            
            with col2:
                st.metric("Tracked Metrics", len(health_stats.get('metrics', {})))
            
            with col3:
                st.metric("Days Active", min(time_period, health_stats['total_entries']))
            
            # Show charts for each metric
            metrics = health_stats.get('metrics', {})
            
            for metric_type, data in metrics.items():
                if data.get('values') and len(data['values']) > 1:
                    show_health_chart(metric_type, data)
        
        else:
            st.info("No health data available for the selected period. Start logging your health metrics to see trends!")
            
    except Exception as e:
        st.error(f"Error loading health trends: {e}")

def show_health_chart(metric_type, data):
    """Show chart for a specific health metric"""
    metric_name = metric_type.replace('_', ' ').title()
    values = data.get('values', [])
    
    if len(values) < 2:
        return
    
    # Create chart based on metric type
    fig = go.Figure()
    
    # Generate x-axis (dates)
    dates = [datetime.now() - timedelta(days=i) for i in range(len(values)-1, -1, -1)]
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines+markers',
        name=metric_name,
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=6)
    ))
    
    # Customize chart
    fig.update_layout(
        title=f"{metric_name} Trend",
        xaxis_title="Date",
        yaxis_title=get_metric_unit(metric_type),
        showlegend=False,
        height=400,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    # Add trend line if enough data points
    if len(values) >= 5:
        # Simple trend calculation
        x_numeric = list(range(len(values)))
        z = np.polyfit(x_numeric, values, 1)
        p = np.poly1d(z)
        trend_values = [p(x) for x in x_numeric]
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=trend_values,
            mode='lines',
            name='Trend',
            line=dict(color='red', width=1, dash='dash'),
            showlegend=False
        ))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current", f"{values[-1]:.1f}" if isinstance(values[-1], (int, float)) else str(values[-1]))
    
    with col2:
        avg_value = sum(values) / len(values) if values else 0
        st.metric("Average", f"{avg_value:.1f}")
    
    with col3:
        if isinstance(values[0], (int, float)):
            st.metric("Highest", f"{max(values):.1f}")
    
    with col4:
        if isinstance(values[0], (int, float)):
            st.metric("Lowest", f"{min(values):.1f}")

def show_daily_goals():
    """Show daily health goals and progress"""
    st.markdown("#### 🎯 Daily Health Goals")
    
    # Default daily goals
    daily_goals = {
        "Water Intake": {"target": 8, "unit": "glasses", "emoji": "🚰"},
        "Exercise Minutes": {"target": 30, "unit": "minutes", "emoji": "🏃"},
        "Sleep Hours": {"target": 8, "unit": "hours", "emoji": "😴"},
        "Mood Score": {"target": 7, "unit": "rating", "emoji": "😊"}
    }
    
    # Get today's health data
    try:
        api_client = st.session_state.api_client
        
        # Get today's entries
        health_stats = api_client.get_health_stats(days=1)
        today_metrics = health_stats.get('metrics', {})
        
        # Show progress for each goal
        for goal_name, goal_info in daily_goals.items():
            metric_key = goal_name.lower().replace(" ", "_")
            current_value = 0
            
            if metric_key in today_metrics:
                values = today_metrics[metric_key].get('values', [])
                if values:
                    if goal_name == "Water Intake":
                        current_value = sum(values)  # Sum all water entries
                    else:
                        current_value = values[-1]  # Latest value for others
            
            show_goal_progress(goal_name, current_value, goal_info)
        
        # Goal completion summary
        completed_goals = 0
        total_goals = len(daily_goals)
        
        for goal_name, goal_info in daily_goals.items():
            metric_key = goal_name.lower().replace(" ", "_")
            current_value = 0
            
            if metric_key in today_metrics:
                values = today_metrics[metric_key].get('values', [])
                if values:
                    if goal_name == "Water Intake":
                        current_value = sum(values)
                    else:
                        current_value = values[-1]
            
            if current_value >= goal_info["target"]:
                completed_goals += 1
        
        # Show overall progress
        st.markdown("#### 🏆 Today's Progress")
        
        progress_percentage = (completed_goals / total_goals) * 100
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Goals Completed", f"{completed_goals}/{total_goals}")
        
        with col2:
            st.metric("Completion Rate", f"{progress_percentage:.0f}%")
        
        with col3:
            if completed_goals == total_goals:
                st.success("🎉 All goals achieved!")
            elif completed_goals >= total_goals // 2:
                st.info("👍 Good progress!")
            else:
                st.warning("💪 Keep going!")
        
    except Exception as e:
        st.error(f"Error loading daily goals: {e}")

def show_goal_progress(goal_name, current_value, goal_info):
    """Show progress for a specific goal"""
    target = goal_info["target"]
    unit = goal_info["unit"]
    emoji = goal_info["emoji"]
    
    progress = min(current_value / target, 1.0) if target > 0 else 0
    
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{emoji} {goal_name}**")
            st.progress(progress)
            st.caption(f"{current_value:.1f} / {target} {unit}")
        
        with col2:
            if progress >= 1.0:
                st.success("✅ Done!")
            else:
                remaining = target - current_value
                st.info(f"{remaining:.1f} to go")

def show_health_summary():
    """Show comprehensive health summary"""
    st.markdown("#### 📋 Health Summary")
    
    try:
        api_client = st.session_state.api_client
        
        # Get health stats for different periods
        week_stats = api_client.get_health_stats(days=7)
        month_stats = api_client.get_health_stats(days=30)
        
        # Summary cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="health-summary-card">
                <h4>📊 This Week</h4>
                <p>{} entries</p>
                <p>{} metrics tracked</p>
            </div>
            """.format(
                week_stats.get('total_entries', 0),
                len(week_stats.get('metrics', {}))
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="health-summary-card">
                <h4>📈 This Month</h4>
                <p>{} entries</p>
                <p>{} metrics tracked</p>
            </div>
            """.format(
                month_stats.get('total_entries', 0),
                len(month_stats.get('metrics', {}))
            ), unsafe_allow_html=True)
        
        with col3:
            # Calculate consistency (days with entries)
            consistency = min(week_stats.get('total_entries', 0) / 7.0, 1.0) * 100
            st.markdown(f"""
            <div class="health-summary-card">
                <h4>🎯 Consistency</h4>
                <p>{consistency:.0f}%</p>
                <p>Weekly tracking</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            # Health score based on goal completion
            health_score = calculate_health_score(week_stats)
            st.markdown(f"""
            <div class="health-summary-card">
                <h4>💪 Health Score</h4>
                <p>{health_score}/100</p>
                <p>Overall wellness</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Recent entries
        st.markdown("##### 📝 Recent Health Entries")
        show_recent_health_entries()
        
        # Health insights
        st.markdown("##### 💡 Health Insights")
        show_health_insights(week_stats, month_stats)
        
    except Exception as e:
        st.error(f"Error loading health summary: {e}")

def show_recent_health_entries():
    """Show recent health entries"""
    try:
        api_client = st.session_state.api_client
        
        # Get recent health logs (would need backend support)
        # For now, show placeholder
        st.info("Recent health entries will be displayed here. (Feature enhancement needed)")
        
    except Exception as e:
        st.error(f"Error loading recent entries: {e}")

def show_health_insights(week_stats, month_stats):
    """Show health insights and recommendations"""
    insights = []
    
    # Analyze metrics for insights
    week_metrics = week_stats.get('metrics', {})
    month_metrics = month_stats.get('metrics', {})
    
    # Water intake insights
    if 'water_intake' in week_metrics:
        water_values = week_metrics['water_intake'].get('values', [])
        if water_values:
            avg_water = sum(water_values) / len(water_values)
            if avg_water < 6:
                insights.append("🚰 Consider increasing your daily water intake. Aim for 8 glasses per day.")
            elif avg_water >= 8:
                insights.append("🚰 Excellent hydration! You're meeting your daily water goals.")
    
    # Exercise insights
    if 'exercise_minutes' in week_metrics:
        exercise_values = week_metrics['exercise_minutes'].get('values', [])
        if exercise_values:
            avg_exercise = sum(exercise_values) / len(exercise_values)
            if avg_exercise < 20:
                insights.append("🏃 Try to increase physical activity. Even 30 minutes daily can make a big difference.")
            elif avg_exercise >= 30:
                insights.append("🏃 Great job staying active! Your exercise routine is on track.")
    
    # Mood insights
    if 'mood_score' in week_metrics:
        mood_values = week_metrics['mood_score'].get('values', [])
        if mood_values:
            avg_mood = sum(mood_values) / len(mood_values)
            if avg_mood < 5:
                insights.append("😊 Consider activities that boost your mood, like spending time outdoors or with loved ones.")
            elif avg_mood >= 7:
                insights.append("😊 Your mood has been consistently positive! Keep up the great work.")
    
    # Sleep insights
    if 'sleep_hours' in week_metrics:
        sleep_values = week_metrics['sleep_hours'].get('values', [])
        if sleep_values:
            avg_sleep = sum(sleep_values) / len(sleep_values)
            if avg_sleep < 7:
                insights.append("😴 Try to get more sleep. Aim for 7-9 hours per night for optimal health.")
            elif avg_sleep >= 8:
                insights.append("😴 Excellent sleep habits! You're getting the rest your body needs.")
    
    # Display insights
    if insights:
        for insight in insights:
            st.info(insight)
    else:
        st.info("💡 Keep logging your health metrics to receive personalized insights!")

def calculate_health_score(stats):
    """Calculate overall health score"""
    score = 50  # Base score
    
    metrics = stats.get('metrics', {})
    
    # Add points for tracked metrics
    score += len(metrics) * 5
    
    # Add points for consistency
    total_entries = stats.get('total_entries', 0)
    if total_entries >= 7:  # Daily tracking
        score += 20
    elif total_entries >= 4:  # Regular tracking
        score += 10
    
    # Bonus for meeting goals (simplified)
    for metric_name, data in metrics.items():
        values = data.get('values', [])
        if values:
            latest_value = values[-1]
            if metric_name == 'water_intake' and latest_value >= 8:
                score += 5
            elif metric_name == 'exercise_minutes' and latest_value >= 30:
                score += 5
            elif metric_name == 'mood_score' and latest_value >= 7:
                score += 5
            elif metric_name == 'sleep_hours' and latest_value >= 7:
                score += 5
    
    return min(score, 100)

def get_metric_unit(metric_type):
    """Get unit for metric type"""
    units = {
        "blood_pressure": "mmHg",
        "heart_rate": "bpm",
        "temperature": "°F",
        "weight": "lbs",
        "blood_sugar": "mg/dL",
        "water_intake": "glasses",
        "sleep_hours": "hours",
        "exercise_minutes": "minutes",
        "mood_score": "1-10 scale",
        "pain_level": "1-10 scale",
        "energy_level": "1-10 scale"
    }
    return units.get(metric_type, "")

# Import numpy for trend calculation
try:
    import numpy as np
except ImportError:
    # Fallback if numpy not available
    def np_polyfit_fallback(x, y, degree):
        return [0, sum(y)/len(y)]  # Simple average as fallback
    
    class NumpyFallback:
        def polyfit(self, x, y, degree):
            return np_polyfit_fallback(x, y, degree)
        def poly1d(self, coeffs):
            return lambda x: coeffs[1]  # Return constant function
    
    np = NumpyFallback()