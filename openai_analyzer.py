import os
import json
from datetime import datetime
from typing import Dict, Any

try:
    import openai
except ImportError as e:  # Keep the import local so that the main app can still run basic analysis without the package
    openai = None


class OpenAIResumeAnalyzer:
    """A dedicated helper class that calls the OpenAI API to analyse resume text.

    Extracting the OpenAI-specific logic into its own module keeps `pdf_processor.py`
    focused purely on PDF parsing / fallback heuristics and facilitates easier unit
    testing (the class can be mocked) as well as future model or prompt changes.
    """

    # --- Prompt template ----------------------------------------------------
    PROMPT_TEMPLATE = """
根据你提供的简历内容，以下将以清晰的 Markdown 形式给出候选人在德国求职市场的分析与优化建议：

---

## 1. 推荐的职业方向与关键词（适用于德国求职平台搜索）

请列出 **3-4** 个职业方向。每个方向使用“方向一 / 二 / 三 …”标题，并在下一行用“关键词：”列出 5-8 个德/英关键词，示例：

方向一：Risikomanagement / Financial Risk Controlling  
• 关键词：Risk Management, Financial Risk Analyst, Risikocontrolling, VaR/CVaR, FRM, CFA

---

## 2. 各段工作经历匹配的职位名称（德国市场常用术语）

按照时间顺序，对 **每一段** 工作经历先用一行 `✅ 起止时间 – 职位 – 公司` 概要，下一行标题“适合的职位名称:”，随后用无序列表列出 3-4 个职位。

---

## 3. 工作经历内容的优化建议（前两条内容重写）

对每段经历，先用 `◆ 公司 / 职位` 作为小标题，分两块：
• **原文：** 使用无序列表列出原始前两条描述；  
• **优化后：** 用无序列表给出量化、成果导向的改写。

---

请直接输出 Markdown，不要使用代码块或额外说明。

以下为候选人的简历原文：
{text}
"""

    def __init__(self, api_key: str | None = None, model: str = "gpt-3.5-turbo"):
        """Instantiate the OpenAI client.

        Parameters
        ----------
        api_key: str | None
            Explicit key.  If *None* (default) the method falls back to the
            `OPENAI_API_KEY` environment variable so that the calling
            application can manage secrets in whichever way it prefers.
        model: str
            Model name to call – kept configurable for easy future upgrades.
        """
        if openai is None:
            raise ImportError("The `openai` package is required for advanced resume analysis. Install it first.")

        self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model

    # ---------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------
    def analyse(self, text: str) -> str:
        """Call Chat Completions API with the predefined prompt.

        Returns the parsed Markdown response.
        """
        system_notice = "You are a professional resume analyzer. Reply ONLY with formatted Markdown as instructed, no extra commentary."  # noqa: E501

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_notice},
                {"role": "user", "content": self.PROMPT_TEMPLATE.format(text=text)},
            ],
            temperature=0.3,
            max_tokens=2500,
        )

        markdown_output: str = response.choices[0].message.content.strip()
        # Remove potential markdown fences accidentally added by the model
        if markdown_output.startswith("```"):
            markdown_output = markdown_output.strip("` ")

        return markdown_output
