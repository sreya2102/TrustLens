export interface ExtractedData {
  title: string;
  url: string;
  wordCount: number;
  headingCount: number;
  buttonCount: number;
  linkCount: number;
  visibleText: string;
}

export type RiskLabel = 'Safe' | 'Caution' | 'Risky';

export type RuleCategory =
  | 'URGENCY'
  | 'SCARCITY'
  | 'SUBSCRIPTION_TRAP'
  | 'PRIVACY_RISK'
  | 'FINANCIAL_MANIPULATION';

export interface KeywordMatch {
  keyword: string;
  category: RuleCategory;
  count: number;
  weight: number;
  color: string;
}

export interface ScanResult {
  title: string;
  url: string;
  wordCount: number;
  headingCount: number;
  buttonCount: number;
  linkCount: number;
  score: number;
  label: RiskLabel;
  matchedKeywords: KeywordMatch[];
  reasons: string[];
  timestamp: string;
  ruleScore?: number;
  mlScore?: number;
  mlPrediction?: RiskLabel;
  mlConfidence?: number;
  scanId?: number;
  modelName?: string;
  modelVersion?: string;
  modelAccuracy?: number;
  modelLatency?: number;
  modelMemory?: number;
  humanExplanation?: string;
  influentialWords?: string[];
  isPrivacyPolicy?: boolean;
  privacySummary?: Record<string, string> | null;
  reputation?: {
    domain: string;
    isHttps: boolean;
    isBlacklisted: boolean;
    domainAge: string;
    reputationScore: number;
    verdict: string;
  };
  trustScore?: number;
}

export interface Rule {
  category: RuleCategory;
  displayName: string;
  keywords: string[];
  weight: number;
  color: string;
  reasonTemplate: string;
}
