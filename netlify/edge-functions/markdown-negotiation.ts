import { Context } from '@netlify/edge-functions';

// Decode the most common HTML entities back into plain text characters.
const decodeEntities = (text: string): string =>
  text
    .replace(/&nbsp;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&lt;/gi, '<')
    .replace(/&gt;/gi, '>')
    .replace(/&quot;/gi, '"')
    .replace(/&#39;/gi, "'")
    .replace(/&apos;/gi, "'")
    .replace(/&#(\d+);/g, (_, code) => String.fromCharCode(Number(code)))
    .replace(/&#x([0-9a-f]+);/gi, (_, code) => String.fromCharCode(parseInt(code, 16)));

const stripTags = (html: string): string => decodeEntities(html.replace(/<[^>]+>/g, '')).trim();

/**
 * Convert an HTML document body into a reasonable Markdown representation.
 * This is intentionally dependency-free so it runs natively in the Deno
 * edge runtime (Turndown/domino are Node-only and fail the edge bundler).
 */
const htmlToMarkdown = (html: string): string => {
  let md = html;

  // Remove non-content elements entirely.
  md = md.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
  md = md.replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, '');
  md = md.replace(/<head\b[^<]*(?:(?!<\/head>)<[^<]*)*<\/head>/gi, '');
  md = md.replace(/<header\b[^<]*(?:(?!<\/header>)<[^<]*)*<\/header>/gi, '');
  md = md.replace(/<footer\b[^<]*(?:(?!<\/footer>)<[^<]*)*<\/footer>/gi, '');
  md = md.replace(/<nav\b[^<]*(?:(?!<\/nav>)<[^<]*)*<\/nav>/gi, '');
  md = md.replace(/<svg\b[^<]*(?:(?!<\/svg>)<[^<]*)*<\/svg>/gi, '');
  md = md.replace(/<!--[\s\S]*?-->/g, '');

  // Images -> ![alt](src)
  md = md.replace(/<img\b[^>]*?>/gi, (tag) => {
    const src = tag.match(/\bsrc\s*=\s*["']([^"']*)["']/i)?.[1] ?? '';
    const alt = tag.match(/\balt\s*=\s*["']([^"']*)["']/i)?.[1] ?? '';
    return src ? `![${alt}](${src})` : '';
  });

  // Links -> [text](href)
  md = md.replace(/<a\b([^>]*)>([\s\S]*?)<\/a>/gi, (_match, attrs, inner) => {
    const href = String(attrs).match(/\bhref\s*=\s*["']([^"']*)["']/i)?.[1] ?? '';
    const text = stripTags(inner);
    if (!text) return '';
    return href ? `[${text}](${href})` : text;
  });

  // Headings
  for (let level = 1; level <= 6; level++) {
    const re = new RegExp(`<h${level}\\b[^>]*>([\\s\\S]*?)<\\/h${level}>`, 'gi');
    md = md.replace(re, (_match, inner) => `\n\n${'#'.repeat(level)} ${stripTags(inner)}\n\n`);
  }

  // Bold and italic
  md = md.replace(/<(strong|b)\b[^>]*>([\s\S]*?)<\/\1>/gi, (_match, _tag, inner) => `**${stripTags(inner)}**`);
  md = md.replace(/<(em|i)\b[^>]*>([\s\S]*?)<\/\1>/gi, (_match, _tag, inner) => `*${stripTags(inner)}*`);

  // Inline code and pre blocks
  md = md.replace(/<pre\b[^>]*>([\s\S]*?)<\/pre>/gi, (_match, inner) => `\n\n\`\`\`\n${stripTags(inner)}\n\`\`\`\n\n`);
  md = md.replace(/<code\b[^>]*>([\s\S]*?)<\/code>/gi, (_match, inner) => `\`${stripTags(inner)}\``);

  // Blockquotes
  md = md.replace(/<blockquote\b[^>]*>([\s\S]*?)<\/blockquote>/gi, (_match, inner) => `\n\n> ${stripTags(inner)}\n\n`);

  // List items
  md = md.replace(/<li\b[^>]*>([\s\S]*?)<\/li>/gi, (_match, inner) => `\n- ${stripTags(inner)}`);
  md = md.replace(/<\/(ul|ol)>/gi, '\n\n');

  // Horizontal rules
  md = md.replace(/<hr\b[^>]*\/?>/gi, '\n\n---\n\n');

  // Line breaks and paragraphs
  md = md.replace(/<br\s*\/?>/gi, '\n');
  md = md.replace(/<\/p>/gi, '\n\n');

  // Strip any remaining tags and decode entities.
  md = stripTags(md);

  // Collapse excessive blank lines.
  md = md.replace(/\n{3,}/g, '\n\n').trim();

  return md;
};

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

  const html = await response.text();
  const markdown = htmlToMarkdown(html);

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
