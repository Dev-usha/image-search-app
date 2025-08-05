import streamlit as st
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.api_client import APIClient

def show_memory_interface():
    """Main memory journal interface"""
    st.markdown("### 💭 Memory Journal")
    st.markdown("Capture your thoughts, experiences, and daily moments here.")
    
    # Tabs for different memory functions
    tab1, tab2, tab3 = st.tabs(["✍️ New Entry", "📖 Recent Memories", "🔍 Search Memories"])
    
    with tab1:
        show_new_memory_entry()
    
    with tab2:
        show_recent_memories()
    
    with tab3:
        show_memory_search()

def show_new_memory_entry():
    """Interface for creating new memory entries"""
    st.markdown("#### Write a New Memory")
    
    # Memory entry form
    with st.form("memory_entry_form"):
        # Memory text
        memory_text = st.text_area(
            "What's on your mind?",
            placeholder="Share your thoughts, experiences, or anything you'd like to remember...",
            height=150,
            help="Write about your day, feelings, experiences, or anything meaningful to you."
        )
        
        # Memory type selection
        col1, col2 = st.columns(2)
        
        with col1:
            memory_type = st.selectbox(
                "Memory Type",
                options=[
                    "diary",
                    "experience",
                    "thought",
                    "gratitude",
                    "achievement",
                    "social",
                    "learning",
                    "reflection"
                ],
                help="Choose the type that best describes your memory"
            )
        
        with col2:
            mood = st.selectbox(
                "How are you feeling?",
                options=[
                    "😊 Happy",
                    "😌 Content",
                    "😐 Neutral",
                    "🤔 Thoughtful",
                    "😔 Sad",
                    "😟 Worried",
                    "😴 Tired",
                    "😤 Frustrated",
                    "🥰 Loved",
                    "🎉 Excited"
                ],
                help="Your current mood helps provide context"
            )
        
        # Tags for better organization
        tags = st.text_input(
            "Tags (optional)",
            placeholder="family, friends, health, hobbies, etc.",
            help="Add comma-separated tags to help organize your memories"
        )
        
        # Submit button
        submitted = st.form_submit_button("Save Memory", type="primary", use_container_width=True)
        
        if submitted:
            if memory_text.strip():
                save_memory_entry(memory_text, memory_type, mood, tags)
            else:
                st.error("Please write something before saving your memory.")

def save_memory_entry(text, memory_type, mood, tags):
    """Save a new memory entry"""
    try:
        api_client = st.session_state.api_client
        
        # Prepare metadata
        metadata = {
            "mood": mood,
            "user_name": st.session_state.user_name,
            "entry_date": datetime.now().isoformat()
        }
        
        # Add tags if provided
        if tags.strip():
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
            metadata["tags"] = tag_list
        
        # Store the memory
        result = api_client.store_memory(
            text=text,
            memory_type=memory_type,
            scope="personal",
            metadata=metadata
        )
        
        if result.get("status") == "success":
            st.success("✅ Memory saved successfully!")
            st.balloons()
            
            # Show a preview of what was saved
            with st.expander("Memory Preview", expanded=True):
                st.markdown(f"**Type:** {memory_type}")
                st.markdown(f"**Mood:** {mood}")
                st.markdown(f"**Content:** {text}")
                if tags.strip():
                    st.markdown(f"**Tags:** {tags}")
        else:
            st.error("Failed to save memory. Please try again.")
            
    except Exception as e:
        st.error(f"Error saving memory: {e}")

def show_recent_memories():
    """Show recent memory entries"""
    st.markdown("#### Your Recent Memories")
    
    try:
        api_client = st.session_state.api_client
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            memory_type_filter = st.selectbox(
                "Filter by Type",
                options=["All", "diary", "experience", "thought", "gratitude", "achievement", "social", "learning", "reflection"],
                key="recent_type_filter"
            )
        
        with col2:
            limit = st.selectbox(
                "Number to Show",
                options=[10, 20, 50, 100],
                index=1,
                key="recent_limit"
            )
        
        with col3:
            if st.button("Refresh", key="refresh_recent"):
                st.rerun()
        
        # Get memories
        filter_type = None if memory_type_filter == "All" else memory_type_filter
        memories = api_client.get_memories(
            scope="personal",
            memory_type=filter_type,
            limit=limit
        )
        
        if memories:
            st.markdown(f"Found {len(memories)} memories")
            
            for i, memory in enumerate(memories):
                show_memory_card(memory, i)
        else:
            st.info("No memories found. Start by writing your first memory entry!")
            
    except Exception as e:
        st.error(f"Error loading memories: {e}")

def show_memory_search():
    """Interface for searching memories"""
    st.markdown("#### Search Your Memories")
    
    # Search form
    search_query = st.text_input(
        "Search for...",
        placeholder="Enter keywords to search your memories...",
        help="Search through all your saved memories"
    )
    
    if search_query:
        try:
            api_client = st.session_state.api_client
            
            # Search memories
            results = api_client.search_memories(
                query=search_query,
                scope="personal",
                limit=20
            )
            
            if results:
                st.markdown(f"Found {len(results)} memories matching '{search_query}'")
                
                for i, memory in enumerate(results):
                    show_memory_card(memory, f"search_{i}")
            else:
                st.info(f"No memories found matching '{search_query}'. Try different keywords.")
                
        except Exception as e:
            st.error(f"Error searching memories: {e}")

def show_memory_card(memory, key_suffix):
    """Display a memory card"""
    timestamp = memory.get('timestamp', 'Unknown time')
    text = memory.get('text', '')
    memory_type = memory.get('memory_type', 'general')
    metadata = memory.get('metadata', {})
    
    # Format timestamp
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime("%B %d, %Y at %I:%M %p")
        else:
            formatted_time = str(timestamp)
    except:
        formatted_time = str(timestamp)
    
    # Create expandable memory card
    with st.expander(f"💭 {memory_type.title()} - {formatted_time}", expanded=False):
        st.markdown(f"**Content:** {text}")
        
        # Show metadata if available
        if metadata:
            col1, col2 = st.columns(2)
            
            with col1:
                if 'mood' in metadata:
                    st.markdown(f"**Mood:** {metadata['mood']}")
                if 'tags' in metadata:
                    tags_str = ", ".join(metadata['tags'])
                    st.markdown(f"**Tags:** {tags_str}")
            
            with col2:
                if 'user_name' in metadata:
                    st.markdown(f"**Author:** {metadata['user_name']}")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💬 Chat About This", key=f"chat_{key_suffix}"):
                # Store this memory for chat context
                st.session_state.selected_memory = memory
                st.session_state.current_page = "chat"
                st.rerun()
        
        with col2:
            if st.button("📋 Copy Text", key=f"copy_{key_suffix}"):
                st.code(text, language=None)
                st.success("Text ready to copy!")
        
        with col3:
            if st.button("🏷️ Add Tags", key=f"tag_{key_suffix}"):
                show_tag_editor(memory, key_suffix)

def show_tag_editor(memory, key_suffix):
    """Show interface to edit tags for a memory"""
    current_tags = memory.get('metadata', {}).get('tags', [])
    
    with st.form(f"tag_form_{key_suffix}"):
        new_tags = st.text_input(
            "Edit Tags",
            value=", ".join(current_tags) if current_tags else "",
            help="Add comma-separated tags"
        )
        
        if st.form_submit_button("Update Tags"):
            # This would require an update memory endpoint
            st.info("Tag updating functionality coming soon!")

def show_memory_stats():
    """Show memory statistics"""
    try:
        api_client = st.session_state.api_client
        
        # Get all memories for stats
        all_memories = api_client.get_memories(scope="personal", limit=1000)
        
        if all_memories:
            # Count by type
            type_counts = {}
            mood_counts = {}
            
            for memory in all_memories:
                memory_type = memory.get('memory_type', 'unknown')
                type_counts[memory_type] = type_counts.get(memory_type, 0) + 1
                
                metadata = memory.get('metadata', {})
                if 'mood' in metadata:
                    mood = metadata['mood']
                    mood_counts[mood] = mood_counts.get(mood, 0) + 1
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Memory Types**")
                for mem_type, count in sorted(type_counts.items()):
                    st.markdown(f"- {mem_type.title()}: {count}")
            
            with col2:
                st.markdown("**Mood Distribution**")
                for mood, count in sorted(mood_counts.items()):
                    st.markdown(f"- {mood}: {count}")
        
    except Exception as e:
        st.error(f"Error loading memory stats: {e}")

# Helper function to format memory types
def get_memory_type_emoji(memory_type):
    """Get emoji for memory type"""
    emoji_map = {
        "diary": "📔",
        "experience": "🌟",
        "thought": "💭",
        "gratitude": "🙏",
        "achievement": "🏆",
        "social": "👥",
        "learning": "📚",
        "reflection": "🤔"
    }
    return emoji_map.get(memory_type, "💭")