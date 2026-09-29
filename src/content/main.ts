import { extractPageData } from './extractor';
import { ExtensionMessage } from '../shared/messageTypes';
import { analyzeText } from './riskAnalyzer';
import { highlightSuspiciousPhrases } from './highlighter';

console.log('TrustLens content script loaded');

chrome.runtime.onMessage.addListener((message: ExtensionMessage, _sender, sendResponse) => {
  if (message.type === 'SCAN_PAGE') {
    try {
      const extracted = extractPageData();
      
      // Perform rule-based lexical risk analysis
      const result = analyzeText(
        extracted.visibleText,
        extracted.title,
        extracted.url,
        {
          wordCount: extracted.wordCount,
          headingCount: extracted.headingCount,
          buttonCount: extracted.buttonCount,
          linkCount: extracted.linkCount
        }
      );
      
      // Apply webpage highlighting in-place
      highlightSuspiciousPhrases();

      // Return the complete analysis details and raw extracted data to popup
      sendResponse({ success: true, data: result, extractedData: extracted });
    } catch (error) {
      console.error('TrustLens content script scan failed:', error);
      sendResponse({ 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown scanning failure' 
      });
    }
  }
  return true; // Keep message channel open for response
});
