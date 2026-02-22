"""
Similarity Feature Extractor

Detects whether student answers are:
1. AI-generated (using linguistic analysis + sentence embeddings)
2. Available online (using Google Custom Search API)

Cross-references with tab-switching data to determine severity:
- Found online + tab switch → HIGH priority
- Found online + no tab switch → MEDIUM priority
- AI-detected → proportional to confidence
"""

import re
import math
import logging
import urllib.parse
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)


# ─── Data Classes ────────────────────────────────────────────────────────────

@dataclass
class SimilarityFeatures:
    """Features extracted from similarity analysis."""
    ai_confidence: float = 0.0           # 0–1, how likely AI-generated
    ai_indicators: List[str] = field(default_factory=list)
    web_match_score: float = 0.0         # 0–1, how much matched online
    matched_sources: List[str] = field(default_factory=list)
    tab_switch_detected: bool = False    # Cross-referenced from focus features
    suspicion_level: str = "low"         # low / medium / high
    flag_reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ai_confidence": round(self.ai_confidence, 3),
            "ai_indicators": self.ai_indicators,
            "web_match_score": round(self.web_match_score, 3),
            "matched_sources": self.matched_sources,
            "tab_switch_detected": self.tab_switch_detected,
            "suspicion_level": self.suspicion_level,
            "flag_reasons": self.flag_reasons,
        }


# ─── AI Detection ───────────────────────────────────────────────────────────

class AIDetector:
    """
    Detects AI-generated text using linguistic feature analysis
    and sentence embedding uniformity.

    Key signals:
    - Sentence length uniformity (AI writes unnaturally consistent sentences)
    - Vocabulary sophistication patterns
    - Hedging / filler phrase density
    - Transition word overuse
    - Low burstiness (human writing varies; AI is flat)
    - Embedding uniformity (AI sentences cluster tightly in embedding space)
    """

    # Phrases strongly associated with AI-generated text
    AI_HEDGE_PHRASES = [
        "it is important to note",
        "it's important to note",
        "it is worth mentioning",
        "in today's world",
        "in today's digital age",
        "in the rapidly evolving",
        "it is crucial to",
        "it is essential to",
        "plays a crucial role",
        "plays a vital role",
        "in conclusion",
        "to summarize",
        "in summary",
        "overall,",
        "furthermore,",
        "moreover,",
        "additionally,",
        "consequently,",
        "nevertheless,",
        "on the other hand,",
        "in other words,",
        "as a result,",
        "for instance,",
        "for example,",
        "it can be argued that",
        "one could argue that",
        "this suggests that",
        "this indicates that",
        "this demonstrates that",
        "delve into",
        "delves into",
        "shed light on",
        "sheds light on",
        "multifaceted",
        "nuanced",
        "paradigm",
        "leverage",
        "utilize",
        "facilitate",
        "comprehensive",
        "robust",
    ]

    # Transition words overused by AI
    AI_TRANSITIONS = [
        "however", "therefore", "furthermore", "moreover",
        "additionally", "consequently", "nevertheless",
        "subsequently", "accordingly", "thus", "hence",
        "meanwhile", "likewise", "similarly", "conversely",
    ]

    def __init__(self):
        self._embedder = None  # Lazy-loaded

    def _get_embedder(self):
        """Lazy-load sentence transformer model."""
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedder = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("Loaded sentence-transformers model for AI detection")
            except ImportError:
                logger.warning("sentence-transformers not available; skipping embedding analysis")
            except Exception as e:
                logger.warning(f"Failed to load embedding model: {e}")
        return self._embedder

    def detect(self, text: str) -> tuple:
        """
        Analyze text for AI-generation signals.

        Returns:
            (ai_confidence: float, indicators: list[str])
        """
        if not text or len(text.strip()) < 30:
            return 0.0, []

        clean = text.strip()
        words = re.findall(r'\b\w+\b', clean.lower())
        sentences = [s.strip() for s in re.split(r'[.!?]+', clean) if s.strip()]

        if len(words) < 10 or len(sentences) < 2:
            return 0.0, []

        indicators = []
        scores = []

        # ── 1. Hedge/filler phrase density ──
        hedge_score = self._hedge_phrase_score(clean.lower(), len(words))
        scores.append(("hedge", hedge_score, 0.20))
        if hedge_score > 0.4:
            indicators.append(f"AI-typical phrases detected (score: {hedge_score:.0%})")

        # ── 2. Sentence length uniformity ──
        uniformity_score = self._sentence_uniformity(sentences)
        scores.append(("uniformity", uniformity_score, 0.20))
        if uniformity_score > 0.5:
            indicators.append(f"Unnaturally uniform sentence lengths (score: {uniformity_score:.0%})")

        # ── 3. Transition word overuse ──
        transition_score = self._transition_overuse(words)
        scores.append(("transitions", transition_score, 0.15))
        if transition_score > 0.4:
            indicators.append(f"Excessive transition words (score: {transition_score:.0%})")

        # ── 4. Vocabulary sophistication ──
        vocab_score = self._vocabulary_sophistication(words)
        scores.append(("vocabulary", vocab_score, 0.15))
        if vocab_score > 0.5:
            indicators.append(f"Unusual vocabulary sophistication (score: {vocab_score:.0%})")

        # ── 5. Burstiness (low = AI-like) ──
        burstiness_score = self._burstiness_score(sentences)
        scores.append(("burstiness", burstiness_score, 0.15))
        if burstiness_score > 0.5:
            indicators.append(f"Low writing burstiness / too uniform (score: {burstiness_score:.0%})")

        # ── 6. Embedding uniformity (if model available) ──
        embedding_score = self._embedding_uniformity(sentences)
        scores.append(("embedding", embedding_score, 0.15))
        if embedding_score > 0.5:
            indicators.append(f"Sentence embedding clustering detected (score: {embedding_score:.0%})")

        # Weighted combination
        total_weight = sum(w for _, _, w in scores)
        ai_confidence = sum(s * w for _, s, w in scores) / total_weight if total_weight > 0 else 0.0
        ai_confidence = max(0.0, min(1.0, ai_confidence))

        return ai_confidence, indicators

    def _hedge_phrase_score(self, text_lower: str, word_count: int) -> float:
        """Score based on density of AI-typical hedge phrases."""
        matches = 0
        for phrase in self.AI_HEDGE_PHRASES:
            if phrase in text_lower:
                matches += 1

        if word_count < 20:
            return 0.0

        # Normalize: expect roughly 1 per 50 words in AI text
        density = matches / (word_count / 50)
        return min(1.0, density / 2.0)  # 2+ matches per 50 words → score 1.0

    def _sentence_uniformity(self, sentences: list) -> float:
        """
        Score how uniform sentence lengths are.
        AI text tends to have very consistent sentence lengths.
        Human text is naturally bursty.
        """
        if len(sentences) < 3:
            return 0.0

        lengths = [len(s.split()) for s in sentences if len(s.split()) > 2]
        if len(lengths) < 3:
            return 0.0

        mean_len = sum(lengths) / len(lengths)
        if mean_len == 0:
            return 0.0

        # Coefficient of variation (CV)
        variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        cv = std_dev / mean_len

        # Low CV = uniform = AI-like
        # Human CV typically 0.4-0.8, AI typically 0.1-0.3
        if cv < 0.15:
            return 0.9
        elif cv < 0.25:
            return 0.7
        elif cv < 0.35:
            return 0.4
        elif cv < 0.50:
            return 0.2
        return 0.0

    def _transition_overuse(self, words: list) -> float:
        """Score based on transition word density."""
        transition_count = sum(1 for w in words if w in self.AI_TRANSITIONS)
        if len(words) < 20:
            return 0.0

        density = transition_count / (len(words) / 100)
        # AI text typically has 3-5+ transitions per 100 words
        return min(1.0, density / 4.0)

    def _vocabulary_sophistication(self, words: list) -> float:
        """
        Score based on vocabulary sophistication patterns.
        AI tends to use a higher proportion of "fancy" words consistently.
        """
        if len(words) < 20:
            return 0.0

        def syllable_count(word):
            word = word.lower()
            count = 0
            vowels = "aeiou"
            if word[0] in vowels:
                count += 1
            for i in range(1, len(word)):
                if word[i] in vowels and word[i - 1] not in vowels:
                    count += 1
            if word.endswith("e"):
                count -= 1
            return max(1, count)

        # Complex words (3+ syllables)
        complex_count = sum(1 for w in words if syllable_count(w) >= 3)
        complex_ratio = complex_count / len(words)

        # AI text typically: 15-25% complex words
        # Human casual: 5-12%
        if complex_ratio > 0.25:
            return 0.9
        elif complex_ratio > 0.18:
            return 0.6
        elif complex_ratio > 0.12:
            return 0.3
        return 0.0

    def _burstiness_score(self, sentences: list) -> float:
        """
        Measure burstiness — variation in complexity across sentences.
        AI writes very evenly; humans have bursts of simple + complex.
        """
        if len(sentences) < 4:
            return 0.0

        # Compute complexity per sentence (word length + sentence length combo)
        complexities = []
        for s in sentences:
            words = s.split()
            if not words:
                continue
            avg_word_len = sum(len(w) for w in words) / len(words)
            complexities.append(avg_word_len * len(words))

        if len(complexities) < 4:
            return 0.0

        mean_c = sum(complexities) / len(complexities)
        if mean_c == 0:
            return 0.0

        variance = sum((c - mean_c) ** 2 for c in complexities) / len(complexities)
        cv = math.sqrt(variance) / mean_c

        # Low CV = flat = AI-like
        if cv < 0.2:
            return 0.8
        elif cv < 0.35:
            return 0.5
        elif cv < 0.5:
            return 0.2
        return 0.0

    def _embedding_uniformity(self, sentences: list) -> float:
        """
        Use sentence embeddings to check if sentences cluster too tightly.
        AI-generated text produces very similar embeddings across sentences.
        """
        embedder = self._get_embedder()
        if embedder is None or len(sentences) < 3:
            return 0.0

        try:
            # Filter to meaningful sentences only
            valid = [s for s in sentences if len(s.split()) >= 4]
            if len(valid) < 3:
                return 0.0

            # Use at most 10 sentences for performance
            sample = valid[:10]
            embeddings = embedder.encode(sample)

            # Compute pairwise cosine similarities
            import numpy as np
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms = np.clip(norms, 1e-8, None)
            normalized = embeddings / norms
            sim_matrix = np.dot(normalized, normalized.T)

            # Average off-diagonal similarity
            n = len(sample)
            total_sim = 0
            count = 0
            for i in range(n):
                for j in range(i + 1, n):
                    total_sim += sim_matrix[i][j]
                    count += 1

            avg_sim = total_sim / count if count > 0 else 0

            # High avg similarity = sentences too alike = AI-like
            # Human text: avg 0.3-0.5, AI text: avg 0.5-0.8
            if avg_sim > 0.7:
                return 0.9
            elif avg_sim > 0.6:
                return 0.7
            elif avg_sim > 0.5:
                return 0.4
            elif avg_sim > 0.4:
                return 0.15
            return 0.0

        except Exception as e:
            logger.warning(f"Embedding analysis failed: {e}")
            return 0.0


# ─── Web Source Checking ─────────────────────────────────────────────────────

class WebSourceChecker:
    """
    Checks if answer text can be found online using Google Custom Search API.

    Extracts significant sentences from the answer and searches for them.
    Returns a match score based on how many snippets are found online.
    """

    def __init__(self, api_key: str = "", search_cx: str = ""):
        self.api_key = api_key
        self.search_cx = search_cx

    def check(self, text: str) -> tuple:
        """
        Search for text snippets online.

        Returns:
            (web_match_score: float, matched_sources: list[str])
        """
        if not self.api_key or not self.search_cx:
            return 0.0, []

        if not text or len(text.strip()) < 30:
            return 0.0, []

        # Extract the most significant sentences to search
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip().split()) >= 6]
        if not sentences:
            return 0.0, []

        # Pick up to 3 longest sentences (most distinctive)
        sentences.sort(key=len, reverse=True)
        search_sentences = sentences[:3]

        matched_sources = []
        match_count = 0

        for sentence in search_sentences:
            try:
                sources = self._search_google(sentence)
                if sources:
                    match_count += 1
                    matched_sources.extend(sources[:2])  # Top 2 sources per query
            except Exception as e:
                logger.warning(f"Google search failed for snippet: {e}")
                continue

        # Score: proportion of searched sentences that had matches
        web_score = match_count / len(search_sentences) if search_sentences else 0.0

        # Deduplicate sources
        seen = set()
        unique_sources = []
        for s in matched_sources:
            if s not in seen:
                seen.add(s)
                unique_sources.append(s)

        return min(1.0, web_score), unique_sources[:5]

    def _search_google(self, query: str) -> List[str]:
        """
        Search Google Custom Search API for exact phrase match.

        Returns list of matching source URLs.
        """
        import urllib.request
        import json

        # Use exact phrase matching by wrapping in quotes
        exact_query = f'"{query[:128]}"'  # Limit query length
        encoded = urllib.parse.quote(exact_query)

        url = (
            f"https://www.googleapis.com/customsearch/v1"
            f"?key={self.api_key}"
            f"&cx={self.search_cx}"
            f"&q={encoded}"
            f"&num=3"
        )

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "CheatingDetector/1.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())

            sources = []
            for item in data.get("items", []):
                link = item.get("link", "")
                if link:
                    sources.append(link)

            return sources

        except urllib.error.HTTPError as e:
            if e.code == 429:
                logger.warning("Google API quota exceeded")
            else:
                logger.warning(f"Google API error: {e.code}")
            return []
        except Exception as e:
            logger.warning(f"Google search request failed: {e}")
            return []


# ─── Score Calculation ───────────────────────────────────────────────────────

def calculate_similarity_score(
    ai_confidence: float,
    web_match_score: float,
    tab_switch_detected: bool
) -> float:
    """
    Combine AI detection and web source scores with tab-switch context.

    Priority logic:
    - Found online + tab-switch detected → HIGH (0.8–1.0)
    - Found online + no tab-switch → MEDIUM (0.4–0.6)
    - AI-detected (regardless) → proportional to confidence
    """
    # Base: weighted combination
    base = (ai_confidence * 0.6) + (web_match_score * 0.4)

    # Escalate based on web match + tab-switch combo
    if web_match_score > 0.3 and tab_switch_detected:
        base = max(base, 0.8)  # HIGH priority
    elif web_match_score > 0.3 and not tab_switch_detected:
        base = max(base, 0.4)  # MEDIUM priority

    return max(0.0, min(1.0, base))


def determine_suspicion_level(score: float) -> str:
    """Map score to human-readable suspicion level."""
    if score >= 0.7:
        return "high"
    elif score >= 0.4:
        return "medium"
    return "low"


# ─── Main Extraction Function ───────────────────────────────────────────────

# Module-level singleton for the AI detector (expensive to initialize)
_ai_detector: Optional[AIDetector] = None


def _get_ai_detector() -> AIDetector:
    """Get or create the singleton AI detector."""
    global _ai_detector
    if _ai_detector is None:
        _ai_detector = AIDetector()
    return _ai_detector


def extract_similarity_features(
    answers: Dict[str, str],
    tab_switch_detected: bool = False,
    api_key: str = "",
    search_cx: str = "",
) -> SimilarityFeatures:
    """
    Extract similarity features from student answers.

    Args:
        answers: Dict of question_id -> answer_text
        tab_switch_detected: Whether focus/blur events indicate tab switching
        api_key: Google Custom Search API key
        search_cx: Google Custom Search engine ID

    Returns:
        SimilarityFeatures with AI detection and web source check results
    """
    features = SimilarityFeatures(tab_switch_detected=tab_switch_detected)

    if not answers:
        return features

    # Combine all answers for analysis
    all_text = " ".join(answers.values())

    if len(all_text.strip()) < 30:
        return features

    # ── AI Detection ──
    detector = _get_ai_detector()
    ai_confidence, ai_indicators = detector.detect(all_text)
    features.ai_confidence = ai_confidence
    features.ai_indicators = ai_indicators

    # ── Web Source Check ──
    if api_key and search_cx:
        checker = WebSourceChecker(api_key=api_key, search_cx=search_cx)
        web_score, matched_sources = checker.check(all_text)
        features.web_match_score = web_score
        features.matched_sources = matched_sources

    # ── Calculate combined score and level ──
    score = calculate_similarity_score(
        features.ai_confidence,
        features.web_match_score,
        tab_switch_detected
    )
    features.suspicion_level = determine_suspicion_level(score)

    # ── Generate flag reasons ──
    if ai_confidence >= 0.4:
        features.flag_reasons.append(
            f"Possible AI-generated content (confidence: {ai_confidence:.0%})"
        )
        if ai_indicators:
            features.flag_reasons.append(ai_indicators[0])  # Top indicator

    if features.web_match_score > 0.3:
        source_preview = features.matched_sources[0] if features.matched_sources else "web"
        if tab_switch_detected:
            features.flag_reasons.append(
                f"Answer found online + tab switching detected (HIGH risk) — {source_preview}"
            )
        else:
            features.flag_reasons.append(
                f"Answer found online (MEDIUM risk, no tab switch) — {source_preview}"
            )

    return features
