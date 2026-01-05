import os
import argparse
from dotenv import load_dotenv
from google import genai

def main():
    
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    args = parser.parse_args()
    
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        raise RuntimeError("No API key found")


    client = genai.Client(api_key=api_key)

  
    prompt = args.user_prompt

    response = client.models.generate_content(
        model='gemini-2.5-flash', contents=prompt
    )

    usage = response.usage_metadata
    if usage is None:
        raise RuntimeError("No usage metadata returned from API response")

    prompt_tokens = usage.prompt_token_count
    response_tokens = getattr(usage, "response_token_count", None)
    if response_tokens is None:
        response_tokens = usage.candidates_token_count
    if prompt_tokens is None or response_tokens is None:
        raise RuntimeError("Usage metadata missing token counts")

    print(prompt)
    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Response tokens: {response_tokens}")
    print("Response:")
    print(response.text)
    
main()
