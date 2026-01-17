"""
Answer Similarity Detection using Sentence Transformers

Uses semantic embeddings to detect similar/copied answers between students.
This helps identify potential collusion or answer sharing.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import os

# Lazy loading for sentence-transformers (heavy import)
_model = None
_model_name = "all-MiniLM-L6-v2"  # Fast, good quality, 384 dimensions


def get_model():
    """Lazy load the sentence transformer model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            print(f"📥 Loading sentence-transformers model: {_model_name}")
            _model = SentenceTransformer(_model_name)
            print("✅ Model loaded successfully!")
        except ImportError:
            print("⚠️ sentence-transformers not installed, using fallback similarity")
            _model = "fallback"
    return _model


@dataclass
class SimilarityResult:
    """Result of comparing two answers."""
    answer1_id: str
    answer2_id: str
    similarity_score: float
    is_suspicious: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "answer1_id": self.answer1_id,
            "answer2_id": self.answer2_id,
            "similarity_score": self.similarity_score,
            "is_suspicious": self.is_suspicious,
        }


@dataclass
class SimilarityReport:
    """Report of answer similarity analysis for a question."""
    question_id: str
    total_answers: int
    suspicious_pairs: List[SimilarityResult]
    max_similarity: float
    mean_similarity: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "total_answers": self.total_answers,
            "suspicious_pairs": [p.to_dict() for p in self.suspicious_pairs],
            "max_similarity": self.max_similarity,
            "mean_similarity": self.mean_similarity,
        }


class AnswerSimilarityModel:
    """
    Detects similar answers between students using semantic embeddings.
    
    Uses sentence-transformers to create dense vector representations
    of answers, then computes cosine similarity.
    """
    
    def __init__(self, threshold: float = 0.85):
        """
        Initialize the similarity model.
        
        Args:
            threshold: Similarity score above which pairs are flagged (0-1)
        """
        self.threshold = threshold
        self._embeddings_cache: Dict[str, np.ndarray] = {}
    
    def compute_embedding(self, text: str) -> np.ndarray:
        """
        Compute the embedding vector for a text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as numpy array
        """
        model = get_model()
        
        if model == "fallback":
            # Fallback: simple bag-of-words style embedding
            return self._fallback_embedding(text)
        
        # Use sentence-transformers
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding
    
    def _fallback_embedding(self, text: str) -> np.ndarray:
        """Simple fallback embedding when sentence-transformers unavailable."""
        # Create a simple character/word frequency vector
        words = text.lower().split()
        # Use hash to create pseudo-random but deterministic features
        features = np.zeros(384)  # Match model dimension
        for i, word in enumerate(words):
            idx = hash(word) % 384
            features[idx] += 1
        # Normalize
        norm = np.linalg.norm(features)
        if norm > 0:
            features = features / norm
        return features
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        emb1 = self.compute_embedding(text1)
        emb2 = self.compute_embedding(text2)
        
        # Cosine similarity
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(max(0, min(1, similarity)))  # Clamp to [0, 1]
    
    def find_similar_pairs(
        self, 
        answers: List[Dict[str, str]],
        question_id: str
    ) -> SimilarityReport:
        """
        Find all pairs of similar answers for a question.
        
        Args:
            answers: List of {"session_id": str, "content": str} dictionaries
            question_id: Question identifier
            
        Returns:
            SimilarityReport with suspicious pairs
        """
        if len(answers) < 2:
            return SimilarityReport(
                question_id=question_id,
                total_answers=len(answers),
                suspicious_pairs=[],
                max_similarity=0.0,
                mean_similarity=0.0,
            )
        
        # Compute all embeddings
        embeddings = []
        for answer in answers:
            content = answer.get("content", "")
            if content:
                emb = self.compute_embedding(content)
                embeddings.append((answer.get("session_id", ""), emb))
        
        # Compare all pairs
        similarities = []
        suspicious_pairs = []
        
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                id1, emb1 = embeddings[i]
                id2, emb2 = embeddings[j]
                
                # Cosine similarity
                similarity = float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
                similarity = max(0, min(1, similarity))
                similarities.append(similarity)
                
                if similarity >= self.threshold:
                    suspicious_pairs.append(SimilarityResult(
                        answer1_id=id1,
                        answer2_id=id2,
                        similarity_score=similarity,
                        is_suspicious=True,
                    ))
        
        # Sort by similarity (highest first)
        suspicious_pairs.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return SimilarityReport(
            question_id=question_id,
            total_answers=len(answers),
            suspicious_pairs=suspicious_pairs,
            max_similarity=max(similarities) if similarities else 0.0,
            mean_similarity=sum(similarities) / len(similarities) if similarities else 0.0,
        )


# Convenience functions
def compute_similarity(text1: str, text2: str, threshold: float = 0.85) -> Tuple[float, bool]:
    """
    Compute similarity between two texts.
    
    Returns:
        Tuple of (similarity_score, is_suspicious)
    """
    model = AnswerSimilarityModel(threshold=threshold)
    score = model.compute_similarity(text1, text2)
    return score, score >= threshold


def find_similar_answers(
    answers: List[Dict[str, str]], 
    question_id: str,
    threshold: float = 0.85
) -> SimilarityReport:
    """
    Find similar answers among a list of submissions.
    
    Args:
        answers: List of {"session_id": str, "content": str}
        question_id: Question identifier
        threshold: Similarity threshold for flagging
        
    Returns:
        SimilarityReport with analysis results
    """
    model = AnswerSimilarityModel(threshold=threshold)
    return model.find_similar_pairs(answers, question_id)
