import { NextRequest } from "next/server";
import OpenAI from "openai";
import { searchWiki, listMethods, listThinkingModels } from "@/lib/wiki-server";
import fs from "fs";
import path from "path";

const ROOT = path.resolve(process.cwd(), "..");
const SYSTEM_PROMPT = `你是基于通信安全学者（陈志远教授，北京邮电大学网络空间安全学院）15篇公开论文构建的科研助手。你不是该学者本人。

## 回答规则
1. 基于知识库证据直接回答问题，要有实质性内容
2. 区分三类证据：A类（直接论文证据，引用论文ID）、B类（跨论文综合归纳）、C类（迁移推断，需标注"这是推断"）
3. 引用要具体——提到方法时给出方法名，提到结论时给出论文ID
4. 诚实说明局限——如果知识库信息不足，直接说"证据不足"
5. 用中文回答，专业术语可保留英文
6. 用markdown组织，有层次结构
7. 不要编造论文、数据、实验或观点`;

export async function POST(req: NextRequest) {
  const { question, api_key } = await req.json();

  if (!api_key?.trim()) {
    return new Response(
      "data: " + JSON.stringify({ chunk: "请先在侧边栏设置 DeepSeek API Key" }) + "\n\n",
      { headers: { "Content-Type": "text/event-stream" } }
    );
  }

  // Build context
  const ctx = buildContext(question || "");

  const userPrompt = `## 知识库参考
${ctx}

## 用户问题
${question}

请基于以上知识库内容，给出有深度的回答。`;

  const client = new OpenAI({
    apiKey: api_key.trim(),
    baseURL: "https://api.deepseek.com",
  });

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      try {
        const completion = await client.chat.completions.create({
          model: "deepseek-chat",
          messages: [
            { role: "system", content: SYSTEM_PROMPT },
            { role: "user", content: userPrompt },
          ],
          temperature: 0.3,
          max_tokens: 4000,
          stream: true,
        });

        for await (const chunk of completion) {
          const delta = chunk.choices[0]?.delta?.content;
          if (delta) {
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({ chunk: delta })}\n\n`));
          }
        }
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ done: true })}\n\n`));
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : "Unknown error";
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ chunk: `\n> 调用出错: ${msg}\n` })}\n\n`));
      }
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}

function buildContext(question: string): string {
  const parts: string[] = [];
  let total = 0;
  const limit = 6000;
  const q = question.toLowerCase();

  function add(content: string) {
    if (total > limit) return;
    parts.push(content);
    total += content.length;
  }

  // Wiki index
  const indexPath = path.join(ROOT, "wiki", "index.md");
  if (fs.existsSync(indexPath)) {
    add(fs.readFileSync(indexPath, "utf-8").slice(0, 1500));
  }

  // Research paradigm
  for (const f of ["research_paradigm.md", "research_questions.md", "glossary.md"]) {
    const fp = path.join(ROOT, "wiki", f);
    if (fs.existsSync(fp)) add(fs.readFileSync(fp, "utf-8").slice(0, 800));
  }

  // Synthesis pages
  const synDir = path.join(ROOT, "wiki", "synthesis");
  if (fs.existsSync(synDir)) {
    for (const f of fs.readdirSync(synDir)) {
      if (total > limit) break;
      const fp = path.join(synDir, f);
      add(fs.readFileSync(fp, "utf-8").slice(0, 600));
    }
  }

  // Concept pages
  const conDir = path.join(ROOT, "wiki", "concepts");
  if (fs.existsSync(conDir)) {
    for (const f of fs.readdirSync(conDir)) {
      if (total > limit) break;
      const fp = path.join(conDir, f);
      add(fs.readFileSync(fp, "utf-8").slice(0, 500));
    }
  }

  // Method cards
  const methods = listMethods();
  for (const m of methods.slice(0, 5)) {
    if (total > limit) break;
    const fp = path.join(ROOT, m.path);
    if (fs.existsSync(fp)) add(fs.readFileSync(fp, "utf-8").slice(0, 400));
  }

  // Thinking models
  const models = listThinkingModels();
  for (const tm of models.slice(0, 3)) {
    if (total > limit) break;
    const fp = path.join(ROOT, tm.path);
    if (fs.existsSync(fp)) add(fs.readFileSync(fp, "utf-8").slice(0, 400));
  }

  return parts.join("\n---\n");
}
