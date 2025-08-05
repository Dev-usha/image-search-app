import requests
import json
import yaml
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

class LLMInterface:
    def __init__(self, ollama_url="http://localhost:11434", default_model="mistral"):
        """
        Initialize LLM interface for Ollama
        
        Args:
            ollama_url: URL of the Ollama API server
            default_model: Default model to use for generation
        """
        self.ollama_url = ollama_url
        self.default_model = default_model
        self.personas = {}
        self._load_personas()
        
    def _load_personas(self):
        """Load persona configurations from YAML files"""
        personas_dir = "personas"
        if not os.path.exists(personas_dir):
            print(f"Personas directory not found: {personas_dir}")
            return
            
        for filename in os.listdir(personas_dir):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                persona_name = filename.split('.')[0]
                try:
                    with open(os.path.join(personas_dir, filename), 'r') as f:
                        persona_config = yaml.safe_load(f)
                        self.personas[persona_name] = persona_config
                        print(f"Loaded persona: {persona_name}")
                except Exception as e:
                    print(f"Error loading persona {filename}: {e}")
                    
    def generate_response(self, message: str, persona: str, memories: List[Dict[str, Any]], 
                         user_name: str = "User") -> str:
        """
        Generate a response using the specified persona and memory context
        
        Args:
            message: User's message
            persona: Persona to use for response
            memories: Relevant memories for context
            user_name: Name of the user
            
        Returns:
            Generated response text
        """
        try:
            # Get persona configuration
            persona_config = self.personas.get(persona, self._get_default_persona())
            
            # Build the prompt
            prompt = self._build_prompt(message, persona_config, memories, user_name)
            
            # Generate response using Ollama
            response = self._call_ollama(prompt, persona_config.get('model', self.default_model))
            
            return response
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return self._get_fallback_response(persona, message)
            
    def _build_prompt(self, message: str, persona_config: Dict[str, Any], 
                     memories: List[Dict[str, Any]], user_name: str) -> str:
        """Build the complete prompt for the LLM"""
        
        # Start with system prompt
        system_prompt = persona_config.get('system_prompt', '')
        
        # Add persona identity
        identity = persona_config.get('identity', {})
        name = identity.get('name', 'AI Assistant')
        role = identity.get('role', 'helpful companion')
        personality = identity.get('personality', 'friendly and supportive')
        
        # Build memory context
        memory_context = self._build_memory_context(memories)
        
        # Build conversation rules
        rules = persona_config.get('conversation_rules', [])
        rules_text = '\n'.join([f"- {rule}" for rule in rules])
        
        # Current time context
        current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
        
        # Combine everything into the prompt
        prompt = f"""System: {system_prompt}

You are {name}, a {role}. Your personality is {personality}.

Current time: {current_time}
User's name: {user_name}

Conversation Rules:
{rules_text}

Relevant memories about {user_name}:
{memory_context}

{user_name}: {message}

{name}: """

        return prompt
        
    def _build_memory_context(self, memories: List[Dict[str, Any]]) -> str:
        """Build memory context string from relevant memories"""
        if not memories:
            return "No relevant memories found."
            
        memory_lines = []
        for memory in memories[:5]:  # Limit to top 5 memories
            timestamp = memory.get('timestamp', 'Unknown time')
            text = memory.get('text', '')
            memory_type = memory.get('memory_type', 'general')
            
            # Format timestamp
            try:
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%B %d at %I:%M %p")
                else:
                    formatted_time = str(timestamp)
            except:
                formatted_time = str(timestamp)
                
            memory_lines.append(f"- {formatted_time} ({memory_type}): {text}")
            
        return '\n'.join(memory_lines)
        
    def _call_ollama(self, prompt: str, model: str) -> str:
        """Make API call to Ollama"""
        try:
            url = f"{self.ollama_url}/api/generate"
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 500
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '').strip()
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling Ollama API: {e}")
            raise e
        except Exception as e:
            print(f"Unexpected error in Ollama call: {e}")
            raise e
            
    def _get_default_persona(self) -> Dict[str, Any]:
        """Get default persona configuration"""
        return {
            'system_prompt': 'You are a helpful and caring AI companion.',
            'identity': {
                'name': 'AI Companion',
                'role': 'digital companion',
                'personality': 'warm, empathetic, and supportive'
            },
            'conversation_rules': [
                'Be warm and empathetic in your responses',
                'Reference the user\'s memories when relevant',
                'Keep responses concise but meaningful',
                'Show genuine care and interest'
            ],
            'model': self.default_model
        }
        
    def _get_fallback_response(self, persona: str, message: str) -> str:
        """Generate fallback response when LLM is unavailable"""
        fallback_responses = {
            'companion': "I'm here for you. Could you tell me more about what's on your mind?",
            'son': "Hi there! I'm glad you reached out. How are you feeling today?",
            'daughter': "Hello! It's so good to hear from you. What would you like to talk about?",
            'doctor': "I understand you have a health concern. While I can't replace professional medical advice, I'm here to help you understand your health information.",
            'nurse': "I'm here to help with your health questions. What can I assist you with today?",
            'therapist': "Thank you for sharing with me. Your feelings and experiences are important. How can I support you today?"
        }
        
        return fallback_responses.get(persona, "I'm here to help. Could you please repeat your question?")
        
    def test_connection(self) -> bool:
        """Test connection to Ollama server"""
        try:
            url = f"{self.ollama_url}/api/tags"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return True
        except:
            return False
            
    def list_available_models(self) -> List[str]:
        """List available models in Ollama"""
        try:
            url = f"{self.ollama_url}/api/tags"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            return models
            
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
            
    def pull_model(self, model_name: str) -> bool:
        """Pull a model to Ollama if not available"""
        try:
            url = f"{self.ollama_url}/api/pull"
            payload = {"name": model_name}
            
            response = requests.post(url, json=payload, timeout=300)  # 5 minute timeout
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            print(f"Error pulling model {model_name}: {e}")
            return False
            
    def get_persona_info(self, persona: str) -> Dict[str, Any]:
        """Get information about a specific persona"""
        return self.personas.get(persona, {})
        
    def list_personas(self) -> List[str]:
        """List all available personas"""
        return list(self.personas.keys())
        
    def reload_personas(self):
        """Reload persona configurations"""
        self.personas.clear()
        self._load_personas()