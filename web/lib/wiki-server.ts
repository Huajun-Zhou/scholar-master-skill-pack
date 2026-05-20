/** Server-side wiki data access layer. Reads markdown files from the project root. */

import fs from "fs";
import path from "path";

// Project root = 3 levels up from web/lib/
const ROOT = path.resolve(process.cwd(), "..");

// ── frontmatter parser ──────────────────────────────────────

function parseFrontmatter(raw: string): {
  frontmatter: Record<string, unknown>;
  body: string;
} {
  if (!raw.startsWith("---")) return { frontmatter: {}, body: raw };
  const close = raw.indexOf("---", 3);
  if (close === -1) return { frontmatter: {}, body: raw };
  const fmText = raw.slice(3, close);
  const body = raw.slice(close + 3).trimStart();
  const fm: Record<string, unknown> = {};
  for (const line of fmText.split("\n")) {
    const colon = line.indexOf(":");
    if (colon > 0) {
      const key = line.slice(0, colon).trim();
      let val: unknown = line.slice(colon + 1).trim();
      // Try parsing as JSON (for arrays)
      if (typeof val === "string" && val.startsWith("[") && val.endsWith("]")) {
        try { val = JSON.parse(val); } catch {}
      }
      fm[key] = val;
    }
  }
  return { frontmatter: fm, body };
}

function readMdFile(relPath: string): { frontmatter: Record<string, unknown>; body: string; path: string } | null {
  const full = path.join(ROOT, relPath);
  if (!fs.existsSync(full)) return null;
  const raw = fs.readFileSync(full, "utf-8");
  const { frontmatter, body } = parseFrontmatter(raw);
  return { frontmatter, body, path: relPath };
}

// ── Papers ──────────────────────────────────────────────────

export function listAllPapers(): Record<string, unknown>[] {
  const regPath = path.join(ROOT, "data", "registry", "paper_registry.jsonl");
  if (!fs.existsSync(regPath)) return [];
  const raw = fs.readFileSync(regPath, "utf-8");
  return raw
    .split("\n")
    .filter(Boolean)
    .map((line) => {
      try { return JSON.parse(line); } catch { return {}; }
    });
}

export function getPaperCard(paperId: string) {
  const dir = path.join(ROOT, "wiki", "papers");
  if (!fs.existsSync(dir)) return null;
  for (const f of fs.readdirSync(dir)) {
    if (!f.endsWith(".md")) continue;
    const page = readMdFile(path.join("wiki", "papers", f));
    if (!page) continue;
    const src = page.frontmatter.source_papers;
    const ids = Array.isArray(src) ? src : [src];
    if (ids.includes(paperId) || String(page.frontmatter.page_id).includes(paperId)) {
      return page;
    }
  }
  return null;
}

// ── Wiki pages ──────────────────────────────────────────────

export function getWikiPage(wikiPath: string) {
  // Try exact path, then with .md extension
  const paths = [wikiPath, `${wikiPath}.md`, wikiPath.endsWith(".md") ? wikiPath : `${wikiPath}.md`];
  for (const p of paths) {
    const page = readMdFile(p.startsWith("wiki/") ? p : `wiki/${p}`);
    if (page) return page;
  }
  return null;
}

export function getWikiIndex() {
  const page = readMdFile("wiki/index.md");
  if (!page) return { frontmatter: {}, body: "", path: "wiki/index.md" };
  return page;
}

// ── Methods ─────────────────────────────────────────────────

export function listMethods(): { id: string; title: string; source_papers: string[]; path: string }[] {
  const dir = path.join(ROOT, "method_cards", "cards");
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir)
    .filter((f) => f.endsWith(".md"))
    .map((f) => {
      const page = readMdFile(path.join("method_cards", "cards", f));
      const fm = page?.frontmatter || {};
      return {
        id: f.replace(".md", ""),
        title: String(fm.title || f),
        source_papers: Array.isArray(fm.source_papers) ? fm.source_papers as string[] : [],
        path: `method_cards/cards/${f}`,
      };
    });
}

export function getMethod(methodId: string) {
  const page = readMdFile(`method_cards/cards/${methodId}.md`);
  if (!page) return null;
  return {
    ...page,
    sections: extractSections(page.body),
  };
}

// ── Thinking Models ─────────────────────────────────────────

export function listThinkingModels(): { id: string; title: string; source_papers: string[]; path: string }[] {
  const dir = path.join(ROOT, "thinking_models", "models");
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir)
    .filter((f) => f.endsWith(".md"))
    .map((f) => {
      const page = readMdFile(path.join("thinking_models", "models", f));
      const fm = page?.frontmatter || {};
      return {
        id: f.replace(".md", ""),
        title: String(fm.title || f),
        source_papers: Array.isArray(fm.source_papers) ? fm.source_papers as string[] : [],
        path: `thinking_models/models/${f}`,
      };
    });
}

export function getThinkingModel(modelId: string) {
  const page = readMdFile(`thinking_models/models/${modelId}.md`);
  if (!page) return null;
  return {
    ...page,
    sections: extractSections(page.body),
  };
}

// ── Search ──────────────────────────────────────────────────

export function searchWiki(query: string, maxResults = 10) {
  const results: { title: string; path: string; snippet: string }[] = [];
  const q = query.toLowerCase();

  function scan(dir: string, prefix: string) {
    const full = path.join(ROOT, dir);
    if (!fs.existsSync(full)) return;
    for (const f of fs.readdirSync(full)) {
      const rel = path.join(prefix, f);
      const abs = path.join(full, f);
      if (fs.statSync(abs).isDirectory()) {
        scan(path.join(dir, f), rel);
        continue;
      }
      if (!f.endsWith(".md")) continue;
      const raw = fs.readFileSync(abs, "utf-8");
      const { frontmatter, body } = parseFrontmatter(raw);
      if (body.toLowerCase().includes(q) || String(frontmatter.title || "").toLowerCase().includes(q)) {
        const idx = body.toLowerCase().indexOf(q);
        const start = Math.max(0, idx - 60);
        results.push({
          title: String(frontmatter.title || f.replace(".md", "")),
          path: rel,
          snippet: body.slice(start, start + 200),
        });
        if (results.length >= maxResults) return;
      }
    }
  }

  scan("wiki", "wiki");
  scan("method_cards/cards", "method_cards/cards");
  scan("thinking_models/models", "thinking_models/models");
  return results.slice(0, maxResults);
}

// ── Section extraction helper ───────────────────────────────

function extractSections(body: string): Record<string, string> {
  const sections: Record<string, string> = {};
  const pattern = /^##\s+\d+\.\s+(.+?)\s*\n+([\s\S]*?)(?=\n+##\s+\d+\.|\n+##\s+[A-Z]|$)/gm;
  let m;
  while ((m = pattern.exec(body)) !== null) {
    sections[m[1]] = m[2].trim();
  }
  return sections;
}
