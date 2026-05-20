"""scholar_skill_pack CLI.

Phase 0 骨架：所有命令均已注册并可显示帮助；
具体业务逻辑在后续 Phase 中逐步实现。

支持调用方式：
    python -m scholar_skill_pack.cli --help
    python -m scholar_skill_pack.cli <command> --help
    scholar-skill-pack <command>           # 安装后

注：因为本项目使用 src 布局，需先在项目根目录执行
    pip install -e .
否则用 PYTHONPATH=src python -m scholar_skill_pack.cli ...
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .ingest import ingest_all, write_parse_report
from .paper_card import (
    assemble_extraction_prompt,
    audit_paper_card,
    batch_audit,
    extract_claims_from_card,
    generate_phase2_report,
    paper_card_path,
    prepare_paper_context,
    write_paper_card_draft,
)
from .maintenance import (
    detect_new_papers,
    incremental_ingest,
    stage_new_paper_updates,
    write_change_log,
)
from .registry import list_papers
from .utils import find_project_root, now_iso, project_paths
from .wiki_ops import read_page
from .wiki_synthesis import (
    assemble_wiki_context,
    generate_research_timeline_content,
    load_all_paper_cards,
    write_source_registry_page,
    write_wiki_hub_page,
)


COMMANDS: dict[str, str] = {
    "init": "初始化项目结构（验证目录与模板）",
    "parse": "解析 data/raw/papers/*.pdf（Phase 1）",
    "registry": "更新 source / paper registry（Phase 1）",
    "extract-paper-cards": "生成 Paper Card 草稿（Phase 2）",
    "audit-evidence": "证据审计（Phase 2）",
    "build-wiki": "构建或更新 Scholar Wiki（Phase 3-4）",
    "distill-methods": "生成 Method Cards（Phase 5）",
    "distill-thinking": "生成 Thinking Models（Phase 6）",
    "compile-skill": "编译 Scholar Skill（Phase 7）",
    "lint": "运行 Wiki lint 与质量门禁",
    "eval": "执行评估（Phase 9）",
    "snapshot": "导出当前版本快照",
    "ask": "无 UI 询问 Scholar Skill",
    "update": "增量更新 — 检测新论文并最小化更新知识库（Phase 10）",
}


def _stub(name: str) -> int:
    """占位实现，返回非零以便上层脚本判断'未实现'。"""
    print(f"[Phase 0 stub] '{name}' 尚未实现。请按规划书 §8 阶段顺序推进。")
    return 2


def cmd_init(args: argparse.Namespace) -> int:
    """检查项目结构与必需文件是否齐全。"""
    root = find_project_root(Path.cwd())
    if root is None:
        print("✗ 未找到项目根（缺少 pyproject.toml + CLAUDE.md）。", file=sys.stderr)
        return 1

    print(f"项目根: {root}")
    required_dirs = [
        "config", "data/raw/papers", "data/processed", "data/registry",
        "schemas", "wiki/papers", "wiki/concepts", "wiki/methods",
        "wiki/datasets", "wiki/experiments", "wiki/claims",
        "wiki/synthesis", "wiki/logs",
        "method_cards/cards", "thinking_models/models",
        "scholar_skill", ".claude/skills", ".claude/agents",
        ".claude/rules", "src/scholar_skill_pack", "scripts",
        "prompts", "eval/eval_results",
        "reports/phase_reports", "reports/quality_reports",
        "reports/ingestion_reports",
    ]
    required_files = [
        "CLAUDE.md", "PROJECT_STATE.md", "README.md", "pyproject.toml",
        "config/scholar.yaml", "config/pipeline.yaml",
        "config/quality_gates.yaml", "config/prompts.yaml",
        "schemas/paper_card.schema.json", "schemas/evidence.schema.json",
        "schemas/method_card.schema.json", "schemas/thinking_model.schema.json",
        "schemas/wiki_page.schema.json", "schemas/qa_eval.schema.json",
        ".claude/CLAUDE.md", ".claude/settings.json",
    ]

    missing_dirs = [d for d in required_dirs if not (root / d).is_dir()]
    missing_files = [f for f in required_files if not (root / f).is_file()]

    print(f"\n✓ 目录: {len(required_dirs) - len(missing_dirs)}/{len(required_dirs)}")
    if missing_dirs:
        print("  缺失目录:")
        for d in missing_dirs:
            print(f"    - {d}")

    print(f"✓ 必需文件: {len(required_files) - len(missing_files)}/{len(required_files)}")
    if missing_files:
        print("  缺失文件:")
        for f in missing_files:
            print(f"    - {f}")

    skills_dir = root / ".claude/skills"
    if skills_dir.is_dir():
        skills = sorted(p.name for p in skills_dir.iterdir() if p.is_dir())
        skill_files = [s for s in skills if (skills_dir / s / "SKILL.md").is_file()]
        print(f"✓ Skills: {len(skill_files)}/{len(skills)} 已写入 SKILL.md")
        for s in skills:
            ok = (skills_dir / s / "SKILL.md").is_file()
            print(f"    [{'x' if ok else ' '}] {s}")

    agents_dir = root / ".claude/agents"
    if agents_dir.is_dir():
        agents = sorted(p.name for p in agents_dir.glob("*.md"))
        print(f"✓ Agents: {len(agents)} 个")
        for a in agents:
            print(f"    - {a}")

    pdfs = list((root / "data/raw/papers").glob("*.pdf")) if (root / "data/raw/papers").is_dir() else []
    print(f"\n论文 PDF: {len(pdfs)} 个待处理")

    ok = not missing_dirs and not missing_files
    print("\n=> Phase 0 验证: " + ("通过 ✓" if ok else "未通过 ✗"))
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scholar_skill_pack",
        description=(
            "Academic Master Skill Pack — 把目标学者的公开论文集合"
            "炼化为 AI 科研助手。详见 CLAUDE.md 与项目规划书。"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="规划书：Academic_Master_Skill_Pack_项目规划书.md",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="cmd", metavar="<command>")
    for name, desc in COMMANDS.items():
        sp = sub.add_parser(name, help=desc, description=desc)
        if name == "ask":
            sp.add_argument("question", nargs="?", help="科研问题")
        elif name == "parse":
            sp.add_argument("--force", action="store_true", help="强制重新解析")
        elif name == "extract-paper-cards":
            sp.add_argument("--paper", help="指定 paper_id（默认全部）")
            sp.add_argument("--draft", action="store_true", help="同时创建 Paper Card 草稿模板")
        elif name == "audit-evidence":
            sp.add_argument("--paper", help="指定 paper_id（默认全部）")
        elif name == "snapshot":
            sp.add_argument("--out", default="reports/snapshots", help="输出目录")
    return parser


def cmd_extract_paper_cards(args: argparse.Namespace) -> int:
    """Phase 2: 为论文生成提取上下文和 Paper Card 模板。"""
    root = find_project_root(Path.cwd())
    if root is None:
        print("✗ 未找到项目根（缺少 pyproject.toml + CLAUDE.md）。", file=sys.stderr)
        return 1

    paths = project_paths(root)
    papers = list_papers(paths["registry"] / "paper_registry.jsonl")

    if args.paper:
        papers = [p for p in papers if p["paper_id"] == args.paper]
        if not papers:
            print(f"✗ 未找到 paper_id={args.paper}", file=sys.stderr)
            return 1

    print(f"处理 {len(papers)} 篇论文...")

    prompt_dir = paths["registry"].parent / "processed" / "extraction_prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)

    # 去重：跳过已标记为重复的
    seen_titles: set[str] = set()
    paper_summaries: list[dict[str, Any]] = []

    for i, paper in enumerate(papers, 1):
        pid = paper["paper_id"]
        title = (paper.get("title") or "").strip()

        # 简单去重：同标题只处理第一个
        title_key = title.lower()
        if title_key in seen_titles:
            print(f"  [{i}/{len(papers)}] {pid}: 跳过（重复标题）")
            continue
        seen_titles.add(title_key)

        try:
            ctx = prepare_paper_context(root, pid)
        except ValueError as e:
            print(f"  [{i}/{len(papers)}] {pid}: 错误 — {e}")
            continue

        # 生成提取提示并写入文件
        prompt = assemble_extraction_prompt(ctx)
        prompt_path = prompt_dir / f"{pid}.md"
        prompt_path.write_text(prompt, encoding="utf-8")

        print(f"  [{i}/{len(papers)}] {pid}: {title[:60]} ({ctx['chunk_count']} chunks)")

        # 如果指定了 --draft，也写一个空白 Paper Card 模板
        if args.draft:
            year = paper.get("year")
            card_path = paper_card_path(paths["wiki"], year, title, pid)
            fm = {
                "page_id": f"paper-{pid}",
                "title": title,
                "source_papers": [pid],
                "paper_year": year,
                "authors": paper.get("authors", []),
                "venue": paper.get("venue", ""),
            }
            body = f"# Paper: {title}\n\n"
            body += "## 1. 元信息\n\n"
            body += f"- paper_id: {pid}\n- title: {title}\n- year: {year}\n"
            body += f"- authors: {', '.join(paper.get('authors', []))}\n"
            body += f"- venue: {paper.get('venue', '')}\n\n"
            body += "## 2. 一句话贡献\n\n[待提取]\n\n"
            body += "## 3. 研究问题\n\n[待提取]\n\n"
            body += "## 4. 核心思想\n\n[待提取]\n\n"
            body += "## 5. 方法框架\n\n[待提取]\n\n"
            body += "## 6. 实验设计\n\n[待提取]\n\n"
            body += "## 7. 关键结论\n\n[待提取]\n\n"
            body += "## 8. 隐含假设\n\n[待提取]\n\n"
            body += "## 9. 局限性\n\n[待提取]\n\n"
            body += "## 10. 可迁移启发\n\n[待提取，C 类迁移推断]\n\n"
            body += "## 11. 与其他论文关系\n\n[待提取]\n\n"
            body += "## 12. Evidence 列表\n\n"
            body += "| evidence_id | page | section | claim_type | confidence |\n"
            body += "|---|---:|---|---|\n"
            write_paper_card_draft(card_path, fm, body)

        paper_summaries.append({
            "file": f"{pid}.md",
            "paper_id": pid,
            "title": title,
            "chunk_count": ctx["chunk_count"],
            "prompt_path": str(prompt_path),
        })

    print(f"\n提取提示已写入: {prompt_dir}")
    print(f"共生成 {len(paper_summaries)} 个提取提示")
    if args.draft:
        print(f"已创建 {len(paper_summaries)} 个 Paper Card 草稿模板")
    return 0


def cmd_audit_evidence(args: argparse.Namespace) -> int:
    """Phase 2: 审计 wiki/papers/ 下的 Paper Card evidence 覆盖。"""
    root = find_project_root(Path.cwd())
    if root is None:
        print("✗ 未找到项目根（缺少 pyproject.toml + CLAUDE.md）。", file=sys.stderr)
        return 1

    paths = project_paths(root)

    if args.paper:
        card_path = paths["wiki"] / "papers" / f"{args.paper}.md"
        if not card_path.is_file():
            print(f"✗ Paper Card 不存在: {card_path}", file=sys.stderr)
            return 1
        audit = audit_paper_card(card_path, args.paper)
        print(f"\n{args.paper}:")
        print(f"  通过: {'✓' if audit['passed'] else '✗'}")
        print(f"  Evidence 引用: {audit['stats'].get('total_evidence_refs', '?')}")
        for issue in audit.get("issues", []):
            print(f"  - {issue}")
        suspect = audit.get("stats", {}).get("suspect_lines", [])
        if suspect:
            print(f"  疑似无源结论行: {suspect}")
        return 0 if audit["passed"] else 2

    print("审计所有 Paper Card...")
    audit_result = batch_audit(root)

    s = audit_result["summary"]
    print(f"\n总数: {s['total']}, 通过: {s['passed']}, 未通过: {s['failed']}")

    # 收集 paper summaries
    papers = list_papers(paths["registry"] / "paper_registry.jsonl")
    paper_summaries: list[dict[str, Any]] = []
    for r in audit_result.get("results", []):
        ps = {
            "file": r.get("file", ""),
            "title": "",
            "evidence_count": r.get("stats", {}).get("total_evidence_refs", 0),
            "issues": len(r.get("issues", [])),
            "passed": r.get("passed", False),
        }
        paper_summaries.append(ps)

    report_path = generate_phase2_report(root, audit_result, paper_summaries)
    print(f"报告: {report_path}")

    for r in audit_result.get("results", []):
        if not r.get("passed"):
            print(f"\n  ✗ {r.get('file')}:")
            for issue in r.get("issues", []):
                print(f"    - {issue}")

    return 0 if audit_result["passed"] else 2


def cmd_audit_evidence(args: argparse.Namespace) -> int:
    """Phase 2: 审计 wiki/papers/ 下的 Paper Card evidence 覆盖。"""
    root = find_project_root(Path.cwd())
    if root is None:
        print("✗ 未找到项目根（缺少 pyproject.toml + CLAUDE.md）。", file=sys.stderr)
        return 1

    paths = project_paths(root)

    if args.paper:
        card_path = paths["wiki"] / "papers" / f"{args.paper}.md"
        if not card_path.is_file():
            print(f"✗ Paper Card 不存在: {card_path}", file=sys.stderr)
            return 1
        audit = audit_paper_card(card_path, args.paper)
        print(f"\n{args.paper}:")
        print(f"  通过: {'✓' if audit['passed'] else '✗'}")
        print(f"  Evidence 引用: {audit['stats'].get('total_evidence_refs', '?')}")
        for issue in audit.get("issues", []):
            print(f"  - {issue}")
        suspect = audit.get("stats", {}).get("suspect_lines", [])
        if suspect:
            print(f"  疑似无源结论行: {suspect}")
        return 0 if audit["passed"] else 2

    print("审计所有 Paper Card...")
    audit_result = batch_audit(root)

    s = audit_result["summary"]
    print(f"\n总数: {s['total']}, 通过: {s['passed']}, 未通过: {s['failed']}")

    papers = list_papers(paths["registry"] / "paper_registry.jsonl")
    paper_summaries: list[dict[str, Any]] = []
    for r in audit_result.get("results", []):
        ps = {
            "file": r.get("file", ""),
            "title": "",
            "evidence_count": r.get("stats", {}).get("total_evidence_refs", 0),
            "issues": len(r.get("issues", [])),
            "passed": r.get("passed", False),
        }
        paper_summaries.append(ps)

    report_path = generate_phase2_report(root, audit_result, paper_summaries)
    print(f"报告: {report_path}")

    for r in audit_result.get("results", []):
        if not r.get("passed"):
            print(f"\n  ✗ {r.get('file')}:")
            for issue in r.get("issues", []):
                print(f"    - {issue}")

    return 0 if audit_result["passed"] else 2


def cmd_build_wiki(args: argparse.Namespace) -> int:
    """Phase 3-4: 从 Paper Cards 构建 Scholar Wiki。"""
    root = find_project_root(Path.cwd())
    if root is None:
        print("✗ 未找到项目根。", file=sys.stderr)
        return 1

    paths = project_paths(root)
    cards = load_all_paper_cards(root)
    print(f"加载 {len(cards)} 篇 Paper Card")

    # 1. Source Registry（纯机械）
    print("生成 source_registry.md...")
    write_source_registry_page(root)
    print("  ✓ source_registry.md")

    # 2. Research Timeline（半机械）
    print("生成 research_timeline.md...")
    timeline = generate_research_timeline_content(cards)
    write_wiki_hub_page(root, "research_timeline", {
        "title": "Research Timeline",
        "source_papers": [c["paper_id"] for c in cards[:5]],
    }, timeline)
    print("  ✓ research_timeline.md")

    # 3. 汇总上下文（供 LLM agent 使用）
    print("装配 Wiki 上下文...")
    ctx = assemble_wiki_context(root)

    # 写上下文摘要到文件供 agent 使用
    ctx_dir = paths["wiki"] / "logs" / "synthesis_context"
    ctx_dir.mkdir(parents=True, exist_ok=True)

    # 论文简表
    import json
    (ctx_dir / "paper_summary.json").write_text(
        json.dumps({
            "n_papers": ctx["n_papers"],
            "year_range": ctx["year_range"],
            "table": ctx["paper_table"],
            "method_count": len(ctx["all_methods"]),
            "dataset_count": len(ctx["all_datasets"]),
            "concept_count": len(ctx["all_concepts"]),
        }, ensure_ascii=False, indent=2), encoding="utf-8")

    # 方法清单
    (ctx_dir / "methods.json").write_text(
        json.dumps(ctx["top_methods"], ensure_ascii=False, indent=2), encoding="utf-8")

    # 数据集清单
    (ctx_dir / "datasets.json").write_text(
        json.dumps(ctx["top_datasets"], ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"  ✓ 上下文写入 {ctx_dir}")
    print(f"  论文: {ctx['n_papers']} 篇 ({ctx['year_range']})")
    print(f"  方法候选: {len(ctx['all_methods'])} 个")
    print(f"  数据集候选: {len(ctx['all_datasets'])} 个")

    print("\n下一步: 使用 Claude Code agents 生成以下页面：")
    print("  - wiki/index.md (导航中心)")
    print("  - wiki/research_questions.md (研究问题分类)")
    print("  - wiki/glossary.md (术语表)")
    print("  - wiki/open_questions.md (开放问题)")
    print("  - wiki/contradictions.md (矛盾候选)")
    print("  - wiki/limitations.md (局限性总结)")
    print("  - wiki/concepts/*.md (概念页)")
    print("  - wiki/methods/*.md (方法页草稿)")
    return 0


def cmd_parse(args: argparse.Namespace) -> int:
    """Phase 1: 解析 PDF → pdf_text → sections → chunks → registries → 报告。"""
    root = find_project_root(Path.cwd())
    if root is None:
        print("✗ 未找到项目根（缺少 pyproject.toml + CLAUDE.md）。", file=sys.stderr)
        return 1

    print(f"项目根: {root}")
    pdfs = sorted((root / "data/raw/papers").glob("*.pdf"))
    if not pdfs:
        print("✗ data/raw/papers/ 下没有 PDF 文件。", file=sys.stderr)
        return 1

    print(f"发现 {len(pdfs)} 个 PDF，开始 Phase 1 解析...")
    summary = ingest_all(root, force=args.force)
    report_path = write_parse_report(root, summary)

    qg = summary.get("qg1", {})
    passed = qg.get("passed", False)
    print(f"\nQG1 质量门禁: {'通过 ✓' if passed else '未通过 ✗'}")
    print(f"解析成功: {qg.get('has_title_candidate', '?')} 有标题, "
          f"{qg.get('text_ratio_above_min', '?')} 文本率达标")
    print(f"报告: {report_path}")
    return 0 if passed else 2


def cmd_update(args: argparse.Namespace) -> int:
    """Phase 10: 增量更新 — 检测新论文并做最小化更新。"""
    root = find_project_root(Path.cwd())
    if root is None:
        print("✗ 未找到项目根。", file=sys.stderr)
        return 1

    # 1. Detect new papers
    new = detect_new_papers(root)
    if not new:
        print("✓ 无新增论文。知识库已是最新。")
        return 0

    print(f"检测到 {len(new)} 篇新论文: {new}")

    # 2. Incremental ingest
    result = incremental_ingest(root)
    n_ok = result.get("n_parsed", 0)
    print(f"解析完成: {n_ok} 篇")

    # 3. Get new paper_ids
    paths = project_paths(root)
    papers = list_papers(paths["registry"] / "paper_registry.jsonl")
    new_pids = []
    for fname in new:
        for p in papers:
            if p.get("source_file") == fname:
                new_pids.append(p["paper_id"])
                break

    # 4. Stage updates
    if new_pids:
        staging_dir = stage_new_paper_updates(root, new_pids)
        print(f"Staging 目录: {staging_dir}")

    # 5. Write change log
    changes = {
        "new_papers": new,
        "new_pages": [f"wiki/papers/*{pid}*.md" for pid in new_pids],
        "modified_pages": [],
        "needs_review": [
            "请为每篇新论文执行 Phase 2 (Paper Card 炼化)",
            "然后更新 wiki/research_timeline.md 和 wiki/source_registry.md",
            "检查是否需要新增 Method Card 或更新现有卡片",
            "重新编译 Scholar Skill (Phase 7)",
        ],
    }
    run_id = result.get("run_id") or f"inc-{now_iso()[:19]}"
    log_path = write_change_log(root, run_id, changes)
    print(f"变更日志: {log_path}")

    print("\n" + "=" * 60)
    print("  增量更新流程")
    print("=" * 60)
    print("已完成:")
    print("  ✓ 新论文解析 + registry 更新")
    print("  ✓ Staging 目录创建")
    print("  ✓ 变更日志写入")
    print()
    print("待手动执行 (Claude Code):")
    print("  1. /ingest-papers (为新论文生成 Paper Card)")
    print("  2. 更新 wiki/research_timeline.md")
    print("  3. 更新 wiki/source_registry.md")
    print("  4. 检查 Method Cards 是否需要更新")
    print("  5. /compile-scholar-skill (重新编译 Skill)")
    print("  6. /lint-wiki (质量检查)")
    return 0


def cmd_ask(args: argparse.Namespace) -> int:
    """无 UI 科研助手问答。加载 Scholar Skill 上下文并输出引导提示。"""
    root = find_project_root(Path.cwd())
    if root is None:
        print("✗ 未找到项目根。", file=sys.stderr)
        return 1

    question = args.question or "请介绍陈志远教授的研究范式"

    # 加载核心 briefing
    briefing_path = root / "scholar_skill" / "scholar_briefing.md"
    briefing = ""
    if briefing_path.is_file():
        briefing = briefing_path.read_text(encoding="utf-8")

    # 加载 Wiki 索引
    wiki_index = ""
    wiki_index_path = root / "wiki" / "index.md"
    if wiki_index_path.is_file():
        wiki_index = wiki_index_path.read_text(encoding="utf-8")[:2000]

    # 输出上下文提示
    print("=" * 60)
    print("  陈志远教授 Scholar Skill — 科研助手")
    print("=" * 60)
    print()
    print("【学者速览】")
    print(briefing[:3000] if briefing else "(briefing not found)")
    print()
    print("【用户问题】")
    print(f"  {question}")
    print()
    print("【回答指引】")
    print("  请基于 Scholar Wiki 回答，严格遵守 A/B/C 证据分级：")
    print("  - A 直接证据: 附 evidence_id")
    print("  - B 综合归纳: ≥ 2 篇论文支持")
    print("  - C 迁移推断: 显式标注'这是推断'")
    print()
    print("【知识库路径】")
    kb_dirs = [
        "wiki/ — 8 hub pages + 23 paper cards + 7 concepts + 7 methods",
        "wiki/synthesis/ — 5 综合页面 (research_lines, method_evolution, ...)",
        "method_cards/cards/ — 7 张完整方法卡片",
        "thinking_models/models/ — 6 个思维模型",
        "scholar_skill/ — 8 个 Skill 支撑文件",
    ]
    for d in kb_dirs:
        print(f"  {d}")
    print()
    print("【回答模板】见 scholar_skill/answer_policy.md")
    print("【证据政策】见 scholar_skill/evidence_policy.md")
    print()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.cmd:
        parser.print_help()
        return 0

    if args.cmd == "init":
        return cmd_init(args)
    if args.cmd == "parse":
        return cmd_parse(args)
    if args.cmd == "extract-paper-cards":
        return cmd_extract_paper_cards(args)
    if args.cmd == "audit-evidence":
        return cmd_audit_evidence(args)
    if args.cmd == "build-wiki":
        return cmd_build_wiki(args)
    if args.cmd == "ask":
        return cmd_ask(args)
    if args.cmd == "update":
        return cmd_update(args)
    return _stub(args.cmd)


if __name__ == "__main__":
    sys.exit(main() or 0)
