import json
from datetime import datetime
from aws_services import invoke_claude_sonnet


class EmotionAgent:
    """Agent for analyzing emotional tone and sentiment."""

    def __init__(self):
        pass

    def analyze_emotion(self, transcript, user_context=""):
        prompt = f"""
        You are an AI wellness assistant analyzing emotional health.
        Consider the user's context: {user_context}

        Analyze the emotional tone of the following transcript. Focus on detecting:
        - Primary emotion (happy, sad, anxious, lonely, confused, angry, calm, etc.)
        - Emotional intensity (1-10 scale)
        - Emotional stability indicators
        - Any concerning emotional patterns

        Transcript: {transcript}

        Provide your analysis in strict JSON format:
        {{
            "primary_emotion": "emotion_name",
            "confidence": 0.85,
            "intensity": 7,
            "stability": "stable/unstable",
            "concerning_patterns": ["pattern1", "pattern2"],
            "summary": "brief emotional summary",
            "timestamp": "{datetime.utcnow().isoformat()}"
        }}
        """
        response = invoke_claude_sonnet(prompt)
        return self.safe_json_parse(response)

    @staticmethod
    def safe_json_parse(response):
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "malformed_json", "raw": response}


class MemoryAgent:
    """Agent for analyzing cognitive patterns and memory indicators."""

    def __init__(self):
        pass

    def analyze_cognitive_patterns(self, transcript, user_context=""):
        prompt = f"""
        You are an AI cognitive health assistant analyzing memory and cognitive patterns.
        Consider the user's context: {user_context}

        Analyze the following transcript. Focus on:
        - Lexical diversity (vocabulary richness)
        - Sentence fluency and coherence
        - Repetition patterns
        - Memory-related indicators
        - Signs of cognitive decline

        Transcript: {transcript}

        Return JSON:
        {{
            "lexical_diversity": 0.75,
            "sentence_fluency": 0.8,
            "repetition_score": 0.2,
            "memory_indicators": ["indicator1", "indicator2"],
            "cognitive_concerns": ["concern1"],
            "overall_cognitive_health": "good/moderate/concerning",
            "timestamp": "{datetime.utcnow().isoformat()}"
        }}
        """
        response = invoke_claude_sonnet(prompt)
        return self.safe_json_parse(response)

    @staticmethod
    def safe_json_parse(response):
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "malformed_json", "raw": response}


class AlertAgent:
    """Agent for evaluating when caregiver alerts should be sent."""

    def __init__(self):
        pass

    def evaluate_alert_conditions(self, emotion_analysis, cognitive_analysis, recent_scores, user_context=""):
        prompt = f"""
        You are an AI caregiver alert assistant. Review the user's emotional and cognitive health, and decide if an alert is needed.

        Emotion Analysis: {emotion_analysis}
        Cognitive Analysis: {cognitive_analysis}
        Recent Scores (last 3 days): {recent_scores}

        Alert Conditions:
        - Cognora Score < 50 for 3 consecutive days
        - Emotion is "lonely" or "hopeless" for 2 consecutive days
        - Severe cognitive decline or instability
        - Emotional intensity >= 8 and stability is unstable

        Return JSON:
        {{
            "alert_needed": true/false,
            "alert_reason": "brief reason",
            "urgency": "low/medium/high",
            "recommended_action": "brief advice for caregiver",
            "timestamp": "{datetime.utcnow().isoformat()}"
        }}
        """
        response = invoke_claude_sonnet(prompt)
        return self.safe_json_parse(response)

    @staticmethod
    def safe_json_parse(response):
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "malformed_json", "raw": response}
