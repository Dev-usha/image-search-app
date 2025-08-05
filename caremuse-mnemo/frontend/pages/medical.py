import streamlit as st
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.api_client import APIClient

def show_medical_interface():
    """Main medical center interface"""
    st.markdown("### 🏥 Medical Center")
    st.markdown("Upload medical documents and chat with healthcare professionals.")
    
    # Tabs for different medical functions
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Upload Documents", "🩺 Chat with Doctor", "👩‍⚕️ Chat with Nurse", "📊 Medical History"])
    
    with tab1:
        show_document_upload()
    
    with tab2:
        show_doctor_chat()
    
    with tab3:
        show_nurse_chat()
    
    with tab4:
        show_medical_history()

def show_document_upload():
    """Interface for uploading medical documents"""
    st.markdown("#### 📄 Upload Medical Documents")
    st.markdown("Upload your medical reports, prescriptions, lab results, and other healthcare documents.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a medical document",
        type=['pdf', 'jpg', 'jpeg', 'png', 'docx', 'txt'],
        help="Supported formats: PDF, Images (JPG, PNG), Word documents, Text files"
    )
    
    if uploaded_file is not None:
        # Show file details
        st.markdown("##### File Details")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**Name:** {uploaded_file.name}")
        with col2:
            st.markdown(f"**Size:** {uploaded_file.size / 1024:.1f} KB")
        with col3:
            st.markdown(f"**Type:** {uploaded_file.type}")
        
        # Processing options
        st.markdown("##### Processing Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            document_type = st.selectbox(
                "Document Type",
                options=[
                    "Lab Results",
                    "Prescription",
                    "Medical Report",
                    "X-Ray/Imaging",
                    "Discharge Summary",
                    "Insurance Document",
                    "Other Medical Document"
                ],
                help="Select the type of medical document"
            )
        
        with col2:
            add_notes = st.text_area(
                "Additional Notes (Optional)",
                placeholder="Add any additional context about this document...",
                height=100
            )
        
        # Upload button
        if st.button("🔄 Process Document", type="primary", use_container_width=True):
            process_medical_document(uploaded_file, document_type, add_notes)

def process_medical_document(uploaded_file, document_type, notes):
    """Process uploaded medical document"""
    try:
        api_client = st.session_state.api_client
        
        with st.spinner("Processing your medical document..."):
            # Upload and process the file
            result = api_client.upload_medical_document(uploaded_file)
            
            if result.get("status") == "success":
                st.success("✅ Document processed successfully!")
                
                # Show processing results
                with st.expander("📋 Processing Results", expanded=True):
                    # Summary
                    if result.get("summary"):
                        st.markdown("**AI Summary:**")
                        st.info(result["summary"])
                    
                    # Extracted text preview
                    if result.get("extracted_text"):
                        st.markdown("**Extracted Text Preview:**")
                        preview_text = result["extracted_text"][:500]
                        if len(result["extracted_text"]) > 500:
                            preview_text += "..."
                        st.text_area("", value=preview_text, height=150, disabled=True)
                    
                    # File information
                    st.markdown("**File Information:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"- **Type:** {document_type}")
                        st.markdown(f"- **File Type:** {result.get('file_type', 'Unknown')}")
                    with col2:
                        st.markdown(f"- **Text Length:** {result.get('text_length', 0)} characters")
                        st.markdown(f"- **Memory ID:** {result.get('memory_id', 'N/A')}")
                
                # Success actions
                st.markdown("### What would you like to do next?")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("🩺 Discuss with Doctor"):
                        st.session_state.current_page = "medical"
                        st.session_state.active_medical_tab = 1  # Doctor chat tab
                        st.rerun()
                
                with col2:
                    if st.button("👩‍⚕️ Ask Nurse"):
                        st.session_state.current_page = "medical"
                        st.session_state.active_medical_tab = 2  # Nurse chat tab
                        st.rerun()
                
                with col3:
                    if st.button("📊 View History"):
                        st.session_state.current_page = "medical"
                        st.session_state.active_medical_tab = 3  # History tab
                        st.rerun()
            else:
                st.error("Failed to process document. Please try again.")
                
    except Exception as e:
        st.error(f"Error processing document: {e}")

def show_doctor_chat():
    """Interface for chatting with doctor persona"""
    st.markdown("#### 🩺 Chat with Dr. Smith")
    st.markdown("Discuss your medical documents and health concerns with your doctor.")
    
    # Chat interface
    show_medical_chat_interface("doctor", "Dr. Smith", "🩺")

def show_nurse_chat():
    """Interface for chatting with nurse persona"""
    st.markdown("#### 👩‍⚕️ Chat with Nurse Johnson")
    st.markdown("Get practical health advice and support from your nurse.")
    
    # Chat interface
    show_medical_chat_interface("nurse", "Nurse Johnson", "👩‍⚕️")

def show_medical_chat_interface(persona, persona_name, emoji):
    """Generic medical chat interface"""
    # Initialize chat history for this persona
    chat_key = f"medical_chat_{persona}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []
    
    # Chat container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for i, message in enumerate(st.session_state[chat_key]):
            if message["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="ai-message">
                    <strong>{emoji} {persona_name}:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    with st.form(f"chat_form_{persona}", clear_on_submit=True):
        user_message = st.text_area(
            f"Message {persona_name}",
            placeholder=f"Ask {persona_name} about your health, medications, or medical documents...",
            height=100,
            key=f"message_input_{persona}"
        )
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            submitted = st.form_submit_button("Send Message", type="primary")
        
        with col2:
            if st.form_submit_button("Clear Chat"):
                st.session_state[chat_key] = []
                st.rerun()
        
        if submitted and user_message.strip():
            send_medical_message(persona, persona_name, user_message, chat_key)

def send_medical_message(persona, persona_name, message, chat_key):
    """Send message to medical persona"""
    try:
        api_client = st.session_state.api_client
        
        # Add user message to chat history
        st.session_state[chat_key].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        with st.spinner(f"Getting response from {persona_name}..."):
            # Send to API
            response = api_client.chat_with_persona(
                message=message,
                persona=persona,
                user_name=st.session_state.user_name
            )
            
            if response.get("response"):
                # Add AI response to chat history
                st.session_state[chat_key].append({
                    "role": "assistant",
                    "content": response["response"],
                    "timestamp": datetime.now().isoformat()
                })
                
                st.rerun()
            else:
                st.error("Failed to get response. Please try again.")
                
    except Exception as e:
        st.error(f"Error sending message: {e}")

def show_medical_history():
    """Show medical document history and health records"""
    st.markdown("#### 📊 Medical History")
    
    # Tabs for different views
    history_tab1, history_tab2, history_tab3 = st.tabs(["📄 Documents", "💬 Chat History", "📈 Health Stats"])
    
    with history_tab1:
        show_medical_documents()
    
    with history_tab2:
        show_medical_chat_history()
    
    with history_tab3:
        show_health_statistics()

def show_medical_documents():
    """Show uploaded medical documents"""
    st.markdown("##### Your Medical Documents")
    
    try:
        api_client = st.session_state.api_client
        
        # Get medical memories (documents)
        medical_memories = api_client.get_memories(
            scope="medical",
            memory_type="medical_report",
            limit=50
        )
        
        if medical_memories:
            st.markdown(f"Found {len(medical_memories)} medical documents")
            
            for i, document in enumerate(medical_memories):
                show_medical_document_card(document, i)
        else:
            st.info("No medical documents uploaded yet. Use the 'Upload Documents' tab to add your first document.")
            
    except Exception as e:
        st.error(f"Error loading medical documents: {e}")

def show_medical_document_card(document, index):
    """Display a medical document card"""
    timestamp = document.get('timestamp', 'Unknown time')
    text = document.get('text', '')  # This is the summary
    metadata = document.get('metadata', {})
    
    # Format timestamp
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime("%B %d, %Y at %I:%M %p")
        else:
            formatted_time = str(timestamp)
    except:
        formatted_time = str(timestamp)
    
    filename = metadata.get('filename', 'Unknown Document')
    file_type = metadata.get('file_type', 'unknown')
    
    with st.expander(f"📄 {filename} - {formatted_time}", expanded=False):
        # Document summary
        st.markdown("**AI Summary:**")
        st.info(text)
        
        # Document details
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**File Type:** {file_type}")
            st.markdown(f"**Upload Date:** {formatted_time}")
        
        with col2:
            if 'text_length' in metadata:
                st.markdown(f"**Text Length:** {metadata['text_length']} characters")
        
        # Show extracted text if available
        if 'extracted_text' in metadata:
            with st.expander("View Full Extracted Text"):
                st.text_area("", value=metadata['extracted_text'], height=200, disabled=True)
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🩺 Discuss with Doctor", key=f"doc_doctor_{index}"):
                st.session_state.selected_document = document
                st.session_state.current_page = "medical"
                st.session_state.active_medical_tab = 1
                st.rerun()
        
        with col2:
            if st.button("👩‍⚕️ Ask Nurse", key=f"doc_nurse_{index}"):
                st.session_state.selected_document = document
                st.session_state.current_page = "medical"
                st.session_state.active_medical_tab = 2
                st.rerun()

def show_medical_chat_history():
    """Show chat history with medical personas"""
    st.markdown("##### Medical Chat History")
    
    try:
        api_client = st.session_state.api_client
        
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            persona_filter = st.selectbox(
                "Filter by Healthcare Provider",
                options=["All", "doctor", "nurse", "therapist"],
                key="medical_chat_filter"
            )
        
        with col2:
            days_filter = st.selectbox(
                "Time Period",
                options=[7, 30, 90, 365],
                format_func=lambda x: f"Last {x} days",
                key="medical_days_filter"
            )
        
        # Get chat history
        persona = None if persona_filter == "All" else persona_filter
        chat_history = api_client.get_chat_history(
            persona=persona,
            days=days_filter,
            limit=50
        )
        
        # Filter to only medical personas
        medical_personas = ["doctor", "nurse", "therapist"]
        medical_chats = [chat for chat in chat_history if chat.get('persona') in medical_personas]
        
        if medical_chats:
            st.markdown(f"Found {len(medical_chats)} medical conversations")
            
            for i, chat in enumerate(medical_chats):
                show_medical_chat_card(chat, i)
        else:
            st.info("No medical chat history found. Start a conversation with a healthcare provider!")
            
    except Exception as e:
        st.error(f"Error loading medical chat history: {e}")

def show_medical_chat_card(chat, index):
    """Display a medical chat card"""
    persona = chat.get('persona', 'unknown')
    user_message = chat.get('user_message', '')
    ai_response = chat.get('ai_response', '')
    timestamp = chat.get('timestamp', 'Unknown time')
    
    # Format timestamp
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime("%B %d, %Y at %I:%M %p")
        else:
            formatted_time = str(timestamp)
    except:
        formatted_time = str(timestamp)
    
    persona_emoji = {"doctor": "🩺", "nurse": "👩‍⚕️", "therapist": "🧠"}.get(persona, "💬")
    
    with st.expander(f"{persona_emoji} {persona.title()} - {formatted_time}", expanded=False):
        st.markdown("**Your Question:**")
        st.markdown(f"> {user_message}")
        
        st.markdown(f"**{persona.title()}'s Response:**")
        st.info(ai_response)

def show_health_statistics():
    """Show health-related statistics"""
    st.markdown("##### Health Statistics")
    
    try:
        api_client = st.session_state.api_client
        
        # Get health stats
        health_stats = api_client.get_health_stats(days=30)
        
        if health_stats.get('total_entries', 0) > 0:
            # Display stats
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Health Entries", health_stats['total_entries'])
            
            with col2:
                st.metric("Tracked Metrics", len(health_stats.get('metrics', {})))
            
            # Show metrics breakdown
            if health_stats.get('metrics'):
                st.markdown("**Health Metrics Tracked:**")
                
                for metric, data in health_stats['metrics'].items():
                    with st.expander(f"{metric.replace('_', ' ').title()} ({data['count']} entries)"):
                        if data.get('values'):
                            st.line_chart(data['values'])
                        else:
                            st.info("No numeric data to chart")
        else:
            st.info("No health statistics available yet. Start tracking your health metrics!")
            
    except Exception as e:
        st.error(f"Error loading health statistics: {e}")

# Helper functions for styling
def get_file_type_emoji(file_type):
    """Get emoji for file type"""
    emoji_map = {
        "pdf": "📄",
        "image": "🖼️",
        "document": "📝",
        "unknown": "❓"
    }
    return emoji_map.get(file_type, "📄")