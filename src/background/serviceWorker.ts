import { ExtensionMessage } from '../shared/messageTypes';
import { ScanResult } from '../shared/types';
import { STORAGE_KEYS } from '../shared/constants';

console.log('TrustLens Background Service Worker initialized.');

// In-memory cache for recent notification dispatches to prevent spamming
const notifiedDomains = new Set<string>();

// 1. Message passing listener
chrome.runtime.onMessage.addListener((message: ExtensionMessage, _sender, sendResponse) => {
  if (message.type === 'SCAN_RESULTS' && 'data' in message) {
    const data = message.data as ScanResult;
    console.log('TrustLens service worker received scan results:', data);
    
    chrome.storage.local.set({ [STORAGE_KEYS.LATEST_SCAN]: data })
      .then(() => {
        sendResponse({ success: true });
      })
      .catch((error) => {
        console.error('Error saving to storage:', error);
        sendResponse({ success: false, error: 'Storage error' });
      });
      
    return true; // Keep channel open for async response
  }
});

// 2. Automatic Background Scanning Tab listener
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  // Only trigger when page load completes
  if (changeInfo.status !== 'complete' || !tab.url) return;

  const url = tab.url;
  // Ignore system, extension, or empty tabs
  if (
    url.startsWith('chrome://') || 
    url.startsWith('chrome-extension://') || 
    url.startsWith('https://chrome.google.com/webstore') ||
    url.startsWith('about:')
  ) {
    return;
  }

  // Retrieve user preferences
  chrome.storage.local.get(['trustlens_settings', 'trustlens_user_id'], async (store) => {
    const settings = store.trustlens_settings || {};
    const autoScan = settings.autoScanEnabled ?? false; // Default: false to respect privacy
    const mode = settings.mode || 'local';
    const backendUrl = settings.backendUrl || 'http://localhost:8000';
    const activeModel = settings.activeModel || 'logistic_regression';
    const userId = store.trustlens_user_id || '';

    if (!autoScan) return;

    try {
      // 1. Extract domain to prevent double alerts
      const domain = new URL(url).hostname;
      if (notifiedDomains.has(domain)) {
        console.log(`Notification already sent for ${domain}. Skipping background alert.`);
        return;
      }

      // 2. Attempt to message content script to extract DOM content
      let response;
      try {
        response = await chrome.tabs.sendMessage(tabId, { type: 'SCAN_PAGE' });
      } catch (err) {
        console.warn('Direct messaging failed, attempting injection...', err);
        // Inject content script if not active
        await chrome.scripting.executeScript({
          target: { tabId },
          files: ['content.js']
        });
        response = await chrome.tabs.sendMessage(tabId, { type: 'SCAN_PAGE' });
      }

      if (!response || !response.success) return;

      const localResult = response.data as ScanResult;
      const extractedData = response.extractedData;
      let finalResult = localResult;

      // 3. Make cloud call if cloud/hybrid mode is active
      if ((mode === 'cloud' || mode === 'hybrid') && extractedData) {
        try {
          const apiRes = await fetch(`${backendUrl}/api/scan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              pageText: extractedData.visibleText,
              url: extractedData.url,
              title: extractedData.title,
              userId: userId,
              activeModel: activeModel
            })
          });

          if (apiRes.ok) {
            const cloudData = await apiRes.json();
            finalResult = {
              title: cloudData.title,
              url: cloudData.url,
              wordCount: extractedData.wordCount,
              headingCount: extractedData.headingCount,
              buttonCount: extractedData.buttonCount,
              linkCount: extractedData.linkCount,
              score: cloudData.score,
              label: cloudData.label,
              matchedKeywords: cloudData.matchedKeywords,
              reasons: cloudData.reasons,
              timestamp: cloudData.timestamp,
              ruleScore: cloudData.ruleScore,
              mlScore: cloudData.mlScore,
              mlPrediction: cloudData.mlPrediction,
              mlConfidence: cloudData.mlConfidence,
              scanId: cloudData.scanId,
              isPrivacyPolicy: cloudData.isPrivacyPolicy,
              privacySummary: cloudData.privacySummary,
              reputation: cloudData.reputation,
              trustScore: cloudData.trustScore
            };
          }
        } catch (apiErr) {
          console.warn('Background Cloud scan failed, fallback to Local:', apiErr);
        }
      }

      // 4. Alert user via Chrome Notification if Risk label is Caution or Risky
      if (finalResult.label === 'Caution' || finalResult.label === 'Risky') {
        notifiedDomains.add(domain);
        
        // Clear domain from notification memory after 10 minutes to allow re-scans later
        setTimeout(() => notifiedDomains.delete(domain), 10 * 60 * 1000);

        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'public/icon128.png',
          title: `TrustLens Security Alert`,
          message: `Deceptive UI or scam patterns detected on ${domain}.\nRisk level: ${finalResult.label} (Score: ${finalResult.score}/100)`,
          priority: 2
        });
      }
    } catch (scanErr) {
      console.error('Background autocheck error:', scanErr);
    }
  });
});
