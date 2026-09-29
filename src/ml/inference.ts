const STOP_WORDS = new Set([
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
]);

function stemWord(word: string): string {
  // Simple suffix-stripping lemmatization fallback (matches the Python preprocess.py fallback)
  if (word.length > 4) {
    if (word.endsWith('ies')) {
      return word.slice(0, -3) + 'y';
    }
    if (word.endsWith('s') && !word.endsWith('ss') && !word.endsWith('us') && !word.endsWith('is')) {
      return word.slice(0, -1);
    }
  }
  return word;
}

export function preprocessText(text: string): string[] {
  if (!text) return [];
  
  // 1. Lowercase conversion
  let cleaned = text.toLowerCase();
  
  // 2. Remove numbers
  cleaned = cleaned.replace(/\b\d+\b/g, ' ');
  
  // 3. Remove punctuation (replace with spaces to keep word boundaries)
  cleaned = cleaned.replace(/[^\w\s]/g, ' ');
  
  // 4. Tokenization (split by whitespace)
  const tokens = cleaned.split(/\s+/).filter(token => token.length > 0);
  
  // 5. Remove stop words
  const filtered = tokens.filter(token => !STOP_WORDS.has(token));
  
  // 6. Lemmatization
  const stemmed = filtered.map(stemWord);
  
  return stemmed;
}
