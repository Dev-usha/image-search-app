import streamlit as st
from datetime import datetime
from typing import Dict, Any, List

def initialize_session_state():
    """Initialize all session state variables for the application"""
    
    # User information
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
    
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {
            'theme': 'light',
            'font_size': 'medium',
            'notifications': True,
            'auto_save': True
        }
    
    # Navigation state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
    
    if 'previous_page' not in st.session_state:
        st.session_state.previous_page = "home"
    
    # Onboarding state
    if 'onboarding_complete' not in st.session_state:
        st.session_state.onboarding_complete = False
    
    # Chat state
    if 'selected_persona' not in st.session_state:
        st.session_state.selected_persona = "companion"
    
    if 'chat_histories' not in st.session_state:
        st.session_state.chat_histories = {}
    
    if 'current_chat_session' not in st.session_state:
        st.session_state.current_chat_session = None
    
    # Memory state
    if 'selected_memory' not in st.session_state:
        st.session_state.selected_memory = None
    
    if 'memory_draft' not in st.session_state:
        st.session_state.memory_draft = {
            'text': '',
            'type': 'diary',
            'mood': '😊 Happy',
            'tags': ''
        }
    
    # Medical state
    if 'selected_document' not in st.session_state:
        st.session_state.selected_document = None
    
    if 'active_medical_tab' not in st.session_state:
        st.session_state.active_medical_tab = 0
    
    # Health tracking state
    if 'health_metrics' not in st.session_state:
        st.session_state.health_metrics = {
            'water_intake': 0,
            'exercise_minutes': 0,
            'sleep_hours': 0,
            'mood_score': 5
        }
    
    # Game state
    if 'current_game' not in st.session_state:
        st.session_state.current_game = None
    
    if 'game_scores' not in st.session_state:
        st.session_state.game_scores = {}
    
    if 'game_session' not in st.session_state:
        st.session_state.game_session = {
            'active': False,
            'start_time': None,
            'current_score': 0,
            'level': 1
        }
    
    # Reminders state
    if 'active_reminders' not in st.session_state:
        st.session_state.active_reminders = []
    
    if 'reminder_notifications' not in st.session_state:
        st.session_state.reminder_notifications = []
    
    # UI state
    if 'sidebar_expanded' not in st.session_state:
        st.session_state.sidebar_expanded = True
    
    if 'show_help' not in st.session_state:
        st.session_state.show_help = False
    
    if 'loading_states' not in st.session_state:
        st.session_state.loading_states = {}
    
    # Error handling state
    if 'error_messages' not in st.session_state:
        st.session_state.error_messages = []
    
    if 'success_messages' not in st.session_state:
        st.session_state.success_messages = []
    
    # Application metadata
    if 'app_version' not in st.session_state:
        st.session_state.app_version = "1.0.0"
    
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = datetime.now()
    
    if 'session_start_time' not in st.session_state:
        st.session_state.session_start_time = datetime.now()

def reset_session_state():
    """Reset all session state variables (for logout or reset)"""
    keys_to_keep = ['app_version']  # Keep some basic app info
    
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    
    # Reinitialize
    initialize_session_state()

def update_last_activity():
    """Update the last activity timestamp"""
    st.session_state.last_activity = datetime.now()

def get_session_duration():
    """Get the current session duration"""
    if 'session_start_time' in st.session_state:
        return datetime.now() - st.session_state.session_start_time
    return None

def save_chat_message(persona: str, user_message: str, ai_response: str):
    """Save a chat message to session state"""
    if 'chat_histories' not in st.session_state:
        st.session_state.chat_histories = {}
    
    if persona not in st.session_state.chat_histories:
        st.session_state.chat_histories[persona] = []
    
    message_entry = {
        'user_message': user_message,
        'ai_response': ai_response,
        'timestamp': datetime.now().isoformat(),
        'session_id': id(st.session_state)
    }
    
    st.session_state.chat_histories[persona].append(message_entry)
    update_last_activity()

def get_chat_history(persona: str) -> List[Dict[str, Any]]:
    """Get chat history for a specific persona"""
    if 'chat_histories' not in st.session_state:
        return []
    
    return st.session_state.chat_histories.get(persona, [])

def clear_chat_history(persona: str = None):
    """Clear chat history for a persona or all personas"""
    if 'chat_histories' not in st.session_state:
        return
    
    if persona:
        if persona in st.session_state.chat_histories:
            st.session_state.chat_histories[persona] = []
    else:
        st.session_state.chat_histories = {}

def add_error_message(message: str):
    """Add an error message to display"""
    if 'error_messages' not in st.session_state:
        st.session_state.error_messages = []
    
    st.session_state.error_messages.append({
        'message': message,
        'timestamp': datetime.now().isoformat()
    })

def add_success_message(message: str):
    """Add a success message to display"""
    if 'success_messages' not in st.session_state:
        st.session_state.success_messages = []
    
    st.session_state.success_messages.append({
        'message': message,
        'timestamp': datetime.now().isoformat()
    })

def clear_messages():
    """Clear all error and success messages"""
    st.session_state.error_messages = []
    st.session_state.success_messages = []

def set_loading_state(component: str, is_loading: bool):
    """Set loading state for a component"""
    if 'loading_states' not in st.session_state:
        st.session_state.loading_states = {}
    
    st.session_state.loading_states[component] = is_loading

def is_loading(component: str) -> bool:
    """Check if a component is in loading state"""
    if 'loading_states' not in st.session_state:
        return False
    
    return st.session_state.loading_states.get(component, False)

def save_memory_draft(text: str, memory_type: str, mood: str, tags: str):
    """Save a memory draft"""
    st.session_state.memory_draft = {
        'text': text,
        'type': memory_type,
        'mood': mood,
        'tags': tags,
        'saved_at': datetime.now().isoformat()
    }

def get_memory_draft() -> Dict[str, Any]:
    """Get the current memory draft"""
    return st.session_state.get('memory_draft', {
        'text': '',
        'type': 'diary',
        'mood': '😊 Happy',
        'tags': ''
    })

def clear_memory_draft():
    """Clear the memory draft"""
    st.session_state.memory_draft = {
        'text': '',
        'type': 'diary',
        'mood': '😊 Happy',
        'tags': ''
    }

def update_health_metric(metric_type: str, value: Any):
    """Update a health metric in session state"""
    if 'health_metrics' not in st.session_state:
        st.session_state.health_metrics = {}
    
    st.session_state.health_metrics[metric_type] = value
    st.session_state.health_metrics['last_updated'] = datetime.now().isoformat()

def get_health_metric(metric_type: str) -> Any:
    """Get a health metric from session state"""
    if 'health_metrics' not in st.session_state:
        return None
    
    return st.session_state.health_metrics.get(metric_type)

def start_game_session(game_type: str):
    """Start a new game session"""
    st.session_state.game_session = {
        'active': True,
        'game_type': game_type,
        'start_time': datetime.now().isoformat(),
        'current_score': 0,
        'level': 1,
        'moves': 0
    }

def update_game_score(score: int):
    """Update the current game score"""
    if 'game_session' in st.session_state and st.session_state.game_session.get('active'):
        st.session_state.game_session['current_score'] = score

def end_game_session() -> Dict[str, Any]:
    """End the current game session and return results"""
    if 'game_session' not in st.session_state or not st.session_state.game_session.get('active'):
        return {}
    
    session = st.session_state.game_session.copy()
    session['end_time'] = datetime.now().isoformat()
    session['active'] = False
    
    # Calculate duration
    if session.get('start_time'):
        start_time = datetime.fromisoformat(session['start_time'])
        end_time = datetime.fromisoformat(session['end_time'])
        session['duration_seconds'] = int((end_time - start_time).total_seconds())
    
    # Clear active session
    st.session_state.game_session = {
        'active': False,
        'start_time': None,
        'current_score': 0,
        'level': 1
    }
    
    return session

def add_reminder_notification(reminder_text: str, reminder_time: str):
    """Add a reminder notification"""
    if 'reminder_notifications' not in st.session_state:
        st.session_state.reminder_notifications = []
    
    notification = {
        'text': reminder_text,
        'time': reminder_time,
        'created_at': datetime.now().isoformat(),
        'shown': False
    }
    
    st.session_state.reminder_notifications.append(notification)

def get_pending_notifications() -> List[Dict[str, Any]]:
    """Get pending reminder notifications"""
    if 'reminder_notifications' not in st.session_state:
        return []
    
    return [n for n in st.session_state.reminder_notifications if not n.get('shown', False)]

def mark_notification_shown(index: int):
    """Mark a notification as shown"""
    if 'reminder_notifications' in st.session_state and index < len(st.session_state.reminder_notifications):
        st.session_state.reminder_notifications[index]['shown'] = True

def get_user_preferences() -> Dict[str, Any]:
    """Get user preferences"""
    return st.session_state.get('user_preferences', {
        'theme': 'light',
        'font_size': 'medium',
        'notifications': True,
        'auto_save': True
    })

def update_user_preferences(preferences: Dict[str, Any]):
    """Update user preferences"""
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {}
    
    st.session_state.user_preferences.update(preferences)

def get_session_stats() -> Dict[str, Any]:
    """Get session statistics"""
    duration = get_session_duration()
    
    return {
        'session_start': st.session_state.get('session_start_time'),
        'last_activity': st.session_state.get('last_activity'),
        'duration': duration,
        'user_name': st.session_state.get('user_name', ''),
        'current_page': st.session_state.get('current_page', 'home'),
        'chat_sessions': len(st.session_state.get('chat_histories', {})),
        'app_version': st.session_state.get('app_version', '1.0.0')
    }