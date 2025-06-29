import spacy
from collections import Counter
import re
from typing import Dict, List, Any

# Load the SpaCy model
# Ensure you have run: python -m spacy download en_core_web_md
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    print("Spacy model 'en_core_web_md' not found. Please run 'python -m spacy download en_core_web_md'")
    nlp = None

def analyze_cognitive_metrics(text: str) -> Dict[str, Any]:
    """
    Analyzes a text to extract a wide range of cognitive and linguistic indicators.
    
    Args:
        text: The user's transcript.
    
    Returns:
        A dictionary containing up to 10 cognitive metrics.
    """
    if not nlp or not text.strip():
        return {
            "error": "NLP model not loaded or text is empty.",
            "word_count": 0,
            "unique_word_count": 0,
            "lexical_diversity": 0,
            "sentence_count": 0,
            "avg_sentence_length": 0,
            "noun_ratio": 0,
            "verb_ratio": 0,
            "adj_ratio": 0,
            "named_entity_count": 0,
            "coherence_score": 0,
        }

    doc = nlp(text)
    
    words = [token.text.lower() for token in doc if token.is_alpha]
    sentences = list(doc.sents)
    
    # 1. Word Count
    word_count = len(words)
    
    # 2. Unique Word Count
    unique_word_count = len(set(words))
    
    # 3. Lexical Diversity (Type-Token Ratio)
    lexical_diversity = unique_word_count / word_count if word_count > 0 else 0
    
    # 4. Sentence Count
    sentence_count = len(sentences)
    
    # 5. Average Sentence Length
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
    
    # Part-of-Speech Ratios
    pos_counts = Counter(token.pos_ for token in doc)
    total_pos = sum(pos_counts.values())
    
    # 6. Noun Ratio
    noun_ratio = pos_counts.get("NOUN", 0) / total_pos if total_pos > 0 else 0
    
    # 7. Verb Ratio
    verb_ratio = pos_counts.get("VERB", 0) / total_pos if total_pos > 0 else 0
    
    # 8. Adjective Ratio
    adj_ratio = pos_counts.get("ADJ", 0) / total_pos if total_pos > 0 else 0
    
    # 9. Named Entity Count (people, places, organizations)
    named_entity_count = len(doc.ents)
    
    # 10. Coherence Score (simple measure: average similarity between adjacent sentences)
    coherence_score = 0
    if sentence_count > 1:
        similarities = []
        for i in range(len(sentences) - 1):
            s1 = sentences[i]
            s2 = sentences[i+1]
            # Ensure vectors are available
            if s1.has_vector and s2.has_vector and s1.vector_norm and s2.vector_norm:
                similarities.append(s1.similarity(s2))
        coherence_score = sum(similarities) / len(similarities) if similarities else 0

    return {
        "word_count": word_count,
        "unique_word_count": unique_word_count,
        "lexical_diversity": round(lexical_diversity, 3),
        "sentence_count": sentence_count,
        "avg_sentence_length": round(avg_sentence_length, 2),
        "noun_ratio": round(noun_ratio, 3),
        "verb_ratio": round(verb_ratio, 3),
        "adj_ratio": round(adj_ratio, 3),
        "named_entity_count": named_entity_count,
        "coherence_score": round(coherence_score, 3),
    }

def has_positive_sentiment(text: str) -> bool:
    """
    A simple check for positive sentiment to guide conversation.
    This is a placeholder and can be replaced with a more sophisticated model.
    """
    positive_words = ["good", "great", "wonderful", "happy", "lovely", "beautiful", "excellent", "nice"]
    return any(word in text.lower() for word in positive_words)

def has_negative_sentiment(text: str) -> bool:
    """
    A simple check for negative sentiment to guide conversation away from sensitive topics.
    """
    negative_words = ["sad", "lonely", "bad", "terrible", "horrible", "confused", "worried", "anxious", "frustrated"]
    return any(word in text.lower() for word in negative_words) 