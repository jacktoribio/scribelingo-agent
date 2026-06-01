import re
from pathlib import Path

from src.core.models import LLMAnalysisResult


def _inline_md(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    return text


def _md_to_html(text: str) -> str:
    html_parts: list[str] = []
    stack: list[int] = []
    blank_line = True

    for line in text.split("\n"):
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if not stripped:
            blank_line = True
            if not stack:
                html_parts.append("")
            continue

        blank_line = False

        if stripped.startswith("### "):
            while stack:
                stack.pop()
                html_parts.append("</ul>")
            html_parts.append(f"<h3>{_inline_md(stripped[4:])}</h3>")

        elif stripped.startswith("## "):
            while stack:
                stack.pop()
                html_parts.append("</ul>")
            html_parts.append(f"<h2>{_inline_md(stripped[3:])}</h2>")

        elif stripped.startswith("# "):
            while stack:
                stack.pop()
                html_parts.append("</ul>")
            html_parts.append(f"<h1>{_inline_md(stripped[2:])}</h1>")

        elif stripped.startswith("---") and not stripped.strip(" -"):
            while stack:
                stack.pop()
                html_parts.append("</ul>")
            html_parts.append("<hr>")

        elif stripped.startswith("* ") or stripped.startswith("- "):
            while stack and stack[-1] > indent:
                stack.pop()
                html_parts.append("</ul>")

            if not stack or stack[-1] < indent:
                stack.append(indent)
                html_parts.append("<ul>")

            content = _inline_md(stripped[2:])
            html_parts.append(f"<li>{content}</li>")

        else:
            while stack:
                stack.pop()
                html_parts.append("</ul>")
            html_parts.append(f"<p>{_inline_md(stripped)}</p>")

    while stack:
        stack.pop()
        html_parts.append("</ul>")

    return "\n".join(html_parts)


class ReportGenerator:
    def generate(
        self,
        transcript: str,
        analysis: LLMAnalysisResult,
        output_path: Path,
        format: str = "html",
    ) -> Path:
        output_path = Path(output_path).resolve()

        if format == "md":
            content = self._build_markdown(transcript, analysis)
        else:
            content = self._build_html(transcript, analysis)

        output_path.write_text(content, encoding="utf-8")
        return output_path

    def _build_markdown(
        self, transcript: str, analysis: LLMAnalysisResult
    ) -> str:
        lines = [
            "# English Learning Report",
            "",
            "## Transcript",
            "",
            transcript,
            "",
            "---",
            "",
            analysis.markdown,
        ]
        return "\n".join(lines)

    def _build_html(
        self, transcript: str, analysis: LLMAnalysisResult
    ) -> str:
        body = _md_to_html(analysis.markdown)

        return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset='utf-8'><title>English Learning Report</title>
<style>
body {{ font-family: -apple-system, sans-serif; max-width: 960px; margin: 2em auto; padding: 0 1em; line-height: 1.6; }}
h1 {{ color: #333; }}
h2 {{ color: #555; margin-top: 2em; }}
h3 {{ color: #666; margin-top: 1.5em; }}
p {{ margin: 0.5em 0; }}
ul {{ margin: 0.5em 0; padding-left: 1.5em; }}
li {{ margin: 0.3em 0; }}
code {{ background: #f4f4f4; padding: 0.2em 0.4em; border-radius: 3px; }}
hr {{ border: none; border-top: 1px solid #ddd; margin: 2em 0; }}
.transcript {{ background: #f9f9f9; padding: 1em; border-radius: 5px; }}
</style></head><body>
<h1>English Learning Report</h1>
<h2>Transcript</h2>
<div class="transcript"><p>{transcript}</p></div>
<hr>
{body}
</body></html>"""
