import { RULES } from './darkPatternRules';
import { calculateScore } from './scoreCalculator';
import { KeywordMatch, ScanResult, RiskLabel } from '../shared/types';
import { predictWebpageText } from '../ml/prediction';

function escapeRegExp(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

export function analyzeText(
  visibleText: string,
  title: string,
  url: string,
  stats: {
    wordCount: number;
    headingCount: number;
    buttonCount: number;
    linkCount: number;
  }
): ScanResult {
  const matchedKeywords: KeywordMatch[] = [];

  // Standardize text whitespace for reliable matching
  const normalizedText = visibleText.replace(/\s+/g, ' ');

  for (const rule of RULES) {
    for (const keyword of rule.keywords) {
      const escapedKeyword = escapeRegExp(keyword);
      
      // Use boundary detection only if the keyword begins/ends with alphanumeric characters
      let regexStr = escapedKeyword;
      if (/^\w/.test(keyword)) {
        regexStr = '\\b' + regexStr;
      }
      if (/\w$/.test(keyword)) {
        regexStr = regexStr + '\\b';
      }

      const regex = new RegExp(regexStr, 'gi');
      const matches = normalizedText.match(regex);
      const count = matches ? matches.length : 0;

      if (count > 0) {
        matchedKeywords.push({
          keyword,
          category: rule.category,
          count,
          weight: rule.weight,
          color: rule.color
        });
      }
    }
  }

  // Compute final scores and label
  const { score: ruleScore, reasons: ruleReasons } = calculateScore(matchedKeywords);

  // Perform ML-based classification
  const mlResult = predictWebpageText(visibleText);
  const mlPrediction = mlResult.prediction;
  const mlConfidence = mlResult.confidence;

  // Calculate ML Score continuously based on probabilities:
  // ML Score = P(Caution) * 50 + P(Risky) * 100
  const probs = mlResult.probabilities;
  const mlScore = Math.round((probs['Caution'] || 0) * 50 + (probs['Risky'] || 0) * 100);

  // Combine scores: 60% rule engine + 40% ML prediction
  const score = Math.round(0.6 * ruleScore + 0.4 * mlScore);

  // Assign label based on thresholds
  // 0-20: Safe, 21-50: Caution, Above 50: Risky
  let label: RiskLabel = 'Safe';
  if (score > 50) {
    label = 'Risky';
  } else if (score > 20) {
    label = 'Caution';
  }

  // Combine reasons and add ML-specific explainability
  const reasons = [...ruleReasons];
  if (mlPrediction !== 'Safe') {
    const pct = Math.round(mlConfidence * 100);
    reasons.push(`🤖 ML Model predicted ${mlPrediction} (${pct}% confidence)`);
  }

  return {
    title,
    url,
    wordCount: stats.wordCount,
    headingCount: stats.headingCount,
    buttonCount: stats.buttonCount,
    linkCount: stats.linkCount,
    score,
    label,
    matchedKeywords,
    reasons,
    timestamp: new Date().toLocaleString(),
    ruleScore,
    mlScore,
    mlPrediction,
    mlConfidence
  };
}
