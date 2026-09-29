import modelParameters from './model_parameters.json';

interface ModelParameters {
  model_type: string;
  classes: string[];
  vocabulary: Record<string, number>;
  idf: number[];
  coefficients: number[][];
  intercepts: number[];
}

const params = modelParameters as ModelParameters;

export function predictProba(tokens: string[]): Record<string, number> {
  const vocab = params.vocabulary;
  const idf = params.idf;
  const coefs = params.coefficients;
  const intercepts = params.intercepts;
  const classes = params.classes;
  const numFeatures = idf.length;

  // Generate n-grams (unigrams and bigrams) from tokens to match tfidf ngram_range (1, 2)
  const ngrams: string[] = [];
  // Unigrams
  for (let i = 0; i < tokens.length; i++) {
    ngrams.push(tokens[i]);
  }
  // Bigrams
  for (let i = 0; i < tokens.length - 1; i++) {
    ngrams.push(tokens[i] + ' ' + tokens[i + 1]);
  }

  // Count term frequencies
  const counts: Record<string, number> = {};
  for (const ngram of ngrams) {
    counts[ngram] = (counts[ngram] || 0) + 1;
  }

  // Compute raw TF-IDF vector
  const tfidfVec = new Array(numFeatures).fill(0);
  for (const [term, idx] of Object.entries(vocab)) {
    const count = counts[term] || 0;
    if (count > 0) {
      tfidfVec[idx] = count * idf[idx];
    }
  }

  // Apply L2 normalization
  let l2Norm = 0;
  for (let i = 0; i < numFeatures; i++) {
    l2Norm += tfidfVec[i] * tfidfVec[i];
  }
  l2Norm = Math.sqrt(l2Norm);

  if (l2Norm > 0) {
    for (let i = 0; i < numFeatures; i++) {
      tfidfVec[i] = tfidfVec[i] / l2Norm;
    }
  }

  // Run Logistic Regression z = intercept + sum(coef_i * tfidf_i)
  const numClasses = classes.length;
  const z: number[] = new Array(numClasses).fill(0);

  for (let k = 0; k < numClasses; k++) {
    z[k] = intercepts[k];
    const classCoefs = coefs[k];
    for (let i = 0; i < numFeatures; i++) {
      z[k] += classCoefs[i] * tfidfVec[i];
    }
  }

  // Softmax
  const maxZ = Math.max(...z);
  const expZ = z.map(val => Math.exp(val - maxZ));
  const sumExpZ = expZ.reduce((sum, val) => sum + val, 0);
  const probs = expZ.map(val => (sumExpZ > 0 ? val / sumExpZ : 0));

  // Map to class labels
  const result: Record<string, number> = {};
  for (let k = 0; k < numClasses; k++) {
    result[classes[k]] = probs[k];
  }
  return result;
}
