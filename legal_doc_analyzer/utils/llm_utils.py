# llm_utils.py

import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def call_llm(prompt: str, model: str = "gpt-4", temperature: float = 0.3, max_tokens: int = 300) -> str:
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"LLM call failed: {e}")
        return ""
