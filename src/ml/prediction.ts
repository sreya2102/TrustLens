import { predictProba } from './model';
import { preprocessText } from './inference';
import { RiskLabel } from '../shared/types';

export interface PredictionResult {
  prediction: RiskLabel;
  confidence: number;
  probabilities: Record<string, number>;
}

export function predictWebpageText(visibleText: string): PredictionResult {
  const tokens = preprocessText(visibleText);
  const probs = predictProba(tokens);

  // Find class with maximum probability
  let maxClass: RiskLabel = 'Safe';
  let maxProb = 0;

  for (const [cls, prob] of Object.entries(probs)) {
    if (prob > maxProb) {
      maxProb = prob;
      maxClass = cls as RiskLabel;
    }
  }

  return {
    prediction: maxClass,
    confidence: maxProb,
    probabilities: probs
  };
}
