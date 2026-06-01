import os
from textwrap import dedent

from openai import OpenAI

from src.core.models import LLMAnalysisResult
from src.core.ports import AnalyzerPort


class AnalysisError(Exception):
    pass


_SYSTEM_PROMPT = dedent("""\
You are an expert English language teacher and linguistic analyst. I am learning English and want to use the text I provide as a study guide.

Analyze the text and break it down into a highly structured, easy-to-read study guide. Your output must strictly follow the format below.

OUTPUT FORMAT INSTRUCTIONS:
Please provide the analysis in English, using the exact headers and bullet points below. For each example found, include the original phrase from the text and a brief, beginner-friendly explanation of why it is important or how it is used.

### 1. Common Verb Tenses & Grammatical Structures
Identify the most prominent verb tenses or structures (e.g., Present Perfect, Past Simple, Passive Voice, Modal Verbs) used in the text. 

For each tense/structure identified, provide a brief explanation of its usage, followed by a bulleted list of at least 5 exact phrases extracted from the text. Crucially, sort these examples in descending order based on how frequently that specific structure or variation repeats in the text (from most frequent to least frequent).

* [Verb Tense/Structure Name]: [Brief explanation of why this tense is used here].
  - "[Example 1 from text (Most frequent)]" ([Speaker Name] - [MM:SS])
  - "[Example 2 from text]" ([Speaker Name] - [MM:SS])
  - "[Example 3 from text]" ([Speaker Name] - [MM:SS])
  - "[Example 4 from text]" ([Speaker Name] - [MM:SS])
  - "[Example 5 from text (Least frequent)]" ([Speaker Name] - [MM:SS])

* [Next Verb Tense/Structure Name]: [Brief explanation].
  - "[Example 1 from text (Most frequent)]" ([Speaker Name] - [MM:SS])
  - "[Example 2 from text]" ([Speaker Name] - [MM:SS])
  - "[Example 3 from text]" ([Speaker Name] - [MM:SS])
  - "[Example 4 from text]" ([Speaker Name] - [MM:SS])
  - "[Example 5 from text (Least frequent)]" ([Speaker Name] - [MM:SS])

### 2. Idiomatic Expressions & Phrasal Verbs
Extract any idioms, phrasal verbs, or natural collocations that a native speaker would use.
* [Expression/Phrasal Verb]: [Meaning and a quick tip on how to use it]
  - "[Example 1 from text (Most frequent)]" ([Speaker Name] - [MM:SS])
  - "[Example 2 from text]" ([Speaker Name] - [MM:SS])
  - "[Example 3 from text]" ([Speaker Name] - [MM:SS])
  - "[Example 4 from text]" ([Speaker Name] - [MM:SS])
  - "[Example 5 from text (Least frequent)]" ([Speaker Name] - [MM:SS])
* [Expression/Phrasal Verb]: [Meaning and a quick tip on how to use it]
  - "[Example 1 from text (Most frequent)]" ([Speaker Name] - [MM:SS])
  - "[Example 2 from text]" ([Speaker Name] - [MM:SS])
  - "[Example 3 from text]" ([Speaker Name] - [MM:SS])
  - "[Example 4 from text]" ([Speaker Name] - [MM:SS])
  - "[Example 5 from text (Least frequent)]" ([Speaker Name] - [MM:SS])

### 3. Advanced or Key Vocabulary
Highlight 3 to 5 key vocabulary words that are crucial for understanding the text or are great for intermediate/advanced learners to know.
* [Word]: Definition: [Simple definition] | Synonym: [1-2 synonyms]
  - "[Example 1 from text (Most frequent)]" ([Speaker Name] - [MM:SS])
  - "[Example 2 from text]" ([Speaker Name] - [MM:SS])
  - "[Example 3 from text]" ([Speaker Name] - [MM:SS])
  - "[Example 4 from text]" ([Speaker Name] - [MM:SS])

### 4. Sentence Patterns for Practice
Select 2 interesting sentence structures from the text that I can use as a template to create my own sentences.
* Pattern 1: "[Original sentence]"
  * Template to mimic: [Show the skeleton of the sentence, e.g., "It is not only [X], but also [Y]"]
* Pattern 2: "[Original sentence]"
  * Template to mimic: [Show the skeleton of the sentence]

### 5. Quick Study Challenge
Give me 2 fill-in-the-blank sentences based on the text's vocabulary or grammar to test my understanding, followed by an "Answer Key" at the very bottom hidden or separated.
""")


_USER_PROMPT_TEMPLATE = "Here is the text to analyze:\n\n[TRANSCRIPT]\n{text}\n[TRANSCRIPT END]"


class LLMAnalyzerAdapter(AnalyzerPort):
    def __init__(self, api_key: str | None = None, model: str = "gpt-5.4-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise AnalysisError(
                "OPENAI_API_KEY not set. Provide api_key or set the "
                "OPENAI_API_KEY environment variable."
            )
        self.model = model
        self._client: OpenAI | None = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def analyze(self, text: str) -> LLMAnalysisResult:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": _USER_PROMPT_TEMPLATE.format(text=text)},
                ],
                temperature=0.3,
            )
        except Exception as exc:
            raise AnalysisError(f"LLM analysis failed: {exc}") from exc

        content = response.choices[0].message.content or ""
        return LLMAnalysisResult(markdown=content.strip())
