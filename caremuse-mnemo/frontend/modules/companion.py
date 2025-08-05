import streamlit as st
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.api_client import APIClient
from utils.state import save_chat_message, get_chat_history

def show_companion_interface():
    """Main companion chat interface"""
    st.markdown("### 👥 Chat with Your Companions")
    st.markdown("Connect with your loving family members and caring AI companion.")
    
    # Persona selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_persona = st.selectbox(
            "Choose who you'd like to chat with:",
            options=["companion", "son", "daughter"],
            format_func=lambda x: get_persona_display_name(x),
            index=0,
            key="persona_selector"
        )
    
    with col2:
        if st.button("🔄 New Conversation"):
            # Clear current chat for this persona
            if f"chat_history_{selected_persona}" in st.session_state:
                st.session_state[f"chat_history_{selected_persona}"] = []
            st.rerun()
    
    # Store selected persona in session state
    st.session_state.selected_persona = selected_persona
    
    # Show persona info
    show_persona_info(selected_persona)
    
    # Chat interface
    show_chat_interface(selected_persona)

def get_persona_display_name(persona: str) -> str:
    """Get display name for persona"""
    names = {
        "companion": "🤖 AI Companion - Your caring digital friend",
        "son": "👨 Your Son - Loving and supportive",
        "daughter": "👩 Your Daughter - Warm and nurturing"
    }
    return names.get(persona, persona.title())

def show_persona_info(persona: str):
    """Show information about the selected persona"""
    persona_info = {
        "companion": {
            "description": "Your AI Companion is here to provide emotional support, encouragement, and friendly conversation. They remember your experiences and celebrate your daily achievements.",
            "emoji": "🤖",
            "color": "#667eea"
        },
        "son": {
            "description": "Your loving son who cares deeply about your wellbeing. He's proud of you and always ready to offer support and share in your joys.",
            "emoji": "👨",
            "color": "#4facfe"
        },
        "daughter": {
            "description": "Your caring daughter who cherishes every moment with you. She's nurturing, emotionally connected, and always there to listen with love.",
            "emoji": "👩",
            "color": "#f093fb"
        }
    }
    
    info = persona_info.get(persona, {})
    
    if info:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {info['color']}20, {info['color']}10); 
                    padding: 1rem; border-radius: 10px; margin: 1rem 0; 
                    border-left: 4px solid {info['color']};">
            <h4 style="margin: 0; color: {info['color']};">
                {info['emoji']} {get_persona_display_name(persona).split(' - ')[0]}
            </h4>
            <p style="margin: 0.5rem 0 0 0; color: #666;">
                {info['description']}
            </p>
        </div>
        """, unsafe_allow_html=True)

def show_chat_interface(persona: str):
    """Show the chat interface for the selected persona"""
    # Initialize chat history for this persona
    chat_key = f"chat_history_{persona}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []
    
    # Chat container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        if st.session_state[chat_key]:
            st.markdown("#### Conversation History")
            
            for i, message in enumerate(st.session_state[chat_key]):
                show_chat_message(message, persona, i)
        else:
            # Show welcome message for new conversation
            show_welcome_message(persona)
    
    # Chat input form
    with st.form(f"chat_form_{persona}", clear_on_submit=True):
        st.markdown("#### Send a Message")
        
        # Suggested prompts for first-time users
        if not st.session_state[chat_key]:
            show_suggested_prompts(persona)
        
        user_message = st.text_area(
            f"Message to {get_persona_display_name(persona).split(' - ')[0]}:",
            placeholder=get_message_placeholder(persona),
            height=100,
            key=f"message_input_{persona}"
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            submitted = st.form_submit_button("💬 Send Message", type="primary")
        
        with col2:
            if st.form_submit_button("🎯 Quick Check-in"):
                user_message = get_quick_checkin_message()
                submitted = True
        
        with col3:
            if st.form_submit_button("🌟 Share Good News"):
                user_message = "I have some good news to share with you!"
                submitted = True
        
        if submitted and user_message.strip():
            send_message_to_persona(persona, user_message.strip(), chat_key)

def show_welcome_message(persona: str):
    """Show welcome message for new conversations"""
    welcome_messages = {
        "companion": "Hello there! 🌟 I'm so glad to see you today. I'm here to listen, support, and celebrate with you. How are you feeling right now?",
        "son": "Hi Mom/Dad! 👋 It's wonderful to connect with you. I've been thinking about you and would love to hear how your day is going. What's new with you?",
        "daughter": "Hello, sweetheart! 💕 You always brighten my day. I'm here and ready to listen to whatever is on your heart. How are you doing today, my dear?"
    }
    
    message = welcome_messages.get(persona, "Hello! How can I help you today?")
    
    st.markdown(f"""
    <div class="ai-message fade-in">
        <strong>{get_persona_emoji(persona)} {get_persona_display_name(persona).split(' - ')[0]}:</strong>
        <p style="margin: 0.5rem 0 0 0;">{message}</p>
    </div>
    """, unsafe_allow_html=True)

def show_suggested_prompts(persona: str):
    """Show suggested conversation starters"""
    prompts = {
        "companion": [
            "How are you feeling today?",
            "Tell me about something good that happened",
            "I'd like to share a memory with you",
            "Can you help me feel better?"
        ],
        "son": [
            "How was your day, son?",
            "I'm proud of something I did today",
            "Do you remember when we...",
            "I've been thinking about family"
        ],
        "daughter": [
            "I had a lovely moment today",
            "Can you help me with something?",
            "I'm feeling grateful for...",
            "Tell me you love me"
        ]
    }
    
    persona_prompts = prompts.get(persona, [])
    
    if persona_prompts:
        st.markdown("**💡 Conversation starters:**")
        
        cols = st.columns(2)
        for i, prompt in enumerate(persona_prompts):
            col = cols[i % 2]
            with col:
                if st.button(f"💬 {prompt}", key=f"prompt_{persona}_{i}", use_container_width=True):
                    # Set the message and trigger send
                    st.session_state[f"message_input_{persona}"] = prompt
                    st.rerun()

def get_message_placeholder(persona: str) -> str:
    """Get placeholder text for message input"""
    placeholders = {
        "companion": "Share your thoughts, feelings, or experiences...",
        "son": "Tell your son what's on your mind...",
        "daughter": "Share with your daughter what's in your heart..."
    }
    return placeholders.get(persona, "Type your message here...")

def get_quick_checkin_message() -> str:
    """Get a quick check-in message"""
    return "Hi! I wanted to check in and let you know how I'm doing today."

def show_chat_message(message: dict, persona: str, index: int):
    """Display a chat message"""
    user_msg = message.get('user_message', '')
    ai_response = message.get('ai_response', '')
    timestamp = message.get('timestamp', '')
    
    # Format timestamp
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime("%I:%M %p")
        else:
            formatted_time = str(timestamp)
    except:
        formatted_time = "Just now"
    
    # User message
    st.markdown(f"""
    <div class="user-message">
        <strong>You ({formatted_time}):</strong>
        <p style="margin: 0.5rem 0 0 0;">{user_msg}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # AI response
    persona_emoji = get_persona_emoji(persona)
    persona_name = get_persona_display_name(persona).split(' - ')[0]
    
    st.markdown(f"""
    <div class="ai-message">
        <strong>{persona_emoji} {persona_name}:</strong>
        <p style="margin: 0.5rem 0 0 0;">{ai_response}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save as Memory", key=f"save_msg_{persona}_{index}"):
            save_message_as_memory(message, persona)
    
    with col2:
        if st.button("📋 Copy", key=f"copy_msg_{persona}_{index}"):
            combined_text = f"You: {user_msg}\n\n{persona_name}: {ai_response}"
            st.code(combined_text, language=None)
            st.success("Message copied!")
    
    with col3:
        if st.button("❤️ Favorite", key=f"fav_msg_{persona}_{index}"):
            # Add to favorites (could be implemented)
            st.success("Added to favorites!")

def send_message_to_persona(persona: str, message: str, chat_key: str):
    """Send message to persona and get response"""
    api_client = st.session_state.api_client
    
    with st.spinner(f"Getting response from {get_persona_display_name(persona).split(' - ')[0]}..."):
        try:
            # Send to API
            response = api_client.chat_with_persona(
                message=message,
                persona=persona,
                user_name=st.session_state.user_name
            )
            
            if response.get("response"):
                # Create message entry
                message_entry = {
                    'user_message': message,
                    'ai_response': response["response"],
                    'timestamp': datetime.now().isoformat(),
                    'persona': persona
                }
                
                # Add to session state
                st.session_state[chat_key].append(message_entry)
                
                # Also save to state utility
                save_chat_message(persona, message, response["response"])
                
                st.rerun()
            else:
                st.error("Failed to get response. Please try again.")
                
        except Exception as e:
            st.error(f"Error sending message: {e}")

def save_message_as_memory(message: dict, persona: str):
    """Save a chat message as a memory entry"""
    try:
        api_client = st.session_state.api_client
        
        user_msg = message.get('user_message', '')
        ai_response = message.get('ai_response', '')
        
        # Create memory text
        persona_name = get_persona_display_name(persona).split(' - ')[0]
        memory_text = f"Had a meaningful conversation with {persona_name}. I shared: '{user_msg}' and they responded with love and support: '{ai_response}'"
        
        # Store as memory
        result = api_client.store_memory(
            text=memory_text,
            memory_type="conversation",
            scope="personal",
            metadata={
                "original_persona": persona,
                "conversation_type": "family_chat",
                "user_name": st.session_state.user_name
            }
        )
        
        if result.get("status") == "success":
            st.success("✅ Conversation saved as a cherished memory!")
        else:
            st.error("Failed to save conversation as memory.")
            
    except Exception as e:
        st.error(f"Error saving conversation: {e}")

def get_persona_emoji(persona: str) -> str:
    """Get emoji for persona"""
    emojis = {
        "companion": "🤖",
        "son": "👨",
        "daughter": "👩"
    }
    return emojis.get(persona, "💬")

def show_conversation_stats(persona: str):
    """Show conversation statistics for this persona"""
    try:
        api_client = st.session_state.api_client
        
        # Get recent conversations with this persona
        conversations = api_client.get_chat_history(persona=persona, days=30, limit=100)
        
        if conversations:
            st.markdown(f"#### 📊 Your conversations with {get_persona_display_name(persona).split(' - ')[0]}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Chats", len(conversations))
            
            with col2:
                # Calculate average response length
                total_length = sum(len(conv.get('ai_response', '')) for conv in conversations)
                avg_length = total_length / len(conversations) if conversations else 0
                st.metric("Avg Response Length", f"{avg_length:.0f} chars")
            
            with col3:
                # Find most recent conversation
                if conversations:
                    latest = conversations[0].get('timestamp', '')
                    try:
                        dt = datetime.fromisoformat(latest.replace('Z', '+00:00'))
                        days_ago = (datetime.now() - dt).days
                        st.metric("Last Chat", f"{days_ago} days ago" if days_ago > 0 else "Today")
                    except:
                        st.metric("Last Chat", "Recently")
        
    except Exception as e:
        st.error(f"Error loading conversation stats: {e}")

def export_persona_conversations(persona: str):
    """Export conversations with a specific persona"""
    try:
        api_client = st.session_state.api_client
        
        conversations = api_client.get_chat_history(persona=persona, days=365, limit=1000)
        
        if conversations:
            # Format for export
            export_lines = []
            export_lines.append(f"Conversations with {get_persona_display_name(persona)}")
            export_lines.append("=" * 50)
            export_lines.append(f"Exported on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
            export_lines.append(f"Total conversations: {len(conversations)}")
            export_lines.append("")
            
            for i, conv in enumerate(conversations, 1):
                user_msg = conv.get('user_message', '')
                ai_msg = conv.get('ai_response', '')
                timestamp = conv.get('timestamp', '')
                
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%B %d, %Y at %I:%M %p')
                except:
                    formatted_time = "Unknown time"
                
                export_lines.append(f"Conversation #{i}")
                export_lines.append(f"Date: {formatted_time}")
                export_lines.append("-" * 30)
                export_lines.append(f"You: {user_msg}")
                export_lines.append(f"{get_persona_display_name(persona).split(' - ')[0]}: {ai_msg}")
                export_lines.append("")
            
            export_text = "\n".join(export_lines)
            
            st.download_button(
                label=f"📥 Download {get_persona_display_name(persona).split(' - ')[0]} Conversations",
                data=export_text,
                file_name=f"{persona}_conversations_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
            
        else:
            st.info(f"No conversations found with {get_persona_display_name(persona).split(' - ')[0]}")
            
    except Exception as e:
        st.error(f"Error exporting conversations: {e}")