export type MarkdownInline =
  | { type: 'text'; value: string }
  | { type: 'strong' | 'emphasis' | 'strikethrough'; children: MarkdownInline[] }
  | { type: 'link'; href: string; children: MarkdownInline[] };

export type MarkdownBlock =
  | { type: 'paragraph'; children: MarkdownInline[] }
  | { type: 'list'; items: MarkdownInline[][] };

function safeHref(href: string): string | null {
  const value = href.trim();
  if (/^(?:https?:\/\/|mailto:)/iu.test(value)) return value;
  if (/^(?:\/[^/]|#)/u.test(value)) return value;
  return null;
}

export function parseMarkdownInline(source: string): MarkdownInline[] {
  const nodes: MarkdownInline[] = [];
  let plain = '';

  function flushPlain() {
    if (!plain) return;
    nodes.push({ type: 'text', value: plain });
    plain = '';
  }

  for (let index = 0; index < source.length;) {
    if (source.startsWith('~~', index)) {
      const end = source.indexOf('~~', index + 2);
      if (end > index + 2) {
        flushPlain();
        nodes.push({ type: 'strikethrough', children: parseMarkdownInline(source.slice(index + 2, end)) });
        index = end + 2;
        continue;
      }
    }

    if (source.startsWith('**', index)) {
      const end = source.indexOf('**', index + 2);
      if (end > index + 2) {
        flushPlain();
        nodes.push({ type: 'strong', children: parseMarkdownInline(source.slice(index + 2, end)) });
        index = end + 2;
        continue;
      }
    }

    if (source[index] === '*') {
      const end = source.indexOf('*', index + 1);
      if (end > index + 1) {
        flushPlain();
        nodes.push({ type: 'emphasis', children: parseMarkdownInline(source.slice(index + 1, end)) });
        index = end + 1;
        continue;
      }
    }

    if (source[index] === '[') {
      const labelEnd = source.indexOf('](', index + 1);
      const hrefEnd = labelEnd === -1 ? -1 : source.indexOf(')', labelEnd + 2);
      if (labelEnd > index + 1 && hrefEnd > labelEnd + 2) {
        const href = safeHref(source.slice(labelEnd + 2, hrefEnd));
        if (href) {
          flushPlain();
          nodes.push({
            type: 'link',
            href,
            children: parseMarkdownInline(source.slice(index + 1, labelEnd))
          });
          index = hrefEnd + 1;
          continue;
        }
      }
    }

    plain += source[index];
    index += 1;
  }

  flushPlain();
  return nodes;
}

export function parseMarkdown(source: string): MarkdownBlock[] {
  const blocks: MarkdownBlock[] = [];
  const paragraph: string[] = [];
  let listItems: MarkdownInline[][] = [];

  function flushParagraph() {
    if (!paragraph.length) return;
    blocks.push({ type: 'paragraph', children: parseMarkdownInline(paragraph.join('\n')) });
    paragraph.length = 0;
  }

  function flushList() {
    if (!listItems.length) return;
    blocks.push({ type: 'list', items: listItems });
    listItems = [];
  }

  for (const line of source.split(/\r?\n/u)) {
    const item = line.match(/^\s*-\s+(.+)$/u);
    if (item) {
      flushParagraph();
      listItems.push(parseMarkdownInline(item[1]));
      continue;
    }

    flushList();
    if (line) {
      paragraph.push(line);
    } else {
      flushParagraph();
    }
  }

  flushList();
  flushParagraph();
  return blocks;
}
