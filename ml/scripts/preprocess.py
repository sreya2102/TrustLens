import re
import string

# We will try to import NLTK. If it fails, we will print a warning and use our robust fallback preprocessor.
# This ensures that the training pipeline is extremely resilient.
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    
    # Download required NLTK resources automatically
    for resource in ['punkt', 'stopwords', 'wordnet', 'omw-1.4']:
        try:
            nltk.data.find(f'tokenizers/{resource}' if resource == 'punkt' else f'corpora/{resource}')
        except LookupError:
            nltk.download(resource, quiet=True)
            
    _HAS_NLTK = True
except ImportError:
    _HAS_NLTK = False

# Hardcoded fallback stop words to ensure preprocessing works even without NLTK installed
FALLBACK_STOP_WORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd",
    'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers',
    'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
    'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
    'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
    'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should',
    "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't",
    'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't",
    'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't",
    'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
}

def fallback_lemmatize(word):
    """
    Very simple suffix-stripping lemmatization fallback.
    Identical to the TypeScript version to ensure parity in behavior.
    """
    if len(word) > 4:
        if word.endswith('ies'):
            return word[:-3] + 'y'
        if word.endswith('s') and not word.endswith('ss') and not word.endswith('us') and not word.endswith('is'):
            return word[:-1]
    return word

def preprocess_text(text):
    """
    Preprocess raw webpage text:
    1. Lowercase conversion
    2. Remove numbers
    3. Remove punctuation
    4. Tokenization
    5. Remove stop words
    6. Lemmatization
    """
    if not isinstance(text, str):
        return ""
    
    # 1. Lowercase conversion
    text = text.lower()
    
    # 2. Remove numbers
    text = re.sub(r'\b\d+\b', ' ', text)
    
    # 3. Remove punctuation (replace with spaces to maintain word boundaries)
    text = text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
    
    # 4. Tokenization
    if _HAS_NLTK:
        try:
            tokens = word_tokenize(text)
        except Exception:
            tokens = text.split()
    else:
        tokens = text.split()
        
    # 5. Remove stop words
    if _HAS_NLTK:
        try:
            stop_words = set(stopwords.words('english'))
        except Exception:
            stop_words = FALLBACK_STOP_WORDS
    else:
        stop_words = FALLBACK_STOP_WORDS
        
    filtered_tokens = [t for t in tokens if t not in stop_words]
    
    # 6. Lemmatization
    if _HAS_NLTK:
        try:
            lemmatizer = WordNetLemmatizer()
            # Standardize nouns and verbs
            lemmatized_tokens = []
            for t in filtered_tokens:
                # First lemmatize as verb, then noun
                lemma = lemmatizer.lemmatize(t, pos='v')
                lemma = lemmatizer.lemmatize(lemma, pos='n')
                lemmatized_tokens.append(lemma)
        except Exception:
            lemmatized_tokens = [fallback_lemmatize(t) for t in filtered_tokens]
    else:
        lemmatized_tokens = [fallback_lemmatize(t) for t in filtered_tokens]
        
    return " ".join(lemmatized_tokens)

if __name__ == '__main__':
    sample_text = "Hurry up! Flash sales end in 5 minutes! Only 2 items left. We renewal subscriptions automatically after 14 days."
    print("Original Text:", sample_text)
    print("Cleaned Text :", preprocess_text(sample_text))
