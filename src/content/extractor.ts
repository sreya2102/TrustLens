import { ExtractedData } from '../shared/messageTypes';

export function extractPageData(): ExtractedData {
  const title = document.title || 'Untitled Page';
  const url = window.location.href || 'Unknown URL';
  
  // Safely extract visible text to handle empty pages or direct media views
  const visibleText = document.body ? document.body.innerText : '';
  const cleanText = visibleText.trim();
  const wordCount = cleanText ? cleanText.split(/\s+/).length : 0;
  
  const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
  const buttons = document.querySelectorAll('button, input[type="button"], input[type="submit"]');
  const links = document.querySelectorAll('a');

  return {
    title,
    url,
    wordCount,
    headingCount: headings.length,
    buttonCount: buttons.length,
    linkCount: links.length,
    visibleText
  };
}
