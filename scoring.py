import json
import re
from typing import Dict, Any
from nlp_metrics import analyze_cognitive_metrics
import spacy

def calculate_cognora_score(emotion_analysis, cognitive_metrics: dict) -> dict:
    """
    Calculates the Cognora Score (0-100) based on emotional and cognitive analysis.
    
    Args:
        emotion_analysis: dict or JSON string from EmotionAgent
        cognitive_metrics: Dictionary of metrics from nlp_metrics.py
    
    Returns:
        Dictionary containing score, breakdown, and wellness zone
    """
    try:
        # Parse analysis results
        if isinstance(emotion_analysis, str):
            emotion_data = json.loads(emotion_analysis)
        else:
            emotion_data = emotion_analysis
        
        # Extract metrics from NLP pipeline
        lexical_diversity = cognitive_metrics.get('lexical_diversity', 0.5)
        # Normalize sentence length (assuming avg 15 words is good)
        sentence_fluency = 1 - abs(15 - cognitive_metrics.get('avg_sentence_length', 15)) / 15
        coherence = cognitive_metrics.get('coherence_score', 0.5)

        # Extract metrics from Emotion Agent
        emotion_confidence = emotion_data.get('confidence', 0.5)
        emotion_intensity = emotion_data.get('intensity', 5) / 10.0  # Normalize to 0-1
        emotion_stability = 1.0 if emotion_data.get('stability') == 'stable' else 0.5
        
        # Calculate component scores (0-100 each)
        # Emotional score is based on stability and confidence, penalized by intensity of negative emotions
        emotion_score = (emotion_confidence * 0.5 + emotion_stability * 0.5) * 100
        if has_negative_sentiment(emotion_data.get('primary_emotion', '')):
             emotion_score -= emotion_intensity * 20 # Penalty for strong negative emotion

        # Cognitive score is based on vocabulary, fluency, and coherence
        cognitive_score = (lexical_diversity * 0.4 + sentence_fluency * 0.3 + coherence * 0.3) * 100
        
        # Weighted final score (emotion 50%, cognitive 50%)
        final_score = (emotion_score * 0.5) + (cognitive_score * 0.5)
        final_score = max(0, min(100, final_score)) # Clamp score between 0 and 100
        
        # Determine wellness zone
        if final_score >= 75:
            zone = "green"
            zone_name = "Excellent"
        elif final_score >= 50:
            zone = "yellow"
            zone_name = "Good"
        else:
            zone = "red"
            zone_name = "Concerning"
        
        return {
            'score': round(final_score, 1),
            'emotion_score': round(emotion_score, 1),
            'cognitive_score': round(cognitive_score, 1),
            'zone': zone,
            'zone_name': zone_name,
            'breakdown': {
                'emotion_confidence': emotion_confidence,
                'emotion_stability': emotion_stability,
                'emotion_intensity': emotion_intensity,
                'lexical_diversity': lexical_diversity,
                'sentence_fluency': sentence_fluency,
                'coherence': coherence
            }
        }
        
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error calculating Cognora Score: {e}")
        return {
            'score': 50.0,
            'emotion_score': 50.0,
            'cognitive_score': 50.0,
            'zone': 'yellow',
            'zone_name': 'Unknown',
            'breakdown': {},
            'error': str(e)
        }

def has_negative_sentiment(emotion: str) -> bool:
    """
    Checks for negative emotions to apply score penalties.
    """
    negative_emotions = ["sad", "lonely", "anxious", "angry", "worried", "frustrated", "confused"]
    return any(neg_emotion in emotion.lower() for neg_emotion in negative_emotions)

def analyze_text_metrics(text: str) -> Dict[str, float]:
    """
    Analyzes basic text metrics for scoring.
    
    Args:
        text: Input text to analyze
    
    Returns:
        Dictionary of text metrics
    """
    if not text:
        return {
            'word_count': 0,
            'unique_words': 0,
            'lexical_diversity': 0.0,
            'avg_sentence_length': 0.0,
            'repetition_ratio': 0.0
        }
    
    # Basic text processing
    words = re.findall(r'\b\w+\b', text.lower())
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Calculate metrics
    word_count = len(words)
    unique_words = len(set(words))
    lexical_diversity = unique_words / word_count if word_count > 0 else 0.0
    
    # Average sentence length
    sentence_lengths = [len(re.findall(r'\b\w+\b', s)) for s in sentences]
    avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0.0
    
    # Repetition analysis (simplified)
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    repeated_words = sum(1 for count in word_freq.values() if count > 1)
    repetition_ratio = repeated_words / len(word_freq) if word_freq else 0.0
    
    return {
        'word_count': word_count,
        'unique_words': unique_words,
        'lexical_diversity': lexical_diversity,
        'avg_sentence_length': avg_sentence_length,
        'repetition_ratio': repetition_ratio
    }

def get_score_color(score: float) -> str:
    """
    Returns the color for a given score.
    
    Args:
        score: Cognora Score (0-100)
    
    Returns:
        Color string for UI display
    """
    if score >= 75:
        return "#28a745"  # Green
    elif score >= 60:
        return "#ffc107"  # Yellow
    else:
        return "#dc3545"  # Red

def get_score_emoji(score: float) -> str:
    """
    Returns an emoji for a given score.
    
    Args:
        score: Cognora Score (0-100)
    
    Returns:
        Emoji string
    """
    if score >= 75:
        return "😊"
    elif score >= 60:
        return "😐"
    else:
        return "😔"

def generate_score_feedback(score_data: Dict[str, Any]) -> str:
    """
    Generates human-readable feedback based on score data.
    
    Args:
        score_data: Score calculation results
    
    Returns:
        Feedback string
    """
    score = score_data['score']
    zone = score_data['zone_name']
    
    if zone == "Excellent":
        return f"Excellent wellness score of {score}! You're showing strong emotional and cognitive health."
    elif zone == "Good":
        return f"Good wellness score of {score}. Your overall health is stable with room for improvement."
    else:
        return f"Your wellness score of {score} indicates some concerns. Consider reaching out to your support network."

def check_alert_conditions(recent_scores: list, recent_emotions: list, recent_cognitive_scores: list = None) -> dict:
    print("DEBUG: Recent scores for alert check:", recent_scores)
    if not recent_scores:
        print("DEBUG: No recent scores available.")
        return {
            'alert_needed': False,
            'reasons': ['No recent scores available'],
            'urgency': 'low'
        }
    # Immediate alert if any of the last 3 scores is below 60
    score_below_60 = any(score < 60 for score in recent_scores[-3:])
    print(f"DEBUG: score_below_60={score_below_60}")
    if score_below_60:
        return {
            'alert_needed': True,
            'reasons': ['Immediate alert: Cognora score below 60'],
            'urgency': 'high'
        }
    # ... (rest of your logic if needed) ...

nlp = spacy.load("en_core_web_lg")
