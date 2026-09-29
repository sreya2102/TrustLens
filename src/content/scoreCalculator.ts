import { KeywordMatch, RiskLabel } from '../shared/types';

export function calculateScore(matches: KeywordMatch[]): {
  score: number;
  label: RiskLabel;
  reasons: string[];
} {
  // Calculate total score based on weight * count of matches
  let score = 0;
  for (const match of matches) {
    score += match.count * match.weight;
  }

  // Clamp score to 100 max
  score = Math.min(score, 100);

  // Assign label based on thresholds
  // 0-20: Safe, 21-50: Caution, Above 50: Risky
  let label: RiskLabel = 'Safe';
  if (score > 50) {
    label = 'Risky';
  } else if (score > 20) {
    label = 'Caution';
  }

  // Generate reasons depending on which categories were matched
  const matchedCategories = new Set<string>();
  for (const match of matches) {
    if (match.count > 0) {
      matchedCategories.add(match.category);
    }
  }

  const reasons: string[] = [];
  if (matchedCategories.has('URGENCY')) {
    reasons.push('⚠ Urgency language detected');
  }
  if (matchedCategories.has('SCARCITY')) {
    reasons.push('⚠ Scarcity language detected');
  }
  if (matchedCategories.has('PRIVACY_RISK')) {
    reasons.push('⚠ Third-party sharing mentioned');
  }
  if (matchedCategories.has('SUBSCRIPTION_TRAP')) {
    reasons.push('⚠ Subscription wording detected');
  }
  if (matchedCategories.has('FINANCIAL_MANIPULATION')) {
    reasons.push('⚠ Financial pressure language detected');
  }

  return {
    score,
    label,
    reasons
  };
}
