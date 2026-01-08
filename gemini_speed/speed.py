from google import genai
from google.genai import types
import base64
import os
import time

client = genai.Client(
    vertexai=True,
    location="us-central1"
)

MODEL = "gemini-2.5-flash"
#MODEL  = "gemini-3-flash-preview"

def generate_test_prompt():
    # 1. Input Token 늘리기 (약 4000 토큰 목표)
    # 영어 기준 1 토큰 ≈ 4 char. 4000 토큰 ≈ 16,000 char
    # 반복되는 문장을 사용하여 길이를 채웁니다.
    base_sentence = "This is a test sentence to fill up the input context window for performance testing. "
    
    # base_sentence는 약 85자(약 20~25토큰). 
    # 4000 토큰을 채우기 위해 약 180~200번 반복
    long_context = base_sentence * 247 

    # 2. Output Token 줄이기 (약 50 토큰 목표)
    # 모델에게 매우 짧은 요약이나 특정 단어 추출을 지시합니다.
    instruction = (
        "\n\n[Instruction]\n"
        "Ignore the repeated text above. "
        "Just tell me the 'base sentence' used above once, and explain why it was repeated in one short sentence. "
        "Keep the total response under 200 words."
    )
    
    return long_context + instruction

def generate(content):

  system_prompt=""

  contents = [
    types.Content(
      role="user",
      parts=[
        types.Part.from_text(text=content)
      ]
    )
  ]

  generate_content_config = types.GenerateContentConfig(
    system_instruction=system_prompt,
    max_output_tokens=180,
    temperature=0.0,
    top_p=1.0,
    #responseJsonSchema=ParseResponse.schema(),
        safety_settings = [types.SafetySetting(
      category="HARM_CATEGORY_HATE_SPEECH",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_DANGEROUS_CONTENT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_HARASSMENT",
      threshold="OFF"
    )],

    thinking_config=types.ThinkingConfig(
      thinking_budget=0,
    ),

  )

  completion = client.models.generate_content(
        model=MODEL,
        config=generate_content_config,
        contents=contents
        )
  return completion

def main():
    prompt = generate_test_prompt()
    print("Prompt Length:", len(prompt))
    
    elapsed_times = []
    
    for i in range(20):
        start_time = time.time()
        response = generate(prompt)
        end_time = time.time()
        
        elapsed = end_time - start_time
        elapsed_times.append(elapsed)
        
        print(f"Iteration {i+1}: {response.usage_metadata.prompt_token_count} input tokens, {response.usage_metadata.total_token_count - response.usage_metadata.prompt_token_count} output tokens : {elapsed:.4f} seconds")
        #print(response)
        print("-" * 20)

    avg_time = sum(elapsed_times) / len(elapsed_times)
    print(f"Average Elapsed Time: {avg_time:.4f} seconds")

if __name__ == "__main__":
    main()