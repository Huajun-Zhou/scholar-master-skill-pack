"""AutoGen GraphFlow 工作流。

提供三个科研工作流:
- ask_scholar_flow: 4-agent 问答
- design_research_flow: 9-agent 研究设计
- critique_paper_flow: 7-agent 论文审查
"""

from .ask_scholar_flow import build_ask_scholar_flow
from .critique_paper_flow import build_critique_paper_flow
from .design_research_flow import build_design_research_flow

__all__ = [
    "build_ask_scholar_flow",
    "build_design_research_flow",
    "build_critique_paper_flow",
]
