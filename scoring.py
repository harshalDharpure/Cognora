import json
import re
from typing import Dict, Any

def calculate_cognora_score(emotion_analysis: str, cognitive_analysis: str) -> Dict[str, Any]:
    """
    Calculates the Cognora Score (0-100) based on emotional and cognitive analysis.
    
    Args:
        emotion_analysis: JSON string from EmotionAgent
        cognitive_analysis: JSON string from MemoryAgent
    
    Returns:
        Dictionary containing score, breakdown, and wellness zone
    """
    try:
        # Parse analysis results
        emotion_data = json.loads(emotion_analysis)
        cognitive_data = json.loads(cognitive_analysis)
        
        # Extract metrics
        emotion_confidence = emotion_data.get('confidence', 0.5)
        emotion_intensity = emotion_data.get('intensity', 5) / 10.0  # Normalize to 0-1
        emotion_stability = 1.0 if emotion_data.get('stability') == 'stable' else 0.5
        
        lexical_diversity = cognitive_data.get('lexical_diversity', 0.5)
        sentence_fluency = cognitive_data.get('sentence_fluency', 0.5)
        repetition_score = cognitive_data.get('repetition_score', 0.5)
        
        # Calculate component scores (0-100 each)
        emotion_score = (emotion_confidence * 0.4 + emotion_stability * 0.4 + (1 - emotion_intensity) * 0.2) * 100
        cognitive_score = (lexical_diversity * 0.4 + sentence_fluency * 0.4 + (1 - repetition_score) * 0.2) * 100
        
        # Weighted final score (emotion 60%, cognitive 40%)
        final_score = (emotion_score * 0.6) + (cognitive_score * 0.4)
        
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
                'repetition_score': repetition_score
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
    elif score >= 50:
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
    elif score >= 50:
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

def check_alert_conditions(recent_scores: list, recent_emotions: list) -> Dict[str, Any]:
    """
    Checks if alert conditions are met based on recent scores and emotions.
    
    Args:
        recent_scores: List of recent Cognora scores
        recent_emotions: List of recent primary emotions
    
    Returns:
        Alert evaluation results
    """
    if len(recent_scores) < 3:
        return {'alert_needed': False, 'reason': 'Insufficient data'}
    
    # Check for 3 consecutive days with score < 50
    low_score_days = sum(1 for score in recent_scores[-3:] if score < 50)
    score_alert = low_score_days >= 3
    
    # Check for 2 consecutive days with "lonely" emotion
    lonely_days = sum(1 for emotion in recent_emotions[-2:] if 'lonely' in emotion.lower())
    emotion_alert = lonely_days >= 2
    
    alert_needed = score_alert or emotion_alert
    
    reasons = []
    if score_alert:
        reasons.append("Low wellness scores for 3+ consecutive days")
    if emotion_alert:
        reasons.append("Lonely emotion detected for 2+ consecutive days")
    
    return {
        'alert_needed': alert_needed,
        'reasons': reasons,
        'urgency': 'high' if alert_needed else 'low'
    }
