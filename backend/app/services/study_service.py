"""Study content and quiz generation service."""

from __future__ import annotations

import json
import re
from typing import Any

from ..adapters.pipeline_adapter import PipelineAdapter


class StudyService:
    def __init__(self, pipeline_adapter: PipelineAdapter) -> None:
        self._pipeline_adapter = pipeline_adapter

    def generate_study_material(
        self,
        user_id: str,
        database_id: str,
        topic_name: str,
    ) -> dict[str, Any]:
        """Generate study content and quiz for a topic within a community database."""

        # Step 1: Retrieve relevant chunks via semantic search
        results = self._pipeline_adapter.semantic_search(
            user_id=user_id,
            query=topic_name,
            top_k=10,
            database_id=database_id,
        )

        if not results:
            return {
                "study_content": f"No content found for the topic **{topic_name}**. Please try a different topic.",
                "quiz": [],
            }

        # Build context from chunks
        context_blocks = []
        for idx, chunk in enumerate(results, start=1):
            text = chunk.get("chunk_text", "")
            source = chunk.get("file_name", "unknown")
            context_blocks.append(f"[{idx}] Source: {source}\n{text}")

        context_text = "\n\n".join(context_blocks)

        # Step 2: Get LLM config
        base_config = self._pipeline_adapter._base_config
        query_cfg = base_config.get("query", {})
        llm_backend = str(query_cfg.get("llm_backend", "groq"))
        llm_model = str(query_cfg.get("llm_model", "llama-3.1-8b-instant"))
        groq_api_key = str(query_cfg.get("groq_api_key", ""))
        gemini_api_key = str(query_cfg.get("gemini_api_key", ""))

        # Step 3: Generate study content
        study_content = self._generate_study_content(
            topic_name=topic_name,
            context=context_text,
            backend=llm_backend,
            model=llm_model,
            groq_api_key=groq_api_key,
            gemini_api_key=gemini_api_key,
        )

        # Step 4: Generate quiz
        quiz = self._generate_quiz(
            topic_name=topic_name,
            context=context_text,
            backend=llm_backend,
            model=llm_model,
            groq_api_key=groq_api_key,
            gemini_api_key=gemini_api_key,
        )

        return {
            "study_content": study_content,
            "quiz": quiz,
        }

    def _generate_study_content(
        self,
        topic_name: str,
        context: str,
        backend: str,
        model: str,
        groq_api_key: str,
        gemini_api_key: str,
    ) -> str:
        prompt = f"""You are an expert educational content writer. Based on the provided context, write a comprehensive study document about "{topic_name}".

## Instructions
- Write detailed, well-structured educational content covering ALL key concepts from the context.
- Use clear headings (## and ###) to organize sections.
- Write in a tutorial/textbook style that helps students learn.
- Include definitions, explanations, examples, and key takeaways.
- Make the content thorough — at least 5-8 paragraphs covering different aspects.
- Use bullet points and numbered lists where appropriate.
- Stay grounded in the provided context — do NOT add information not present in the sources.
- Make it engaging and easy to understand.

## Context
{context}

## Study Document for: {topic_name}
"""
        return self._call_llm(prompt, backend, model, groq_api_key, gemini_api_key)

    def _generate_quiz(
        self,
        topic_name: str,
        context: str,
        backend: str,
        model: str,
        groq_api_key: str,
        gemini_api_key: str,
    ) -> list[dict[str, Any]]:
        prompt = f"""You are an expert quiz maker. Based on the provided context about "{topic_name}", create exactly 7 multiple-choice questions.

## Instructions
- Create 7 MCQ questions that test understanding of the key concepts.
- Each question should have exactly 4 options (A, B, C, D).
- Only ONE option should be correct per question.
- Questions should range from basic recall to deeper understanding.
- Stay grounded in the provided context.
- Return ONLY a valid JSON array with no additional text.

## Required JSON format
[
  {{
    "question": "What is...?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0
  }}
]

Where correct_answer is the 0-based index of the correct option.

## Context
{context}

## JSON array of 7 MCQ questions:
"""
        raw = self._call_llm(prompt, backend, model, groq_api_key, gemini_api_key)

        # Parse JSON from the response
        try:
            match = re.search(r"\[.*\]", raw, re.DOTALL)
            if match:
                quiz = json.loads(match.group())
                if isinstance(quiz, list):
                    # Validate structure
                    valid = []
                    for q in quiz:
                        if (
                            isinstance(q, dict)
                            and "question" in q
                            and "options" in q
                            and "correct_answer" in q
                            and isinstance(q["options"], list)
                            and len(q["options"]) == 4
                            and isinstance(q["correct_answer"], int)
                            and 0 <= q["correct_answer"] <= 3
                        ):
                            valid.append({
                                "question": str(q["question"]),
                                "options": [str(o) for o in q["options"]],
                                "correct_answer": int(q["correct_answer"]),
                            })
                    return valid
        except (json.JSONDecodeError, ValueError):
            pass

        return []

    def _call_llm(
        self,
        prompt: str,
        backend: str,
        model: str,
        groq_api_key: str,
        gemini_api_key: str,
    ) -> str:
        """Route LLM call to the configured backend."""
        if backend == "groq":
            return self._call_groq(prompt, model, groq_api_key)
        elif backend == "gemini":
            return self._call_gemini(prompt, model, gemini_api_key)
        elif backend == "ollama":
            return self._call_ollama(prompt, model)
        else:
            raise RuntimeError(f"Unknown LLM backend: {backend}")

    def _call_groq(self, prompt: str, model: str, api_key: str) -> str:
        from openai import OpenAI

        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful educational assistant. Provide thorough, well-structured content."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content or ""

    def _call_gemini(self, prompt: str, model: str, api_key: str) -> str:
        from google import genai

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "system_instruction": "You are a helpful educational assistant. Provide thorough, well-structured content.",
            },
        )
        return response.text or ""

    def _call_ollama(self, prompt: str, model: str) -> str:
        import ollama

        result = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful educational assistant. Provide thorough, well-structured content."},
                {"role": "user", "content": prompt},
            ],
        )
        return result.get("message", {}).get("content", "")
