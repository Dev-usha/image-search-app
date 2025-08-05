import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class ChatLogger:
    def __init__(self, db_path="db.sqlite"):
        """
        Initialize chat logger
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._init_chat_tables()
        
    def _init_chat_tables(self):
        """Initialize chat logging tables in SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Chat conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_conversations (
                id TEXT PRIMARY KEY,
                persona TEXT NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                scope TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                user_name TEXT,
                metadata TEXT
            )
        ''')
        
        # Chat sessions table for grouping conversations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id TEXT PRIMARY KEY,
                persona TEXT NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                message_count INTEGER DEFAULT 0,
                user_name TEXT
            )
        ''')
        
        # Indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_persona ON chat_conversations(persona)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_timestamp ON chat_conversations(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_scope ON chat_conversations(scope)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_persona ON chat_sessions(persona)')
        
        conn.commit()
        conn.close()
        
    def log_conversation(self, persona: str, user_message: str, ai_response: str, 
                        scope: str, user_name: str = "User", metadata: Dict[str, Any] = None) -> str:
        """
        Log a conversation exchange
        
        Args:
            persona: Persona that responded
            user_message: User's message
            ai_response: AI's response
            scope: Conversation scope (personal/medical)
            user_name: Name of the user
            metadata: Additional metadata
            
        Returns:
            Conversation ID
        """
        try:
            conversation_id = str(uuid.uuid4())
            timestamp = datetime.now()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert conversation
            cursor.execute('''
                INSERT INTO chat_conversations 
                (id, persona, user_message, ai_response, scope, timestamp, user_name, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                conversation_id,
                persona,
                user_message,
                ai_response,
                scope,
                timestamp,
                user_name,
                json.dumps(metadata) if metadata else None
            ))
            
            conn.commit()
            conn.close()
            
            return conversation_id
            
        except Exception as e:
            print(f"Error logging conversation: {e}")
            return ""
            
    def get_chat_history(self, persona: str = None, days: int = 7, 
                        limit: int = 50, user_name: str = None) -> List[Dict[str, Any]]:
        """
        Get chat history with filtering options
        
        Args:
            persona: Filter by persona (optional)
            days: Number of days to look back
            limit: Maximum number of conversations to return
            user_name: Filter by user name (optional)
            
        Returns:
            List of conversation dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build query
            query = '''
                SELECT id, persona, user_message, ai_response, scope, timestamp, user_name, metadata
                FROM chat_conversations
                WHERE timestamp >= ?
            '''
            params = [datetime.now() - timedelta(days=days)]
            
            if persona:
                query += ' AND persona = ?'
                params.append(persona)
                
            if user_name:
                query += ' AND user_name = ?'
                params.append(user_name)
                
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            
            conversations = []
            for row in cursor.fetchall():
                conversation = {
                    'id': row[0],
                    'persona': row[1],
                    'user_message': row[2],
                    'ai_response': row[3],
                    'scope': row[4],
                    'timestamp': row[5],
                    'user_name': row[6],
                    'metadata': json.loads(row[7]) if row[7] else {}
                }
                conversations.append(conversation)
                
            conn.close()
            return conversations
            
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []
            
    def search_conversations(self, query: str, persona: str = None, 
                           days: int = 30, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search conversations by text content
        
        Args:
            query: Search query
            persona: Filter by persona (optional)
            days: Number of days to search back
            limit: Maximum results
            
        Returns:
            List of matching conversations
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build search query
            search_query = '''
                SELECT id, persona, user_message, ai_response, scope, timestamp, user_name, metadata
                FROM chat_conversations
                WHERE timestamp >= ?
                AND (user_message LIKE ? OR ai_response LIKE ?)
            '''
            params = [
                datetime.now() - timedelta(days=days),
                f'%{query}%',
                f'%{query}%'
            ]
            
            if persona:
                search_query += ' AND persona = ?'
                params.append(persona)
                
            search_query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(search_query, params)
            
            conversations = []
            for row in cursor.fetchall():
                conversation = {
                    'id': row[0],
                    'persona': row[1],
                    'user_message': row[2],
                    'ai_response': row[3],
                    'scope': row[4],
                    'timestamp': row[5],
                    'user_name': row[6],
                    'metadata': json.loads(row[7]) if row[7] else {},
                    'relevance_score': self._calculate_relevance(query, row[2], row[3])
                }
                conversations.append(conversation)
                
            # Sort by relevance score
            conversations.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            conn.close()
            return conversations
            
        except Exception as e:
            print(f"Error searching conversations: {e}")
            return []
            
    def get_conversation_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Get conversation statistics
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Statistics dictionary
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since_date = datetime.now() - timedelta(days=days)
            
            # Total conversations
            cursor.execute(
                'SELECT COUNT(*) FROM chat_conversations WHERE timestamp >= ?',
                (since_date,)
            )
            total_conversations = cursor.fetchone()[0]
            
            # Conversations by persona
            cursor.execute('''
                SELECT persona, COUNT(*) 
                FROM chat_conversations 
                WHERE timestamp >= ? 
                GROUP BY persona
            ''', (since_date,))
            
            persona_stats = dict(cursor.fetchall())
            
            # Conversations by day
            cursor.execute('''
                SELECT DATE(timestamp) as date, COUNT(*) 
                FROM chat_conversations 
                WHERE timestamp >= ? 
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            ''', (since_date,))
            
            daily_stats = dict(cursor.fetchall())
            
            # Average response length
            cursor.execute('''
                SELECT AVG(LENGTH(ai_response)) 
                FROM chat_conversations 
                WHERE timestamp >= ?
            ''', (since_date,))
            
            avg_response_length = cursor.fetchone()[0] or 0
            
            # Most active hours
            cursor.execute('''
                SELECT strftime('%H', timestamp) as hour, COUNT(*) 
                FROM chat_conversations 
                WHERE timestamp >= ? 
                GROUP BY strftime('%H', timestamp)
                ORDER BY COUNT(*) DESC
            ''', (since_date,))
            
            hourly_stats = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_conversations': total_conversations,
                'persona_breakdown': persona_stats,
                'daily_activity': daily_stats,
                'average_response_length': round(avg_response_length, 2),
                'most_active_hours': hourly_stats,
                'analysis_period_days': days
            }
            
        except Exception as e:
            print(f"Error getting conversation stats: {e}")
            return {}
            
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a specific conversation
        
        Args:
            conversation_id: ID of conversation to delete
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM chat_conversations WHERE id = ?', (conversation_id,))
            
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            return success
            
        except Exception as e:
            print(f"Error deleting conversation: {e}")
            return False
            
    def clear_old_conversations(self, days_to_keep: int = 90) -> int:
        """
        Clear conversations older than specified days
        
        Args:
            days_to_keep: Number of days of conversations to keep
            
        Returns:
            Number of conversations deleted
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            cursor.execute('DELETE FROM chat_conversations WHERE timestamp < ?', (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            return deleted_count
            
        except Exception as e:
            print(f"Error clearing old conversations: {e}")
            return 0
            
    def export_conversations(self, persona: str = None, days: int = 30) -> List[Dict[str, Any]]:
        """
        Export conversations for backup or analysis
        
        Args:
            persona: Filter by persona (optional)
            days: Number of days to export
            
        Returns:
            List of conversation data
        """
        return self.get_chat_history(persona=persona, days=days, limit=10000)
        
    def _calculate_relevance(self, query: str, user_message: str, ai_response: str) -> float:
        """Calculate relevance score for search results"""
        query_lower = query.lower()
        user_lower = user_message.lower()
        ai_lower = ai_response.lower()
        
        score = 0.0
        
        # Exact matches get higher scores
        if query_lower in user_lower:
            score += 2.0
        if query_lower in ai_lower:
            score += 1.5
            
        # Word matches
        query_words = query_lower.split()
        user_words = user_lower.split()
        ai_words = ai_lower.split()
        
        for word in query_words:
            if word in user_words:
                score += 1.0
            if word in ai_words:
                score += 0.5
                
        return score
        
    def get_recent_context(self, persona: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get recent conversation context for a persona
        
        Args:
            persona: Persona to get context for
            limit: Number of recent conversations
            
        Returns:
            List of recent conversations
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_message, ai_response, timestamp
                FROM chat_conversations
                WHERE persona = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (persona, limit))
            
            context = []
            for row in cursor.fetchall():
                context.append({
                    'user_message': row[0],
                    'ai_response': row[1],
                    'timestamp': row[2]
                })
                
            conn.close()
            return context
            
        except Exception as e:
            print(f"Error getting recent context: {e}")
            return []