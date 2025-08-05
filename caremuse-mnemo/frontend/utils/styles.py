import streamlit as st

def apply_custom_styles():
    """Apply custom CSS styles to the Streamlit application"""
    
    st.markdown("""
    <style>
    /* Main application styles */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* Welcome card styles */
    .welcome-card {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
    }
    
    .welcome-card h3 {
        color: #495057;
        margin-bottom: 1rem;
    }
    
    .welcome-card ul {
        padding-left: 1.5rem;
    }
    
    .welcome-card li {
        margin: 0.5rem 0;
        color: #6c757d;
    }
    
    /* Dashboard cards */
    .dashboard-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .dashboard-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    .dashboard-card h4 {
        color: #495057;
        margin-bottom: 0.5rem;
    }
    
    .dashboard-card p {
        color: #6c757d;
        margin: 0;
        font-size: 0.9rem;
    }
    
    /* Activity items */
    .activity-item {
        display: flex;
        align-items: center;
        padding: 0.75rem;
        margin: 0.5rem 0;
        background: #f8f9fa;
        border-radius: 8px;
        border-left: 4px solid #007bff;
    }
    
    .activity-icon {
        font-size: 1.2rem;
        margin-right: 0.75rem;
        min-width: 30px;
    }
    
    .activity-content {
        flex: 1;
        color: #495057;
        font-size: 0.9rem;
    }
    
    .activity-type {
        font-size: 0.8rem;
        color: #6c757d;
        background: #e9ecef;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        margin-left: 0.5rem;
    }
    
    /* Chat message styles */
    .user-message {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #2196f3;
    }
    
    .ai-message {
        background: #f3e5f5;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #9c27b0;
    }
    
    .user-message strong,
    .ai-message strong {
        color: #333;
        display: block;
        margin-bottom: 0.5rem;
    }
    
    /* Memory card styles */
    .memory-card {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    .memory-card:hover {
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }
    
    .memory-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .memory-type {
        background: #007bff;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
    }
    
    .memory-timestamp {
        color: #6c757d;
        font-size: 0.8rem;
    }
    
    /* Medical document styles */
    .medical-document {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .medical-document-header {
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .medical-document-icon {
        font-size: 1.5rem;
        margin-right: 0.75rem;
        color: #856404;
    }
    
    .medical-document-title {
        flex: 1;
        font-weight: 600;
        color: #856404;
    }
    
    /* Game styles */
    .game-card {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .game-card h4 {
        margin-bottom: 0.5rem;
    }
    
    .game-score {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .game-grid {
        display: grid;
        gap: 0.5rem;
        margin: 1rem 0;
        justify-content: center;
    }
    
    .game-tile {
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: white;
        border: 2px solid #dee2e6;
        border-radius: 8px;
        font-size: 1.2rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .game-tile:hover {
        background: #f8f9fa;
        transform: scale(1.05);
    }
    
    .game-tile.matched {
        background: #28a745;
        color: white;
        border-color: #28a745;
    }
    
    .game-tile.flipped {
        background: #007bff;
        color: white;
        border-color: #007bff;
    }
    
    /* Health metric styles */
    .health-metric {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .health-metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #28a745;
        margin: 0.5rem 0;
    }
    
    .health-metric-label {
        color: #6c757d;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Reminder styles */
    .reminder-item {
        display: flex;
        align-items: center;
        padding: 1rem;
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .reminder-item.completed {
        background: #f8f9fa;
        opacity: 0.7;
    }
    
    .reminder-icon {
        font-size: 1.5rem;
        margin-right: 1rem;
        color: #ffc107;
    }
    
    .reminder-content {
        flex: 1;
    }
    
    .reminder-text {
        font-weight: 500;
        color: #495057;
        margin-bottom: 0.25rem;
    }
    
    .reminder-time {
        font-size: 0.8rem;
        color: #6c757d;
    }
    
    .reminder-actions {
        display: flex;
        gap: 0.5rem;
    }
    
    /* Statistics styles */
    .stat-card {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #007bff;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        color: #6c757d;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Progress bar styles */
    .progress-container {
        background: #e9ecef;
        border-radius: 10px;
        height: 20px;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #28a745, #20c997);
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    /* Notification styles */
    .notification {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
    }
    
    .notification.success {
        background: #d4edda;
        border-color: #c3e6cb;
    }
    
    .notification.error {
        background: #f8d7da;
        border-color: #f5c6cb;
    }
    
    .notification-icon {
        font-size: 1.2rem;
        margin-right: 0.75rem;
    }
    
    .notification-content {
        flex: 1;
    }
    
    /* Button styles */
    .btn-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        color: white;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .btn-primary:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    .btn-secondary {
        background: #6c757d;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        color: white;
        font-weight: 500;
    }
    
    .btn-success {
        background: #28a745;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        color: white;
        font-weight: 500;
    }
    
    .btn-warning {
        background: #ffc107;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        color: #212529;
        font-weight: 500;
    }
    
    /* Form styles */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #ced4da;
        padding: 0.75rem;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 1px solid #ced4da;
        padding: 0.75rem;
    }
    
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 1px solid #ced4da;
        padding: 0.75rem;
    }
    
    /* Sidebar styles */
    .css-1d391kg {
        background: #f8f9fa;
    }
    
    .css-1d391kg .css-1v0mbdj {
        border-radius: 10px;
        margin: 0.25rem 0;
    }
    
    /* Tab styles */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 8px;
        padding: 0 20px;
        background: #f8f9fa;
        border: 1px solid #dee2e6;
    }
    
    .stTabs [aria-selected="true"] {
        background: #007bff;
        color: white;
        border-color: #007bff;
    }
    
    /* Metric styles */
    .metric-container {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    /* Expander styles */
    .streamlit-expanderHeader {
        background: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
    
    /* File uploader styles */
    .stFileUploader > div {
        border: 2px dashed #007bff;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9fa;
    }
    
    /* Success/Error message styles */
    .stSuccess {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stError {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stWarning {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stInfo {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header p {
            font-size: 1rem;
        }
        
        .dashboard-card {
            padding: 1rem;
        }
        
        .game-tile {
            width: 50px;
            height: 50px;
            font-size: 1rem;
        }
        
        .stat-value {
            font-size: 2rem;
        }
    }
    
    /* Animation classes */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); }
        to { transform: translateX(0); }
    }
    
    .slide-in {
        animation: slideIn 0.3s ease-out;
    }
    
    /* Loading spinner */
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #007bff;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Accessibility improvements */
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }
    
    /* Focus styles for better accessibility */
    button:focus,
    input:focus,
    select:focus,
    textarea:focus {
        outline: 2px solid #007bff;
        outline-offset: 2px;
    }
    
    /* High contrast mode support */
    @media (prefers-contrast: high) {
        .dashboard-card,
        .memory-card,
        .health-metric,
        .reminder-item,
        .stat-card {
            border-width: 2px;
        }
    }
    
    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {
        *,
        *::before,
        *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def get_persona_color(persona: str) -> str:
    """Get color scheme for different personas"""
    colors = {
        "companion": "#667eea",
        "son": "#4facfe",
        "daughter": "#f093fb",
        "doctor": "#43e97b",
        "nurse": "#38f9d7",
        "therapist": "#4facfe"
    }
    return colors.get(persona, "#667eea")

def get_memory_type_color(memory_type: str) -> str:
    """Get color scheme for different memory types"""
    colors = {
        "diary": "#667eea",
        "experience": "#4facfe",
        "thought": "#43e97b",
        "gratitude": "#f093fb",
        "achievement": "#ffeaa7",
        "social": "#fd79a8",
        "learning": "#00b894",
        "reflection": "#6c5ce7"
    }
    return colors.get(memory_type, "#667eea")

def apply_dark_theme():
    """Apply dark theme styles"""
    st.markdown("""
    <style>
    /* Dark theme overrides */
    .main-header {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
    }
    
    .welcome-card,
    .dashboard-card,
    .memory-card,
    .health-metric,
    .reminder-item,
    .stat-card {
        background: #2d3748;
        border-color: #4a5568;
        color: #e2e8f0;
    }
    
    .activity-item {
        background: #2d3748;
        color: #e2e8f0;
    }
    
    .user-message {
        background: #2a4365;
        border-left-color: #3182ce;
    }
    
    .ai-message {
        background: #553c9a;
        border-left-color: #805ad5;
    }
    
    body {
        background-color: #1a202c;
        color: #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)