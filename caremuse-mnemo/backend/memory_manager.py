import sqlite3
import faiss
import numpy as np
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from embeddings import EmbeddingGenerator

class MemoryManager:
    def __init__(self, db_path="db.sqlite"):
        self.db_path = db_path
        self.embedding_generator = EmbeddingGenerator()
        
        # Initialize databases
        self._init_database()
        self._init_faiss_indices()
        
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main memories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                scope TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                metadata TEXT,
                faiss_id INTEGER
            )
        ''')
        
        # Index for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scope ON memories(scope)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON memories(memory_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)')
        
        conn.commit()
        conn.close()
        
    def _init_faiss_indices(self):
        """Initialize FAISS indices for vector search"""
        self.embedding_dim = 384  # sentence-transformers/all-MiniLM-L6-v2 dimension
        
        # Try to load existing indices
        try:
            self.personal_index = faiss.read_index("faiss_personal.index")
            self.medical_index = faiss.read_index("faiss_medical.index")
        except:
            # Create new indices if they don't exist
            self.personal_index = faiss.IndexFlatIP(self.embedding_dim)
            self.medical_index = faiss.IndexFlatIP(self.embedding_dim)
            
        # Keep track of FAISS ID to memory ID mapping
        self._load_faiss_mappings()
        
    def _load_faiss_mappings(self):
        """Load FAISS ID to memory ID mappings"""
        self.personal_id_map = {}
        self.medical_id_map = {}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, faiss_id, scope FROM memories WHERE faiss_id IS NOT NULL')
        for memory_id, faiss_id, scope in cursor.fetchall():
            if scope == "personal":
                self.personal_id_map[faiss_id] = memory_id
            else:
                self.medical_id_map[faiss_id] = memory_id
                
        conn.close()
        
    def store_memory(self, text: str, memory_type: str, scope: str, metadata: Dict[str, Any] = None) -> str:
        """Store a new memory entry"""
        memory_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # Generate embedding
        embedding = self.embedding_generator.generate_embedding(text)
        
        # Choose appropriate FAISS index
        if scope == "personal":
            faiss_index = self.personal_index
            id_map = self.personal_id_map
        else:
            faiss_index = self.medical_index
            id_map = self.medical_id_map
            
        # Add to FAISS index
        faiss_id = faiss_index.ntotal
        faiss_index.add(np.array([embedding], dtype=np.float32))
        id_map[faiss_id] = memory_id
        
        # Store in SQLite
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO memories (id, text, memory_type, scope, timestamp, metadata, faiss_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            memory_id,
            text,
            memory_type,
            scope,
            timestamp,
            json.dumps(metadata) if metadata else None,
            faiss_id
        ))
        
        conn.commit()
        conn.close()
        
        # Save FAISS indices
        self._save_faiss_indices()
        
        return memory_id
        
    def search_memories(self, query: str, scope: str = "personal", limit: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant memories using vector similarity"""
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        # Choose appropriate index and mapping
        if scope == "personal":
            faiss_index = self.personal_index
            id_map = self.personal_id_map
        else:
            faiss_index = self.medical_index
            id_map = self.medical_id_map
            
        if faiss_index.ntotal == 0:
            return []
            
        # Search FAISS index
        k = min(limit, faiss_index.ntotal)
        scores, indices = faiss_index.search(np.array([query_embedding], dtype=np.float32), k)
        
        # Get memory details from SQLite
        memory_ids = [id_map[idx] for idx in indices[0] if idx in id_map]
        
        if not memory_ids:
            return []
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        placeholders = ','.join(['?' for _ in memory_ids])
        cursor.execute(f'''
            SELECT id, text, memory_type, scope, timestamp, metadata
            FROM memories
            WHERE id IN ({placeholders})
            ORDER BY timestamp DESC
        ''', memory_ids)
        
        memories = []
        for row in cursor.fetchall():
            memory = {
                'id': row[0],
                'text': row[1],
                'memory_type': row[2],
                'scope': row[3],
                'timestamp': row[4],
                'metadata': json.loads(row[5]) if row[5] else {}
            }
            memories.append(memory)
            
        conn.close()
        return memories
        
    def get_memories(self, scope: str = "personal", memory_type: str = None, 
                    limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get memories with filtering options"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT id, text, memory_type, scope, timestamp, metadata FROM memories WHERE scope = ?'
        params = [scope]
        
        if memory_type:
            query += ' AND memory_type = ?'
            params.append(memory_type)
            
        query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        
        memories = []
        for row in cursor.fetchall():
            memory = {
                'id': row[0],
                'text': row[1],
                'memory_type': row[2],
                'scope': row[3],
                'timestamp': row[4],
                'metadata': json.loads(row[5]) if row[5] else {}
            }
            memories.append(memory)
            
        conn.close()
        return memories
        
    def update_reminder_status(self, reminder_id: str, is_completed: bool) -> bool:
        """Update reminder completion status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current metadata
        cursor.execute('SELECT metadata FROM memories WHERE id = ?', (reminder_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False
            
        metadata = json.loads(result[0]) if result[0] else {}
        metadata['is_completed'] = is_completed
        
        # Update metadata
        cursor.execute('UPDATE memories SET metadata = ? WHERE id = ?', 
                      (json.dumps(metadata), reminder_id))
        
        conn.commit()
        conn.close()
        return True
        
    def get_health_stats(self, metric_type: str = None, days: int = 30) -> Dict[str, Any]:
        """Get health statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = datetime.now() - timedelta(days=days)
        
        query = '''
            SELECT metadata FROM memories 
            WHERE memory_type = 'health_log' 
            AND scope = 'medical' 
            AND timestamp >= ?
        '''
        params = [since_date]
        
        if metric_type:
            query += ' AND json_extract(metadata, "$.metric_type") = ?'
            params.append(metric_type)
            
        cursor.execute(query, params)
        
        stats = {
            'total_entries': 0,
            'metrics': {},
            'recent_entries': []
        }
        
        for row in cursor.fetchall():
            metadata = json.loads(row[0]) if row[0] else {}
            stats['total_entries'] += 1
            
            metric = metadata.get('metric_type', 'unknown')
            if metric not in stats['metrics']:
                stats['metrics'][metric] = {'count': 0, 'values': []}
                
            stats['metrics'][metric]['count'] += 1
            if 'value' in metadata:
                try:
                    value = float(metadata['value'])
                    stats['metrics'][metric]['values'].append(value)
                except:
                    pass
                    
        conn.close()
        return stats
        
    def get_game_stats(self, game_type: str = None, days: int = 30) -> Dict[str, Any]:
        """Get game performance statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = datetime.now() - timedelta(days=days)
        
        query = '''
            SELECT metadata FROM memories 
            WHERE memory_type = 'game_result' 
            AND scope = 'personal' 
            AND timestamp >= ?
        '''
        params = [since_date]
        
        if game_type:
            query += ' AND json_extract(metadata, "$.game_type") = ?'
            params.append(game_type)
            
        cursor.execute(query, params)
        
        stats = {
            'total_games': 0,
            'games': {},
            'best_scores': {}
        }
        
        for row in cursor.fetchall():
            metadata = json.loads(row[0]) if row[0] else {}
            stats['total_games'] += 1
            
            game = metadata.get('game_type', 'unknown')
            score = metadata.get('score', 0)
            time_taken = metadata.get('time_taken', 0)
            
            if game not in stats['games']:
                stats['games'][game] = {
                    'count': 0,
                    'total_score': 0,
                    'total_time': 0,
                    'best_score': 0,
                    'best_time': float('inf')
                }
                
            game_stats = stats['games'][game]
            game_stats['count'] += 1
            game_stats['total_score'] += score
            game_stats['total_time'] += time_taken
            game_stats['best_score'] = max(game_stats['best_score'], score)
            game_stats['best_time'] = min(game_stats['best_time'], time_taken)
            
        # Calculate averages
        for game in stats['games']:
            game_stats = stats['games'][game]
            if game_stats['count'] > 0:
                game_stats['avg_score'] = game_stats['total_score'] / game_stats['count']
                game_stats['avg_time'] = game_stats['total_time'] / game_stats['count']
                
        conn.close()
        return stats
        
    def _save_faiss_indices(self):
        """Save FAISS indices to disk"""
        faiss.write_index(self.personal_index, "faiss_personal.index")
        faiss.write_index(self.medical_index, "faiss_medical.index")
        
    def __del__(self):
        """Save indices when object is destroyed"""
        try:
            self._save_faiss_indices()
        except:
            pass