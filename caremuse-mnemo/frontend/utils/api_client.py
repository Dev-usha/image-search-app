import requests
import json
from typing import Dict, List, Any, Optional
import streamlit as st

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize API client for CareMuse + Mnemo backend
        
        Args:
            base_url: Base URL of the backend API
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to the API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            Response JSON as dictionary
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            # Handle empty responses
            if response.status_code == 204 or not response.content:
                return {"status": "success"}
            
            return response.json()
            
        except requests.exceptions.ConnectionError:
            st.error("🔌 Cannot connect to the backend server. Please make sure it's running.")
            return {"status": "error", "message": "Connection failed"}
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            st.error(f"❌ API Error: {error_msg}")
            return {"status": "error", "message": error_msg}
            
        except requests.exceptions.RequestException as e:
            st.error(f"🚫 Request failed: {str(e)}")
            return {"status": "error", "message": str(e)}
            
        except json.JSONDecodeError:
            st.error("📄 Invalid response format from server")
            return {"status": "error", "message": "Invalid JSON response"}
    
    def health_check(self) -> bool:
        """
        Check if the backend API is healthy
        
        Returns:
            True if API is responding, False otherwise
        """
        try:
            response = self._make_request("GET", "/")
            return response.get("status") != "error"
        except:
            return False
    
    def store_memory(self, text: str, memory_type: str = "diary", 
                    scope: str = "personal", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Store a new memory entry
        
        Args:
            text: Memory content
            memory_type: Type of memory
            scope: Memory scope (personal/medical)
            metadata: Additional metadata
            
        Returns:
            API response
        """
        data = {
            "text": text,
            "memory_type": memory_type,
            "scope": scope,
            "metadata": metadata or {}
        }
        
        return self._make_request("POST", "/store_memory", json=data)
    
    def get_memories(self, scope: str = "personal", memory_type: str = None,
                    limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get memories with filtering
        
        Args:
            scope: Memory scope
            memory_type: Filter by memory type
            limit: Maximum number of memories
            offset: Pagination offset
            
        Returns:
            List of memories
        """
        params = {
            "scope": scope,
            "limit": limit,
            "offset": offset
        }
        
        if memory_type:
            params["memory_type"] = memory_type
        
        response = self._make_request("GET", "/get_memories", params=params)
        return response.get("memories", []) if response.get("status") != "error" else []
    
    def search_memories(self, query: str, scope: str = "personal", 
                       limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search memories using vector similarity
        
        Args:
            query: Search query
            scope: Memory scope
            limit: Maximum results
            
        Returns:
            List of matching memories
        """
        params = {
            "query": query,
            "scope": scope,
            "limit": limit
        }
        
        response = self._make_request("GET", "/search_memories", params=params)
        return response.get("memories", []) if response.get("status") != "error" else []
    
    def chat_with_persona(self, message: str, persona: str, 
                         user_name: str = "User") -> Dict[str, Any]:
        """
        Chat with a specific persona
        
        Args:
            message: User's message
            persona: Persona to chat with
            user_name: User's name
            
        Returns:
            Persona's response
        """
        data = {
            "message": message,
            "persona": persona,
            "user_name": user_name
        }
        
        return self._make_request("POST", "/chat", json=data)
    
    def upload_medical_document(self, file) -> Dict[str, Any]:
        """
        Upload and process medical document
        
        Args:
            file: File object to upload
            
        Returns:
            Processing results
        """
        # For file uploads, we need to use a different approach
        url = f"{self.base_url}/upload_medical"
        
        try:
            # Reset file pointer
            file.seek(0)
            
            files = {"file": (file.name, file, file.type)}
            
            # Use requests directly for file upload (not session to avoid JSON headers)
            response = requests.post(url, files=files)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.ConnectionError:
            st.error("🔌 Cannot connect to the backend server for file upload.")
            return {"status": "error", "message": "Connection failed"}
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            st.error(f"❌ Upload Error: {error_msg}")
            return {"status": "error", "message": error_msg}
            
        except Exception as e:
            st.error(f"🚫 Upload failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def add_reminder(self, text: str, reminder_time: str, 
                    reminder_type: str = "general", is_completed: bool = False) -> Dict[str, Any]:
        """
        Add a new reminder
        
        Args:
            text: Reminder text
            reminder_time: When to remind
            reminder_type: Type of reminder
            is_completed: Whether completed
            
        Returns:
            API response
        """
        data = {
            "text": text,
            "reminder_time": reminder_time,
            "reminder_type": reminder_type,
            "is_completed": is_completed
        }
        
        return self._make_request("POST", "/add_reminder", json=data)
    
    def get_reminders(self, completed: bool = None) -> List[Dict[str, Any]]:
        """
        Get reminders
        
        Args:
            completed: Filter by completion status
            
        Returns:
            List of reminders
        """
        params = {}
        if completed is not None:
            params["completed"] = completed
        
        response = self._make_request("GET", "/get_reminders", params=params)
        return response.get("reminders", []) if response.get("status") != "error" else []
    
    def update_reminder(self, reminder_id: str, is_completed: bool) -> Dict[str, Any]:
        """
        Update reminder completion status
        
        Args:
            reminder_id: ID of reminder to update
            is_completed: New completion status
            
        Returns:
            API response
        """
        params = {"is_completed": is_completed}
        return self._make_request("PUT", f"/update_reminder/{reminder_id}", params=params)
    
    def log_health_metric(self, metric_type: str, value: str, unit: str = "", 
                         notes: str = "") -> Dict[str, Any]:
        """
        Log a health metric
        
        Args:
            metric_type: Type of health metric
            value: Metric value
            unit: Unit of measurement
            notes: Additional notes
            
        Returns:
            API response
        """
        data = {
            "metric_type": metric_type,
            "value": value,
            "unit": unit,
            "notes": notes
        }
        
        return self._make_request("POST", "/log_health", json=data)
    
    def get_health_stats(self, metric_type: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Get health statistics
        
        Args:
            metric_type: Filter by metric type
            days: Number of days to analyze
            
        Returns:
            Health statistics
        """
        params = {"days": days}
        if metric_type:
            params["metric_type"] = metric_type
        
        response = self._make_request("GET", "/get_health_stats", params=params)
        return response.get("health_stats", {}) if response.get("status") != "error" else {}
    
    def log_game_result(self, game_type: str, score: int, time_taken: int, 
                       difficulty: str = "normal") -> Dict[str, Any]:
        """
        Log brain game result
        
        Args:
            game_type: Type of game
            score: Game score
            time_taken: Time taken in seconds
            difficulty: Game difficulty
            
        Returns:
            API response
        """
        data = {
            "game_type": game_type,
            "score": score,
            "time_taken": time_taken,
            "difficulty": difficulty
        }
        
        return self._make_request("POST", "/log_game_result", json=data)
    
    def get_game_stats(self, game_type: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Get game performance statistics
        
        Args:
            game_type: Filter by game type
            days: Number of days to analyze
            
        Returns:
            Game statistics
        """
        params = {"days": days}
        if game_type:
            params["game_type"] = game_type
        
        response = self._make_request("GET", "/get_game_stats", params=params)
        return response.get("game_stats", {}) if response.get("status") != "error" else {}
    
    def get_chat_history(self, persona: str = None, days: int = 7, 
                        limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get chat history
        
        Args:
            persona: Filter by persona
            days: Number of days to look back
            limit: Maximum conversations to return
            
        Returns:
            List of conversations
        """
        params = {
            "days": days,
            "limit": limit
        }
        
        if persona:
            params["persona"] = persona
        
        response = self._make_request("GET", "/get_chat_history", params=params)
        return response.get("chat_history", []) if response.get("status") != "error" else []
    
    def search_conversations(self, query: str, persona: str = None, 
                           days: int = 30, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search conversations (if backend supports it)
        
        Args:
            query: Search query
            persona: Filter by persona
            days: Days to search back
            limit: Maximum results
            
        Returns:
            List of matching conversations
        """
        # This might not be implemented in the backend yet
        # For now, we'll use get_chat_history and filter client-side
        conversations = self.get_chat_history(persona=persona, days=days, limit=limit * 2)
        
        # Simple client-side search
        query_lower = query.lower()
        results = []
        
        for conv in conversations:
            user_msg = conv.get('user_message', '').lower()
            ai_msg = conv.get('ai_response', '').lower()
            
            if query_lower in user_msg or query_lower in ai_msg:
                results.append(conv)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def get_conversation_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Get conversation statistics (if backend supports it)
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Conversation statistics
        """
        # This might not be implemented in the backend yet
        # We'll try the endpoint, and if it fails, return empty dict
        try:
            params = {"days": days}
            response = self._make_request("GET", "/get_conversation_stats", params=params)
            return response.get("stats", {}) if response.get("status") != "error" else {}
        except:
            return {}
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to the backend
        
        Returns:
            Connection test results
        """
        try:
            response = self._make_request("GET", "/")
            
            if response.get("status") != "error":
                return {
                    "status": "connected",
                    "message": "Backend is running and accessible",
                    "backend_message": response.get("message", "")
                }
            else:
                return {
                    "status": "error",
                    "message": "Backend returned an error",
                    "error": response.get("message", "")
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": "Cannot connect to backend",
                "error": str(e)
            }
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        Get API information and available endpoints
        
        Returns:
            API information
        """
        return {
            "base_url": self.base_url,
            "available_endpoints": [
                "/",
                "/store_memory",
                "/get_memories",
                "/search_memories", 
                "/chat",
                "/upload_medical",
                "/add_reminder",
                "/get_reminders",
                "/update_reminder/{id}",
                "/log_health",
                "/get_health_stats",
                "/log_game_result",
                "/get_game_stats",
                "/get_chat_history"
            ],
            "connection_status": "connected" if self.health_check() else "disconnected"
        }