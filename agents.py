from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.prompts import StringPromptTemplate
from langchain.schema import AgentAction, AgentFinish
from langchain.memory import ConversationBufferMemory
from aws_services import invoke_claude_sonnet
import re
from typing import List, Union

class EmotionAgent:
    """Agent for analyzing emotional tone and sentiment."""
    
    def __init__(self):
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        
    def analyze_emotion(self, transcript):
        """Analyzes the emotional tone of the transcript."""
        prompt = f"""
        Analyze the emotional tone of the following transcript. Focus on detecting:
        - Primary emotion (happy, sad, anxious, lonely, confused, angry, calm, etc.)
        - Emotional intensity (1-10 scale)
        - Emotional stability indicators
        - Any concerning emotional patterns
        
        Transcript: {transcript}
        
        Provide your analysis in JSON format:
        {{
            "primary_emotion": "emotion_name",
            "confidence": 0.85,
            "intensity": 7,
            "stability": "stable/unstable",
            "concerning_patterns": ["pattern1", "pattern2"],
            "summary": "brief emotional summary"
        }}
        """
        
        response = invoke_claude_sonnet(prompt)
        return response

class MemoryAgent:
    """Agent for analyzing cognitive patterns and memory indicators."""
    
    def __init__(self):
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        
    def analyze_cognitive_patterns(self, transcript):
        """Analyzes cognitive patterns and memory indicators."""
        prompt = f"""
        Analyze the cognitive patterns in the following transcript. Focus on:
        - Lexical diversity (vocabulary richness)
        - Sentence fluency and coherence
        - Repetition patterns
        - Memory-related indicators
        - Cognitive decline signs
        
        Transcript: {transcript}
        
        Provide your analysis in JSON format:
        {{
            "lexical_diversity": 0.75,
            "sentence_fluency": 0.8,
            "repetition_score": 0.2,
            "memory_indicators": ["indicator1", "indicator2"],
            "cognitive_concerns": ["concern1", "concern2"],
            "overall_cognitive_health": "good/moderate/concerning"
        }}
        """
        
        response = invoke_claude_sonnet(prompt)
        return response

class AlertAgent:
    """Agent for determining when to send caregiver alerts."""
    
    def __init__(self):
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        
    def evaluate_alert_conditions(self, emotion_analysis, cognitive_analysis, recent_scores):
        """Evaluates whether alert conditions are met."""
        prompt = f"""
        Evaluate whether caregiver alert conditions are met based on:
        
        Emotion Analysis: {emotion_analysis}
        Cognitive Analysis: {cognitive_analysis}
        Recent Scores: {recent_scores}
        
        Alert Conditions:
        1. Cognora Score < 50 for 3 consecutive days
        2. Emotion is "lonely" for 2 consecutive days
        3. Severe cognitive decline indicators
        4. High emotional distress
        
        Provide your evaluation in JSON format:
        {{
            "alert_needed": true/false,
            "alert_reason": "reason for alert",
            "urgency": "low/medium/high",
            "recommended_action": "suggested action for caregiver"
        }}
        """
        
        response = invoke_claude_sonnet(prompt)
        return response

def create_emotion_analysis_prompt(transcript, user_context=""):
    """Creates a personalized prompt for emotion analysis."""
    return f"""
    You are an AI wellness assistant analyzing emotional health. 
    Consider the user's context: {user_context}
    
    Analyze this transcript for emotional patterns:
    {transcript}
    
    Focus on:
    1. Primary emotional state
    2. Emotional stability
    3. Changes from previous patterns
    4. Concerning emotional indicators
    
    Provide a structured analysis.
    """

def create_memory_analysis_prompt(transcript, user_context=""):
    """Creates a personalized prompt for memory analysis."""
    return f"""
    You are an AI cognitive health assistant analyzing memory and cognitive patterns.
    Consider the user's context: {user_context}
    
    Analyze this transcript for cognitive indicators:
    {transcript}
    
    Focus on:
    1. Vocabulary richness and diversity
    2. Sentence structure and fluency
    3. Repetition patterns
    4. Memory-related language
    5. Cognitive decline indicators
    
    Provide a structured analysis.
    """

def create_alert_evaluation_prompt(analysis_data, user_context=""):
    """Creates a personalized prompt for alert evaluation."""
    return f"""
    You are an AI caregiver alert system evaluating wellness indicators.
    Consider the user's context: {user_context}
    
    Current analysis data: {analysis_data}
    
    Evaluate if caregiver intervention is needed based on:
    1. Sustained low wellness scores
    2. Emotional distress patterns
    3. Cognitive decline indicators
    4. Social isolation signs
    
    Provide a clear recommendation with urgency level.
    """
