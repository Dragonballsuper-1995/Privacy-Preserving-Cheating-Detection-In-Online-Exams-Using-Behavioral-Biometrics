"""
Text Analysis Feature Extractor

Analyzes subjective answer text for suspicious patterns that may indicate:
- AI-generated content
- Copy-pasted content from external sources
- Template-like responses
- Unusual writing patterns
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import math


@dataclass
class TextFeatures:
    """Features extracted from text content."""
    
    # Basic metrics
    word_count: int = 0
    sentence_count: int = 0
    avg_word_length: float = 0.0
    avg_sentence_length: float = 0.0
    
    # Complexity metrics
    vocabulary_richness: float = 0.0  # Unique words / total words
    complex_word_ratio: float = 0.0   # Words with 3+ syllables
    
    # Suspicious pattern indicators
    formal_language_score: float = 0.0  # Unusually formal language
    repetition_score: float = 0.0       # Repeated phrases
    template_score: float = 0.0         # Template-like structure
    
    # Final scores
    suspicion_score: float = 0.0
    flag_reasons: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "word_count": self.word_count,
            "sentence_count": self.sentence_count,
            "avg_word_length": round(self.avg_word_length, 2),
            "avg_sentence_length": round(self.avg_sentence_length, 2),
            "vocabulary_richness": round(self.vocabulary_richness, 3),
            "complex_word_ratio": round(self.complex_word_ratio, 3),
            "formal_language_score": round(self.formal_language_score, 3),
            "repetition_score": round(self.repetition_score, 3),
            "template_score": round(self.template_score, 3),
            "suspicion_score": round(self.suspicion_score, 3),
            "flag_reasons": self.flag_reasons,
        }


class TextAnalyzer:
    """Analyzes text for suspicious patterns."""
    
    # Formal/AI-like phrases that rarely appear in natural student writing
    FORMAL_PHRASES = [
        "it is important to note",
        "in conclusion",
        "furthermore",
        "moreover",
        "in summary",
        "to summarize",
        "it should be noted",
        "as mentioned above",
        "as previously stated",
        "in other words",
        "on the other hand",
        "for instance",
        "for example",
        "in addition",
        "additionally",
        "consequently",
        "therefore",
        "thus",
        "hence",
        "whereby",
        "nonetheless",
        "nevertheless",
    ]
    
    # Template patterns (markdown-like structure)
    TEMPLATE_PATTERNS = [
        r"^#+\s",           # Markdown headers
        r"^\*\*.*\*\*",     # Bold text at start
        r"^\d+\.\s",        # Numbered lists
        r"^[-*]\s",         # Bullet points
        r"```",             # Code blocks
    ]
    
    def __init__(self, suspicion_threshold: float = 0.6):
        self.suspicion_threshold = suspicion_threshold
    
    def count_syllables(self, word: str) -> int:
        """Estimate syllable count in a word."""
        word = word.lower()
        vowels = "aeiouy"
        count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent e
        if word.endswith('e') and count > 1:
            count -= 1
        
        return max(1, count)
    
    def analyze_text(self, text: str, question_type: str = "subjective") -> TextFeatures:
        """
        Analyze text for suspicious patterns.
        
        Args:
            text: The answer text to analyze
            question_type: Type of question (subjective, coding, etc.)
            
        Returns:
            TextFeatures with extracted metrics and suspicion score
        """
        features = TextFeatures()
        
        if not text or len(text.strip()) < 10:
            return features
        
        # Clean text
        clean_text = text.strip()
        
        # Basic metrics
        words = re.findall(r'\b\w+\b', clean_text.lower())
        sentences = re.split(r'[.!?]+', clean_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        features.word_count = len(words)
        features.sentence_count = len(sentences)
        
        if features.word_count > 0:
            features.avg_word_length = sum(len(w) for w in words) / len(words)
            
            # Vocabulary richness
            unique_words = set(words)
            features.vocabulary_richness = len(unique_words) / len(words)
            
            # Complex word ratio (3+ syllables)
            complex_words = sum(1 for w in words if self.count_syllables(w) >= 3)
            features.complex_word_ratio = complex_words / len(words)
        
        if features.sentence_count > 0:
            features.avg_sentence_length = features.word_count / features.sentence_count
        
        # Formal language detection
        formal_count = 0
        text_lower = clean_text.lower()
        for phrase in self.FORMAL_PHRASES:
            if phrase in text_lower:
                formal_count += 1
        
        # Normalize by text length
        if features.word_count > 20:
            features.formal_language_score = min(1.0, formal_count / 3)
        
        # Template pattern detection
        lines = clean_text.split('\n')
        template_matches = 0
        for line in lines:
            for pattern in self.TEMPLATE_PATTERNS:
                if re.match(pattern, line.strip()):
                    template_matches += 1
                    break
        
        if len(lines) > 0:
            features.template_score = min(1.0, template_matches / max(3, len(lines) * 0.5))
        
        # Repetition detection (n-gram analysis)
        if features.word_count >= 10:
            # Check for repeated 3-grams
            trigrams = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
            if trigrams:
                unique_trigrams = set(trigrams)
                repetition_ratio = 1 - (len(unique_trigrams) / len(trigrams))
                features.repetition_score = repetition_ratio
        
        # Calculate overall suspicion score
        # Weighted combination of indicators
        features.suspicion_score = (
            features.formal_language_score * 0.35 +
            features.template_score * 0.35 +
            features.repetition_score * 0.15 +
            (1 - features.vocabulary_richness) * 0.15  # Low vocabulary diversity is suspicious
        )
        
        # Clamp to [0, 1]
        features.suspicion_score = max(0.0, min(1.0, features.suspicion_score))
        
        # Generate flag reasons
        if features.formal_language_score > 0.5:
            features.flag_reasons.append("Unusually formal language patterns detected")
        
        if features.template_score > 0.4:
            features.flag_reasons.append("Template-like formatting detected")
        
        if features.repetition_score > 0.3:
            features.flag_reasons.append("High phrase repetition")
        
        if features.vocabulary_richness < 0.4 and features.word_count > 30:
            features.flag_reasons.append("Low vocabulary diversity")
        
        if features.avg_sentence_length > 25:
            features.flag_reasons.append("Unusually long sentences (possible copy-paste)")
        
        return features
    
    def analyze_answers(self, answers: Dict[str, str]) -> Dict[str, TextFeatures]:
        """
        Analyze multiple answers from a session.
        
        Args:
            answers: Dictionary of question_id -> answer_text
            
        Returns:
            Dictionary of question_id -> TextFeatures
        """
        results = {}
        for question_id, answer_text in answers.items():
            results[question_id] = self.analyze_text(answer_text)
        return results
    
    def get_aggregate_score(self, answers: Dict[str, str]) -> float:
        """
        Get aggregate suspicion score across all answers.
        
        Returns weighted average based on answer length.
        """
        if not answers:
            return 0.0
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for answer_text in answers.values():
            features = self.analyze_text(answer_text)
            weight = math.log1p(features.word_count)  # Log scale for length weight
            weighted_sum += features.suspicion_score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return weighted_sum / total_weight


def extract_text_features(answers: Dict[str, str], suspicion_threshold: float = 0.6) -> Dict[str, TextFeatures]:
    """
    Convenience function to extract text features from answers.
    
    Args:
        answers: Dictionary of question_id -> answer_text
        suspicion_threshold: Threshold for flagging (0-1)
        
    Returns:
        Dictionary of question_id -> TextFeatures
    """
    analyzer = TextAnalyzer(suspicion_threshold=suspicion_threshold)
    return analyzer.analyze_answers(answers)


def get_text_suspicion_score(answers: Dict[str, str]) -> float:
    """
    Get aggregate text suspicion score.
    
    Args:
        answers: Dictionary of question_id -> answer_text
        
    Returns:
        Aggregate suspicion score (0-1)
    """
    analyzer = TextAnalyzer()
    return analyzer.get_aggregate_score(answers)
