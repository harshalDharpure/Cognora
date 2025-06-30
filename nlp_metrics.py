import re
from collections import Counter
from typing import Dict, List, Any
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag

# Download required NLTK data (will be cached)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

def analyze_cognitive_metrics(text: str) -> Dict[str, Any]:
    """
    Analyzes a text to extract cognitive and linguistic indicators using lightweight NLTK.
    
    Args:
        text: The user's transcript.
    
    Returns:
        A dictionary containing cognitive metrics.
    """
    if not text.strip():
        return {
            "error": "Text is empty.",
            "word_count": 0,
            "unique_word_count": 0,
            "lexical_diversity": 0,
            "sentence_count": 0,
            "avg_sentence_length": 0,
            "noun_ratio": 0,
            "verb_ratio": 0,
            "adj_ratio": 0,
            "named_entity_count": 0,
            "coherence_score": 0.5,  # Default neutral score
        }

    try:
        # Tokenize text
        sentences = sent_tokenize(text)
        words = word_tokenize(text.lower())
        
        # Filter out punctuation and get only alphabetic words
        words = [word for word in words if word.isalpha()]
        
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
        
        # Part-of-Speech Analysis
        if words:
            pos_tags = pos_tag(words)
            pos_counts = Counter(tag for word, tag in pos_tags)
            total_pos = sum(pos_counts.values())
            
            # 6. Noun Ratio (NN, NNS, NNP, NNPS)
            noun_tags = ['NN', 'NNS', 'NNP', 'NNPS']
            noun_count = sum(pos_counts.get(tag, 0) for tag in noun_tags)
            noun_ratio = noun_count / total_pos if total_pos > 0 else 0
            
            # 7. Verb Ratio (VB, VBD, VBG, VBN, VBP, VBZ)
            verb_tags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
            verb_count = sum(pos_counts.get(tag, 0) for tag in verb_tags)
            verb_ratio = verb_count / total_pos if total_pos > 0 else 0
            
            # 8. Adjective Ratio (JJ, JJR, JJS)
            adj_tags = ['JJ', 'JJR', 'JJS']
            adj_count = sum(pos_counts.get(tag, 0) for tag in adj_tags)
            adj_ratio = adj_count / total_pos if total_pos > 0 else 0
        else:
            noun_ratio = verb_ratio = adj_ratio = 0
        
        # 9. Named Entity Count (simplified - count capitalized words)
        named_entities = re.findall(r'\b[A-Z][a-z]+\b', text)
        named_entity_count = len(set(named_entities))
        
        # 10. Coherence Score (simplified - based on sentence length consistency)
        if sentence_count > 1:
            sentence_lengths = [len(word_tokenize(s)) for s in sentences]
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            variance = sum((l - avg_length) ** 2 for l in sentence_lengths) / len(sentence_lengths)
            # Normalize variance to 0-1 scale (lower variance = higher coherence)
            coherence_score = max(0, 1 - (variance / (avg_length ** 2)))
        else:
            coherence_score = 0.5

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
        
    except Exception as e:
        print(f"Error in NLP analysis: {e}")
        return {
            "error": f"Analysis failed: {str(e)}",
            "word_count": len(text.split()),
            "unique_word_count": len(set(text.split())),
            "lexical_diversity": 0.5,
            "sentence_count": len(text.split('.')),
            "avg_sentence_length": 10,
            "noun_ratio": 0.3,
            "verb_ratio": 0.2,
            "adj_ratio": 0.1,
            "named_entity_count": 0,
            "coherence_score": 0.5,
        }

def has_positive_sentiment(text: str) -> bool:
    """
    A simple check for positive sentiment to guide conversation.
    """
    positive_words = ["good", "great", "wonderful", "happy", "lovely", "beautiful", "excellent", "nice", "amazing", "fantastic"]
    return any(word in text.lower() for word in positive_words)

def has_negative_sentiment(text: str) -> bool:
    """
    A simple check for negative sentiment to guide conversation away from sensitive topics.
    """
    negative_words = ["sad", "lonely", "bad", "terrible", "horrible", "confused", "worried", "anxious", "frustrated", "angry", "depressed"]
    return any(word in text.lower() for word in negative_words) 