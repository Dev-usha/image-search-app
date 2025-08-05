import streamlit as st
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.api_client import APIClient

def show_chat_history_interface():
    """Main chat history interface"""
    st.markdown("### 📜 Chat History")
    st.markdown("View and search through your past conversations with all personas.")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["🔍 Search Conversations", "📊 Chat Statistics", "📋 All Conversations"])
    
    with tab1:
        show_conversation_search()
    
    with tab2:
        show_chat_statistics()
    
    with tab3:
        show_all_conversations()

def show_conversation_search():
    """Interface for searching conversations"""
    st.markdown("#### 🔍 Search Your Conversations")
    
    # Search form
    with st.form("conversation_search_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            search_query = st.text_input(
                "Search for...",
                placeholder="Enter keywords to search conversations...",
                help="Search through all your conversation history"
            )
        
        with col2:
            persona_filter = st.selectbox(
                "Filter by Persona",
                options=["All", "companion", "son", "daughter", "doctor", "nurse", "therapist"],
                help="Filter by specific persona"
            )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            days_back = st.selectbox(
                "Time Period",
                options=[7, 30, 90, 365, 0],
                format_func=lambda x: f"Last {x} days" if x > 0 else "All time",
                index=2,
                help="How far back to search"
            )
        
        with col2:
            max_results = st.selectbox(
                "Max Results",
                options=[10, 25, 50, 100],
                index=1,
                help="Maximum number of results to show"
            )
        
        with col3:
            submitted = st.form_submit_button("🔍 Search", type="primary")
    
    if submitted and search_query:
        search_conversations(search_query, persona_filter, days_back, max_results)

def search_conversations(query, persona_filter, days_back, max_results):
    """Search for conversations"""
    try:
        api_client = st.session_state.api_client
        
        with st.spinner("Searching your conversations..."):
            # Use search endpoint if available, otherwise filter results
            if hasattr(api_client, 'search_conversations'):
                persona = None if persona_filter == "All" else persona_filter
                results = api_client.search_conversations(
                    query=query,
                    persona=persona,
                    days=days_back if days_back > 0 else 365,
                    limit=max_results
                )
            else:
                # Fallback: get all conversations and filter
                persona = None if persona_filter == "All" else persona_filter
                all_conversations = api_client.get_chat_history(
                    persona=persona,
                    days=days_back if days_back > 0 else 365,
                    limit=max_results * 2
                )
                
                # Simple text search
                query_lower = query.lower()
                results = []
                for conv in all_conversations:
                    user_msg = conv.get('user_message', '').lower()
                    ai_msg = conv.get('ai_response', '').lower()
                    if query_lower in user_msg or query_lower in ai_msg:
                        results.append(conv)
                
                results = results[:max_results]
        
        if results:
            st.success(f"Found {len(results)} conversations matching '{query}'")
            
            for i, conversation in enumerate(results):
                show_conversation_card(conversation, f"search_{i}", highlight_query=query)
        else:
            st.info(f"No conversations found matching '{query}'. Try different keywords or adjust your filters.")
            
    except Exception as e:
        st.error(f"Error searching conversations: {e}")

def show_chat_statistics():
    """Show chat statistics and analytics"""
    st.markdown("#### 📊 Chat Statistics")
    
    try:
        api_client = st.session_state.api_client
        
        # Time period selector
        col1, col2 = st.columns(2)
        
        with col1:
            analysis_period = st.selectbox(
                "Analysis Period",
                options=[7, 30, 90, 365],
                format_func=lambda x: f"Last {x} days",
                index=1,
                key="stats_period"
            )
        
        with col2:
            if st.button("Refresh Statistics"):
                st.rerun()
        
        # Get conversation statistics
        if hasattr(api_client, 'get_conversation_stats'):
            stats = api_client.get_conversation_stats(days=analysis_period)
        else:
            # Fallback: calculate stats manually
            stats = calculate_conversation_stats(api_client, analysis_period)
        
        if stats:
            # Overall metrics
            st.markdown("##### Overall Activity")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Conversations", stats.get('total_conversations', 0))
            
            with col2:
                avg_length = stats.get('average_response_length', 0)
                st.metric("Avg Response Length", f"{avg_length:.0f} chars")
            
            with col3:
                persona_count = len(stats.get('persona_breakdown', {}))
                st.metric("Active Personas", persona_count)
            
            with col4:
                daily_avg = stats.get('total_conversations', 0) / analysis_period
                st.metric("Daily Average", f"{daily_avg:.1f}")
            
            # Persona breakdown
            if stats.get('persona_breakdown'):
                st.markdown("##### Conversations by Persona")
                
                persona_data = stats['persona_breakdown']
                persona_names = list(persona_data.keys())
                persona_counts = list(persona_data.values())
                
                # Create a simple bar chart using columns
                for persona, count in persona_data.items():
                    persona_emoji = get_persona_emoji(persona)
                    percentage = (count / stats['total_conversations']) * 100 if stats['total_conversations'] > 0 else 0
                    
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.markdown(f"{persona_emoji} {persona.title()}")
                    with col2:
                        st.progress(percentage / 100)
                        st.markdown(f"{count} conversations ({percentage:.1f}%)")
            
            # Daily activity
            if stats.get('daily_activity'):
                st.markdown("##### Daily Activity")
                
                daily_data = stats['daily_activity']
                if daily_data:
                    # Show recent days
                    recent_days = sorted(daily_data.items(), reverse=True)[:7]
                    
                    for date_str, count in recent_days:
                        try:
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                            formatted_date = date_obj.strftime('%B %d, %Y')
                        except:
                            formatted_date = date_str
                        
                        st.markdown(f"- **{formatted_date}:** {count} conversations")
            
            # Most active hours (if available)
            if stats.get('most_active_hours'):
                st.markdown("##### Most Active Hours")
                
                hourly_data = stats['most_active_hours']
                top_hours = sorted(hourly_data.items(), key=lambda x: x[1], reverse=True)[:5]
                
                for hour, count in top_hours:
                    hour_12 = datetime.strptime(f"{hour}:00", "%H:%M").strftime("%I:%M %p")
                    st.markdown(f"- **{hour_12}:** {count} conversations")
        
        else:
            st.info("No conversation statistics available yet. Start chatting to see your activity patterns!")
            
    except Exception as e:
        st.error(f"Error loading chat statistics: {e}")

def calculate_conversation_stats(api_client, days):
    """Calculate conversation statistics manually"""
    try:
        # Get all conversations for the period
        conversations = api_client.get_chat_history(days=days, limit=1000)
        
        if not conversations:
            return {}
        
        # Calculate basic stats
        total_conversations = len(conversations)
        
        # Persona breakdown
        persona_breakdown = {}
        total_response_length = 0
        daily_activity = {}
        
        for conv in conversations:
            # Persona stats
            persona = conv.get('persona', 'unknown')
            persona_breakdown[persona] = persona_breakdown.get(persona, 0) + 1
            
            # Response length
            response = conv.get('ai_response', '')
            total_response_length += len(response)
            
            # Daily activity
            timestamp = conv.get('timestamp', '')
            try:
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    date_str = dt.strftime('%Y-%m-%d')
                    daily_activity[date_str] = daily_activity.get(date_str, 0) + 1
            except:
                pass
        
        avg_response_length = total_response_length / total_conversations if total_conversations > 0 else 0
        
        return {
            'total_conversations': total_conversations,
            'persona_breakdown': persona_breakdown,
            'average_response_length': avg_response_length,
            'daily_activity': daily_activity,
            'analysis_period_days': days
        }
        
    except Exception as e:
        print(f"Error calculating stats: {e}")
        return {}

def show_all_conversations():
    """Show all conversations with filtering"""
    st.markdown("#### 📋 All Conversations")
    
    # Filter controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        persona_filter = st.selectbox(
            "Persona",
            options=["All", "companion", "son", "daughter", "doctor", "nurse", "therapist"],
            key="all_persona_filter",
            help="Filter by persona"
        )
    
    with col2:
        days_filter = st.selectbox(
            "Time Period",
            options=[7, 30, 90, 365],
            format_func=lambda x: f"Last {x} days",
            index=1,
            key="all_days_filter"
        )
    
    with col3:
        limit_filter = st.selectbox(
            "Show",
            options=[25, 50, 100, 200],
            index=1,
            key="all_limit_filter",
            help="Number of conversations to display"
        )
    
    with col4:
        if st.button("Refresh", key="refresh_all"):
            st.rerun()
    
    # Get conversations
    try:
        api_client = st.session_state.api_client
        
        persona = None if persona_filter == "All" else persona_filter
        conversations = api_client.get_chat_history(
            persona=persona,
            days=days_filter,
            limit=limit_filter
        )
        
        if conversations:
            st.markdown(f"Showing {len(conversations)} conversations")
            
            # Group conversations by date
            grouped_conversations = group_conversations_by_date(conversations)
            
            for date_str, date_conversations in grouped_conversations.items():
                st.markdown(f"##### {date_str}")
                
                for i, conversation in enumerate(date_conversations):
                    show_conversation_card(conversation, f"all_{date_str}_{i}")
        else:
            st.info("No conversations found with the current filters. Try adjusting your selection or start a new conversation!")
            
    except Exception as e:
        st.error(f"Error loading conversations: {e}")

def group_conversations_by_date(conversations):
    """Group conversations by date"""
    grouped = {}
    
    for conv in conversations:
        timestamp = conv.get('timestamp', '')
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                date_str = dt.strftime('%B %d, %Y')
            else:
                date_str = "Unknown Date"
        except:
            date_str = "Unknown Date"
        
        if date_str not in grouped:
            grouped[date_str] = []
        grouped[date_str].append(conv)
    
    # Sort by date (most recent first)
    return dict(sorted(grouped.items(), key=lambda x: x[0], reverse=True))

def show_conversation_card(conversation, key_suffix, highlight_query=None):
    """Display a conversation card"""
    persona = conversation.get('persona', 'unknown')
    user_message = conversation.get('user_message', '')
    ai_response = conversation.get('ai_response', '')
    timestamp = conversation.get('timestamp', 'Unknown time')
    
    # Format timestamp
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime("%I:%M %p")
        else:
            formatted_time = str(timestamp)
    except:
        formatted_time = str(timestamp)
    
    persona_emoji = get_persona_emoji(persona)
    
    # Highlight search query if provided
    display_user_msg = user_message
    display_ai_msg = ai_response
    
    if highlight_query:
        # Simple highlighting (could be improved with proper HTML highlighting)
        query_lower = highlight_query.lower()
        if query_lower in user_message.lower():
            # Mark as highlighted (basic approach)
            display_user_msg = f"🔍 {user_message}"
        if query_lower in ai_response.lower():
            display_ai_msg = f"🔍 {ai_response}"
    
    with st.expander(f"{persona_emoji} {persona.title()} - {formatted_time}", expanded=False):
        st.markdown("**Your Message:**")
        st.markdown(f"> {display_user_msg}")
        
        st.markdown(f"**{persona.title()}'s Response:**")
        st.info(display_ai_msg)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💬 Continue Chat", key=f"continue_{key_suffix}"):
                # Set up to continue this conversation
                st.session_state.selected_persona = persona
                st.session_state.current_page = "chat"
                st.rerun()
        
        with col2:
            if st.button("📋 Copy Text", key=f"copy_{key_suffix}"):
                combined_text = f"You: {user_message}\n\n{persona.title()}: {ai_response}"
                st.code(combined_text, language=None)
                st.success("Conversation text ready to copy!")
        
        with col3:
            if st.button("💾 Save as Memory", key=f"save_{key_suffix}"):
                save_conversation_as_memory(conversation, key_suffix)

def save_conversation_as_memory(conversation, key_suffix):
    """Save conversation as a memory entry"""
    try:
        api_client = st.session_state.api_client
        
        persona = conversation.get('persona', 'unknown')
        user_message = conversation.get('user_message', '')
        ai_response = conversation.get('ai_response', '')
        
        # Create memory text
        memory_text = f"Had a conversation with {persona}. I asked: '{user_message}' and they responded: '{ai_response}'"
        
        # Store as memory
        result = api_client.store_memory(
            text=memory_text,
            memory_type="conversation",
            scope="personal",
            metadata={
                "original_persona": persona,
                "conversation_type": "saved_from_history",
                "user_name": st.session_state.user_name
            }
        )
        
        if result.get("status") == "success":
            st.success("✅ Conversation saved as memory!")
        else:
            st.error("Failed to save conversation as memory.")
            
    except Exception as e:
        st.error(f"Error saving conversation: {e}")

def get_persona_emoji(persona):
    """Get emoji for persona"""
    emoji_map = {
        "companion": "🤖",
        "son": "👨",
        "daughter": "👩",
        "doctor": "🩺",
        "nurse": "👩‍⚕️",
        "therapist": "🧠"
    }
    return emoji_map.get(persona, "💬")

def export_chat_history():
    """Export chat history functionality"""
    st.markdown("#### 📤 Export Chat History")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_persona = st.selectbox(
            "Export Persona",
            options=["All", "companion", "son", "daughter", "doctor", "nurse", "therapist"],
            help="Choose which persona's conversations to export"
        )
    
    with col2:
        export_days = st.selectbox(
            "Time Period",
            options=[30, 90, 365, 0],
            format_func=lambda x: f"Last {x} days" if x > 0 else "All time",
            help="How far back to export"
        )
    
    if st.button("📤 Export Conversations", type="primary"):
        try:
            api_client = st.session_state.api_client
            
            persona = None if export_persona == "All" else export_persona
            conversations = api_client.get_chat_history(
                persona=persona,
                days=export_days if export_days > 0 else 365,
                limit=10000
            )
            
            if conversations:
                # Format for export
                export_text = format_conversations_for_export(conversations)
                
                st.download_button(
                    label="💾 Download Chat History",
                    data=export_text,
                    file_name=f"chat_history_{export_persona}_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
                
                st.success(f"Ready to download {len(conversations)} conversations!")
            else:
                st.info("No conversations found to export.")
                
        except Exception as e:
            st.error(f"Error exporting conversations: {e}")

def format_conversations_for_export(conversations):
    """Format conversations for text export"""
    export_lines = []
    export_lines.append("CareMuse + Mnemo Chat History Export")
    export_lines.append("=" * 50)
    export_lines.append(f"Exported on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    export_lines.append(f"Total conversations: {len(conversations)}")
    export_lines.append("")
    
    for i, conv in enumerate(conversations, 1):
        persona = conv.get('persona', 'Unknown')
        user_msg = conv.get('user_message', '')
        ai_msg = conv.get('ai_response', '')
        timestamp = conv.get('timestamp', '')
        
        # Format timestamp
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                formatted_time = dt.strftime('%B %d, %Y at %I:%M %p')
            else:
                formatted_time = str(timestamp)
        except:
            formatted_time = "Unknown time"
        
        export_lines.append(f"Conversation #{i}")
        export_lines.append(f"Date: {formatted_time}")
        export_lines.append(f"Persona: {persona.title()}")
        export_lines.append("-" * 30)
        export_lines.append(f"You: {user_msg}")
        export_lines.append(f"{persona.title()}: {ai_msg}")
        export_lines.append("")
    
    return "\n".join(export_lines)