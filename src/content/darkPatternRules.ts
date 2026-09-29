import { Rule } from '../shared/types';

export const RULES: Rule[] = [
  {
    category: 'URGENCY',
    displayName: 'Urgency language',
    weight: 10,
    color: '#fef08a', // Tailwind yellow-200 (translucent on highlight)
    reasonTemplate: 'Urgency language detected',
    keywords: [
      'hurry',
      'limited time',
      'offer ends soon',
      'only today',
      'last chance',
      'act now',
      'sale ends',
      'only few left',
      'expires soon',
      'ends soon',
      'dont miss out',
      'don\'t miss out',
      'flash sale',
      'hurry up',
      'limited time only',
      'last minute',
      'last-minute',
      'one day only',
      'final hours',
      'tick tock',
      'tick-tock',
      'seconds left',
      'running out'
    ]
  },
  {
    category: 'SCARCITY',
    displayName: 'Scarcity language',
    weight: 15,
    color: '#fed7aa', // Tailwind orange-200
    reasonTemplate: 'Scarcity language detected',
    keywords: [
      'only 1 left',
      'only 2 left',
      'only 3 left',
      'only 4 left',
      'only 5 left',
      'few remaining',
      'almost sold out',
      'limited stock',
      'low stock',
      'selling fast',
      'high demand',
      'demand is high',
      'last items',
      'backorder soon',
      'almost gone',
      'limited quantity',
      'while supplies last'
    ]
  },
  {
    category: 'SUBSCRIPTION_TRAP',
    displayName: 'Subscription traps',
    weight: 25,
    color: '#fca5a5', // Tailwind red-300
    reasonTemplate: 'Subscription wording detected',
    keywords: [
      'free trial',
      'auto renewal',
      'auto-renewal',
      'recurring billing',
      'subscription',
      'cancel anytime',
      'cancel any time',
      'renew automatically',
      'renews automatically',
      'billed monthly',
      'billed annually',
      'membership fee',
      'continuous billing',
      'auto-renew',
      'trial period',
      'after the trial',
      'continuous service',
      'billed weekly'
    ]
  },
  {
    category: 'PRIVACY_RISK',
    displayName: 'Privacy risks',
    weight: 20,
    color: '#fdba74', // Tailwind orange-300
    reasonTemplate: 'Third-party sharing mentioned',
    keywords: [
      'share your data',
      'share your personal details',
      'third-party partners',
      'third party partners',
      'personalized ads',
      'marketing partners',
      'consent required',
      'sell data',
      'sell your data',
      'track location',
      'access contacts',
      'device information',
      'allow cookies',
      'ad profiling',
      'data collection',
      'share with partners',
      'third-party advertising',
      'targeted ads',
      'advertising networks'
    ]
  },
  {
    category: 'FINANCIAL_MANIPULATION',
    displayName: 'Financial manipulation',
    weight: 30,
    color: '#fca5a5', // Tailwind red-300
    reasonTemplate: 'Financial pressure language detected',
    keywords: [
      'instant approval',
      'guaranteed loan',
      'win cash',
      'congratulations',
      'claim reward',
      'earn money',
      'no risk',
      'risk free',
      'risk-free',
      'guaranteed returns',
      'get rich',
      'double your income',
      'financial freedom',
      'cash prize',
      'jackpot',
      'free gift',
      'claim now',
      'make money fast',
      'unlimited cash',
      'easy money',
      'no obligation'
    ]
  }
];
