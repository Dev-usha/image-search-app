from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import torch

class EmbeddingGenerator:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the embedding generator with a sentence transformer model
        
        Args:
            model_name: HuggingFace model name for sentence embeddings
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
        
    def _load_model(self):
        """Load the sentence transformer model"""
        try:
            self.model = SentenceTransformer(self.model_name)
            print(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            print(f"Error loading model {self.model_name}: {e}")
            # Fallback to a smaller model if the main one fails
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                print("Loaded fallback embedding model: all-MiniLM-L6-v2")
            except Exception as e2:
                print(f"Error loading fallback model: {e2}")
                raise e2
                
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            numpy array of embeddings
        """
        if not self.model:
            raise RuntimeError("Embedding model not loaded")
            
        try:
            # Clean and preprocess text
            text = self._preprocess_text(text)
            
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            # Normalize the embedding for cosine similarity
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding.astype(np.float32)
            
        except Exception as e:
            print(f"Error generating embedding for text: {text[:100]}... Error: {e}")
            # Return zero vector as fallback
            return np.zeros(384, dtype=np.float32)
            
    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts efficiently
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            numpy array of embeddings (batch_size, embedding_dim)
        """
        if not self.model:
            raise RuntimeError("Embedding model not loaded")
            
        try:
            # Preprocess all texts
            processed_texts = [self._preprocess_text(text) for text in texts]
            
            # Generate embeddings in batch
            embeddings = self.model.encode(processed_texts, convert_to_numpy=True, batch_size=32)
            
            # Normalize embeddings
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            embeddings = embeddings / norms
            
            return embeddings.astype(np.float32)
            
        except Exception as e:
            print(f"Error generating batch embeddings: {e}")
            # Return zero vectors as fallback
            return np.zeros((len(texts), 384), dtype=np.float32)
            
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text before embedding generation
        
        Args:
            text: Raw input text
            
        Returns:
            Preprocessed text
        """
        if not text or not isinstance(text, str):
            return ""
            
        # Basic text cleaning
        text = text.strip()
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Truncate very long texts (model has token limits)
        max_length = 512  # Conservative limit for most sentence transformers
        if len(text) > max_length:
            text = text[:max_length]
            
        return text
        
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (-1 to 1)
        """
        try:
            # Ensure embeddings are normalized
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            embedding1 = embedding1 / norm1
            embedding2 = embedding2 / norm2
            
            # Compute cosine similarity
            similarity = np.dot(embedding1, embedding2)
            
            return float(similarity)
            
        except Exception as e:
            print(f"Error computing similarity: {e}")
            return 0.0
            
    def find_most_similar(self, query_embedding: np.ndarray, 
                         candidate_embeddings: np.ndarray, 
                         top_k: int = 5) -> List[tuple]:
        """
        Find most similar embeddings to a query
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: Array of candidate embeddings
            top_k: Number of top results to return
            
        Returns:
            List of (index, similarity_score) tuples
        """
        try:
            # Compute similarities
            similarities = np.dot(candidate_embeddings, query_embedding)
            
            # Get top k indices
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            # Return indices with similarity scores
            results = [(int(idx), float(similarities[idx])) for idx in top_indices]
            
            return results
            
        except Exception as e:
            print(f"Error finding similar embeddings: {e}")
            return []
            
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model"""
        if not self.model:
            return 384  # Default for all-MiniLM-L6-v2
        return self.model.get_sentence_embedding_dimension()
        
    def encode_for_search(self, text: str) -> np.ndarray:
        """
        Encode text specifically optimized for search/retrieval
        This is an alias for generate_embedding with potential future optimizations
        
        Args:
            text: Text to encode for search
            
        Returns:
            Search-optimized embedding
        """
        return self.generate_embedding(text)
        
    def __del__(self):
        """Cleanup when object is destroyed"""
        if hasattr(self, 'model') and self.model:
            del self.model