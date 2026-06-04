import { Context } from '@netlify/edge-functions';
import TurndownService from 'https://esm.sh/turndown@7.1.3';

export default async (request: Request, context: Context) => {
  const accept = request.headers.get('accept') || '';

  // Only run if the request explicitly asks for text/markdown
  if (!accept.includes('text/markdown')) {
    return;
  }

  // Get the HTML response from the CDN origin
  const response = await context.next();
  if (!response.ok) {
    return response;
  }

  const contentType = response.headers.get('content-type') || '';
  if (!contentType.includes('text/html')) {
    return response;
  }

  let html = await response.text();

  // Strip unnecessary elements (scripts, styles, head, header, footer, nav)
  html = html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
  html = html.replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, '');
  html = html.replace(/<head\b[^<]*(?:(?!<\/head>)<[^<]*)*<\/head>/gi, '');
  html = html.replace(/<header\b[^<]*(?:(?!<\/header>)<[^<]*)*<\/header>/gi, '');
  html = html.replace(/<footer\b[^<]*(?:(?!<\/footer>)<[^<]*)*<\/footer>/gi, '');
  html = html.replace(/<nav\b[^<]*(?:(?!<\/nav>)<[^<]*)*<\/nav>/gi, '');

  // Convert to Markdown using Turndown
  const turndownService = new TurndownService({
    headingStyle: 'atx',
    codeBlockStyle: 'fenced',
    hr: '---',
  });

  // Keep links and images formatted cleanly
  turndownService.addRule('stripEmptyLinks', {
    filter: (node) => node.nodeName === 'A' && !node.textContent.trim() && !node.getAttribute('href'),
    replacement: () => '',
  });

  const markdown = turndownService.turndown(html);

  // Return Markdown response with correct content-type and headers
  return new Response(markdown, {
    status: response.status,
    statusText: response.statusText,
    headers: {
      'Content-Type': 'text/markdown; charset=utf-8',
      'X-Markdown-Tokens': Math.round(markdown.length / 4).toString(),
      'Access-Control-Allow-Origin': '*',
      'Cache-Control': 'public, max-age=0, must-revalidate',
    },
  });
};
