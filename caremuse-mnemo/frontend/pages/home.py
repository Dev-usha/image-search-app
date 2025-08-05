import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.api_client import APIClient
from utils.state import initialize_session_state
from utils.styles import apply_custom_styles

def main():
    st.set_page_config(
        page_title="CareMuse + Mnemo",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom styles
    apply_custom_styles()
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize API client
    if 'api_client' not in st.session_state:
        st.session_state.api_client = APIClient()
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🧠 CareMuse + Mnemo</h1>
        <p>Your caring digital companion for memory support and wellness</p>
    </div>
    """, unsafe_allow_html=True)
    
    # User onboarding
    if not st.session_state.user_name:
        show_onboarding()
    else:
        show_main_interface()

def show_onboarding():
    """Show user onboarding interface"""
    st.markdown("### Welcome! Let's get to know you")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="welcome-card">
            <h3>🌟 Welcome to CareMuse + Mnemo</h3>
            <p>I'm here to be your caring companion, helping you with:</p>
            <ul>
                <li>💭 Keeping track of your daily memories and experiences</li>
                <li>👥 Chatting with family personas and healthcare providers</li>
                <li>🧠 Playing brain games and tracking your progress</li>
                <li>💊 Managing reminders and health information</li>
                <li>📋 Organizing medical documents and reports</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Name input
        user_name = st.text_input(
            "What would you like me to call you?",
            placeholder="Enter your name here...",
            help="This helps personalize your experience"
        )
        
        if st.button("Get Started", type="primary", use_container_width=True):
            if user_name.strip():
                st.session_state.user_name = user_name.strip()
                st.session_state.onboarding_complete = True
                
                # Store initial greeting memory
                api_client = st.session_state.api_client
                greeting_memory = f"User introduced themselves as {user_name} and started using CareMuse + Mnemo"
                api_client.store_memory(greeting_memory, "introduction", "personal")
                
                st.rerun()
            else:
                st.error("Please enter your name to continue")

def show_main_interface():
    """Show main application interface"""
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"### Hello, {st.session_state.user_name}! 👋")
        
        # Navigation menu
        st.markdown("### 🧭 Navigation")
        
        # Main sections
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = "home"
            
        if st.button("💭 Memory Journal", use_container_width=True):
            st.session_state.current_page = "memory"
            
        if st.button("👥 Chat with Companions", use_container_width=True):
            st.session_state.current_page = "chat"
            
        if st.button("🏥 Medical Center", use_container_width=True):
            st.session_state.current_page = "medical"
            
        if st.button("🧠 Brain Games", use_container_width=True):
            st.session_state.current_page = "games"
            
        if st.button("⏰ Reminders", use_container_width=True):
            st.session_state.current_page = "reminders"
            
        if st.button("📊 Health Tracking", use_container_width=True):
            st.session_state.current_page = "health"
            
        if st.button("📜 Chat History", use_container_width=True):
            st.session_state.current_page = "chat_history"
            
        st.divider()
        
        # Quick stats
        show_quick_stats()
        
        st.divider()
        
        # Settings
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.current_page = "settings"
    
    # Main content area
    current_page = st.session_state.get('current_page', 'home')
    
    if current_page == "home":
        show_dashboard()
    elif current_page == "memory":
        show_memory_page()
    elif current_page == "chat":
        show_chat_page()
    elif current_page == "medical":
        show_medical_page()
    elif current_page == "games":
        show_games_page()
    elif current_page == "reminders":
        show_reminders_page()
    elif current_page == "health":
        show_health_page()
    elif current_page == "chat_history":
        show_chat_history_page()
    elif current_page == "settings":
        show_settings_page()

def show_quick_stats():
    """Show quick statistics in sidebar"""
    try:
        api_client = st.session_state.api_client
        
        # Get recent stats
        memories = api_client.get_memories(scope="personal", limit=10)
        chat_history = api_client.get_chat_history(days=7)
        
        st.markdown("### 📊 Quick Stats")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Memories", len(memories))
        with col2:
            st.metric("Chats (7d)", len(chat_history))
            
    except Exception as e:
        st.error(f"Error loading stats: {e}")

def show_dashboard():
    """Show main dashboard"""
    st.markdown("### 🏠 Welcome Home")
    
    # Today's overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <h4>💭 Today's Memories</h4>
            <p>Capture your experiences and thoughts</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Add Memory", key="dash_memory", use_container_width=True):
            st.session_state.current_page = "memory"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="dashboard-card">
            <h4>👥 Chat with Family</h4>
            <p>Connect with your loving companions</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Start Chatting", key="dash_chat", use_container_width=True):
            st.session_state.current_page = "chat"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="dashboard-card">
            <h4>🧠 Brain Exercise</h4>
            <p>Keep your mind active and sharp</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Play Games", key="dash_games", use_container_width=True):
            st.session_state.current_page = "games"
            st.rerun()
    
    st.divider()
    
    # Recent activity
    show_recent_activity()

def show_recent_activity():
    """Show recent activity feed"""
    st.markdown("### 📋 Recent Activity")
    
    try:
        api_client = st.session_state.api_client
        
        # Get recent memories and chats
        recent_memories = api_client.get_memories(scope="personal", limit=5)
        recent_chats = api_client.get_chat_history(days=3, limit=5)
        
        # Combine and sort by timestamp
        all_activity = []
        
        for memory in recent_memories:
            all_activity.append({
                'type': 'memory',
                'timestamp': memory.get('timestamp'),
                'content': memory.get('text', ''),
                'memory_type': memory.get('memory_type', 'general')
            })
        
        for chat in recent_chats:
            all_activity.append({
                'type': 'chat',
                'timestamp': chat.get('timestamp'),
                'content': chat.get('user_message', ''),
                'persona': chat.get('persona', 'unknown')
            })
        
        # Sort by timestamp (most recent first)
        all_activity.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Display recent activity
        for activity in all_activity[:8]:  # Show top 8 items
            if activity['type'] == 'memory':
                st.markdown(f"""
                <div class="activity-item">
                    <span class="activity-icon">💭</span>
                    <span class="activity-content">{activity['content'][:100]}...</span>
                    <span class="activity-type">{activity['memory_type']}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="activity-item">
                    <span class="activity-icon">💬</span>
                    <span class="activity-content">{activity['content'][:100]}...</span>
                    <span class="activity-type">{activity['persona']}</span>
                </div>
                """, unsafe_allow_html=True)
        
        if not all_activity:
            st.info("No recent activity. Start by adding a memory or chatting with a companion!")
            
    except Exception as e:
        st.error(f"Error loading recent activity: {e}")

def show_memory_page():
    """Import and show memory page"""
    from pages.memory import show_memory_interface
    show_memory_interface()

def show_chat_page():
    """Import and show chat page"""
    from modules.companion import show_companion_interface
    show_companion_interface()

def show_medical_page():
    """Import and show medical page"""
    from pages.medical import show_medical_interface
    show_medical_interface()

def show_games_page():
    """Import and show games page"""
    from modules.games import show_games_interface
    show_games_interface()

def show_reminders_page():
    """Import and show reminders page"""
    from modules.reminders import show_reminders_interface
    show_reminders_interface()

def show_health_page():
    """Import and show health page"""
    from modules.health import show_health_interface
    show_health_interface()

def show_chat_history_page():
    """Import and show chat history page"""
    from pages.chat_history import show_chat_history_interface
    show_chat_history_interface()

def show_settings_page():
    """Show settings interface"""
    st.markdown("### ⚙️ Settings")
    
    st.markdown("#### User Information")
    new_name = st.text_input("Your Name", value=st.session_state.user_name)
    
    if st.button("Update Name"):
        st.session_state.user_name = new_name
        st.success("Name updated successfully!")
    
    st.divider()
    
    st.markdown("#### Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export Data", help="Download your data for backup"):
            st.info("Data export functionality coming soon!")
    
    with col2:
        if st.button("Clear History", help="Remove old conversations and memories"):
            if st.checkbox("I understand this will delete my data"):
                st.warning("This feature is not yet implemented for safety.")
    
    st.divider()
    
    st.markdown("#### About CareMuse + Mnemo")
    st.info("""
    CareMuse + Mnemo is your caring digital companion designed to support individuals 
    with memory challenges. Features include memory journaling, persona-based conversations, 
    brain games, health tracking, and medical document management.
    
    Version: 1.0.0
    """)

if __name__ == "__main__":
    main()