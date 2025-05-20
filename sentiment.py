from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
   
    def analyze(self, text: str) -> float:
        text = text.lower().strip()
        
        # Custom word adjustments for game context
        custom_words = {
            'exodyne': -1.5,  # Gang name has negative connotation
            'stray': -0.5,    # Neutral-negative for non-gang members
            'target': -1.0,   # Suspicious word
            'rumor': -0.7     # Generally negative
        }
        
        # Temporarily add custom words
        for word, score in custom_words.items():
            self.analyzer.lexicon[word] = score
            
        vs = self.analyzer.polarity_scores(text)
        
        # Remove custom words after analysis
        for word in custom_words:
            if word in self.analyzer.lexicon:
                del self.analyzer.lexicon[word]
                
        return vs['compound']