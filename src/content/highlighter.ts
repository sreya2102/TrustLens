import { RULES } from './darkPatternRules';

function escapeRegExp(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Removes all TrustLens highlight spans and merges the text back.
 */
export function clearHighlights(): void {
  const highlights = document.querySelectorAll('span.trustlens-highlight');
  highlights.forEach((span) => {
    const parent = span.parentNode;
    if (parent) {
      const textNode = document.createTextNode(span.textContent || '');
      parent.replaceChild(textNode, span);
      parent.normalize(); // Merges adjacent text nodes
    }
  });
}

/**
 * Traverses the DOM to wrap matched keywords in styled span elements.
 */
export function highlightSuspiciousPhrases(): void {
  // First clear any existing highlights
  clearHighlights();

  const keywordMap = new Map<string, { color: string; category: string }>();
  const keywords: string[] = [];

  for (const rule of RULES) {
    for (const keyword of rule.keywords) {
      keywordMap.set(keyword.toLowerCase(), { color: rule.color, category: rule.category });
      keywords.push(keyword);
    }
  }

  // Sort descending by length to match longer phrases before their sub-phrases
  keywords.sort((a, b) => b.length - a.length);

  if (keywords.length === 0) return;

  const escapedKeywords = keywords.map((k) => {
    const esc = escapeRegExp(k);
    let pattern = esc;
    if (/^\w/.test(k)) pattern = '\\b' + pattern;
    if (/\w$/.test(k)) pattern = pattern + '\\b';
    return pattern;
  });

  const regex = new RegExp(`(${escapedKeywords.join('|')})`, 'gi');

  const walk = (node: Node) => {
    if (node.nodeType === Node.TEXT_NODE) {
      const textNode = node as Text;
      const text = textNode.nodeValue || '';

      if (!text.trim()) return;

      regex.lastIndex = 0;
      if (regex.test(text)) {
        regex.lastIndex = 0;
        const fragment = document.createDocumentFragment();
        let lastIdx = 0;
        let match: RegExpExecArray | null;

        while ((match = regex.exec(text)) !== null) {
          const matchIdx = match.index;
          const matchText = match[0];

          // Text segment before the match
          if (matchIdx > lastIdx) {
            fragment.appendChild(document.createTextNode(text.substring(lastIdx, matchIdx)));
          }

          // Create the highlight span
          const span = document.createElement('span');
          const meta = keywordMap.get(matchText.toLowerCase());
          const bgColor = meta ? meta.color : '#fef08a';

          span.className = 'trustlens-highlight';
          span.style.backgroundColor = bgColor;
          span.style.color = '#1e293b'; // Tailwind slate-800 for high-contrast text readability
          span.style.fontWeight = '600';
          span.style.borderRadius = '4px';
          span.style.padding = '0.5px 3.5px';
          span.style.margin = '0 1px';
          span.style.display = 'inline';
          span.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.15)';
          span.title = `TrustLens: ${meta?.category.replace('_', ' ') || 'Warning'}`;

          span.textContent = matchText;
          fragment.appendChild(span);

          lastIdx = regex.lastIndex;
        }

        if (lastIdx < text.length) {
          fragment.appendChild(document.createTextNode(text.substring(lastIdx)));
        }

        textNode.parentNode?.replaceChild(fragment, textNode);
      }
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      const el = node as Element;
      const tag = el.tagName.toUpperCase();

      // Avoid editing script, style, form input elements, SVG and already processed highlights
      if (
        tag !== 'SCRIPT' &&
        tag !== 'STYLE' &&
        tag !== 'NOSCRIPT' &&
        tag !== 'TEXTAREA' &&
        tag !== 'INPUT' &&
        tag !== 'IFRAME' &&
        tag !== 'SVG' &&
        !el.classList.contains('trustlens-highlight')
      ) {
        const children = Array.from(el.childNodes);
        for (const child of children) {
          walk(child);
        }
      }
    }
  };

  walk(document.body);
}
