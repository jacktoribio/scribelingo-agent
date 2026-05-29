from pathlib import Path
from typing import Optional

from src.analysis.phrases import PhrasesResult
from src.analysis.grammar import GrammarResult
from src.analysis.vocabulary import VocabularyResult


class Reporter:
    def generate(
        self,
        transcript: str,
        phrases: PhrasesResult,
        grammar: GrammarResult,
        vocabulary: VocabularyResult,
        output_path: Path,
        format: str = "html",
    ) -> Path:
        output_path = Path(output_path).resolve()

        if format == "md":
            content = self._build_markdown(
                transcript, phrases, grammar, vocabulary
            )
        else:
            content = self._build_html(
                transcript, phrases, grammar, vocabulary
            )

        output_path.write_text(content, encoding="utf-8")
        return output_path

    def _build_markdown(
        self,
        transcript: str,
        phrases: PhrasesResult,
        grammar: GrammarResult,
        vocabulary: VocabularyResult,
    ) -> str:
        lines = ["# English Learning Report", ""]

        lines.append("## Transcript")
        lines.append("")
        lines.append(transcript)
        lines.append("")

        lines.append("## Common Phrases")
        lines.append("")
        lines.append("| N | Phrase | Score |")
        lines.append("|---|--------|-------|")
        for n, items in sorted(phrases.ngrams.items()):
            for phrase, score in items[:10]:
                lines.append(f"| {n} | {phrase} | {score} |")
        lines.append("")

        if phrases.collocations:
            lines.append("### Collocations (PMI)")
            lines.append("")
            lines.append("| Phrase | PMI |")
            lines.append("|--------|-----|")
            for phrase, score in phrases.collocations[:15]:
                lines.append(f"| {phrase} | {score:.2f} |")
            lines.append("")

        lines.append("## Grammar Patterns")
        lines.append("")
        lines.append("| Pattern | Example | Frequency |")
        lines.append("|---------|---------|-----------|")
        for pattern, example, count in grammar.pos_patterns[:20]:
            example_short = example[:60] if len(example) > 60 else example
            lines.append(f"| {pattern} | {example_short} | {count} |")
        lines.append("")

        lines.append("## Vocabulary")
        lines.append("")
        lines.append("| Word | Frequency |")
        lines.append("|------|-----------|")
        for word, freq in vocabulary.word_freq[:30]:
            lines.append(f"| {word} | {freq} |")
        lines.append("")

        if vocabulary.keywords:
            lines.append("### Key Terms (TF-IDF)")
            lines.append("")
            lines.append("| Word | Score |")
            lines.append("|------|-------|")
            for word, score in vocabulary.keywords[:20]:
                lines.append(f"| {word} | {score:.3f} |")
            lines.append("")

        return "\n".join(lines)

    def _build_html(
        self,
        transcript: str,
        phrases: PhrasesResult,
        grammar: GrammarResult,
        vocabulary: VocabularyResult,
    ) -> str:
        md = self._build_markdown(
            transcript, phrases, grammar, vocabulary
        )
        html_lines = [
            "<!DOCTYPE html>",
            '<html lang="en">',
            "<head><meta charset='utf-8'><title>English Learning Report</title>",
            "<style>",
            "body { font-family: -apple-system, sans-serif; max-width: 960px; margin: 2em auto; padding: 0 1em; }",
            "table { border-collapse: collapse; width: 100%; margin: 1em 0; }",
            "th, td { border: 1px solid #ccc; padding: 0.5em; text-align: left; }",
            "th { background: #f5f5f5; }",
            "h1 { color: #333; }",
            "h2 { color: #555; margin-top: 2em; }",
            "</style></head><body>",
            "<h1>English Learning Report</h1>",
        ]

        html_lines.append("<h2>Transcript</h2>")
        html_lines.append(f"<p>{transcript}</p>")

        html_lines.append("<h2>Common Phrases</h2>")
        if phrases.ngrams:
            html_lines.append("<table><tr><th>N</th><th>Phrase</th><th>Score</th></tr>")
            for n, items in sorted(phrases.ngrams.items()):
                for phrase, score in items[:10]:
                    html_lines.append(
                        f"<tr><td>{n}</td><td>{phrase}</td><td>{score}</td></tr>"
                    )
            html_lines.append("</table>")

        if phrases.collocations:
            html_lines.append("<h3>Collocations (PMI)</h3>")
            html_lines.append("<table><tr><th>Phrase</th><th>PMI</th></tr>")
            for phrase, score in phrases.collocations[:15]:
                html_lines.append(
                    f"<tr><td>{phrase}</td><td>{score:.2f}</td></tr>"
                )
            html_lines.append("</table>")

        html_lines.append("<h2>Grammar Patterns</h2>")
        if grammar.pos_patterns:
            html_lines.append(
                "<table><tr><th>Pattern</th><th>Example</th><th>Frequency</th></tr>"
            )
            for pattern, example, count in grammar.pos_patterns[:20]:
                example_short = (
                    example[:60] if len(example) > 60 else example
                )
                html_lines.append(
                    f"<tr><td>{pattern}</td><td>{example_short}</td>"
                    f"<td>{count}</td></tr>"
                )
            html_lines.append("</table>")

        html_lines.append("<h2>Vocabulary</h2>")
        if vocabulary.word_freq:
            html_lines.append(
                "<table><tr><th>Word</th><th>Frequency</th></tr>"
            )
            for word, freq in vocabulary.word_freq[:30]:
                html_lines.append(
                    f"<tr><td>{word}</td><td>{freq}</td></tr>"
                )
            html_lines.append("</table>")

        if vocabulary.keywords:
            html_lines.append("<h3>Key Terms (TF-IDF)</h3>")
            html_lines.append(
                "<table><tr><th>Word</th><th>Score</th></tr>"
            )
            for word, score in vocabulary.keywords[:20]:
                html_lines.append(
                    f"<tr><td>{word}</td><td>{score:.3f}</td></tr>"
                )
            html_lines.append("</table>")

        html_lines.append("</body></html>")
        return "\n".join(html_lines)
