from openai import OpenAI
import re
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
    api_key=os.getenv("DEEPSEEK_API_KEY")
)

def clean_response(text):
    # 1. Remove reasoning block
    cleaned = re.sub(r"<think>.*?</think>\s*", "", text, flags=re.DOTALL)

    # 2. Remove bold intro tags like "**Fact Check:**"
    cleaned = re.sub(r"^\*\*[^*]+\*\*[:\-]?\s*", "", cleaned.strip(), flags=re.IGNORECASE)

    # 3. Convert **bold** and *bold* to HTML <b>...</b>
    cleaned = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", cleaned)
    cleaned = re.sub(r"\*(.+?)\*", r"<b>\1</b>", cleaned)

    return cleaned.strip()

def fact_check_input():
    while True:
        user_input = input("\n🔍 Enter a statement to fact-check (or 'exit' to quit):\n> ")
        if user_input.lower() in {"exit", "quit"}:
            print("👋 Exiting.")
            break

        print("\n⏳ Fact-checking...\n")

        completion = client.chat.completions.create(
            model="deepseek-ai/deepseek-r1",
            messages=[
                {"role": "user", "content": f"Fact-check this statement in a clear, user-friendly way, but do NOT include your reasoning or thinking process: {user_input}"}
            ],
            temperature=0.6,
            top_p=0.7,
            max_tokens=4096,
            stream=True
        )

        full_response = ""
        for chunk in completion:
            delta = chunk.choices[0].delta.content
            if delta:
                full_response += delta

        # Clean the response
        cleaned = clean_response(full_response)
        print("✅ Fact-Checked Response:\n" + cleaned.strip())

if __name__ == "__main__":
    fact_check_input()