import os
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from call_function import available_functions, call_function
from prompts import system_prompt

def main():
    
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        raise RuntimeError("No API key found")


    client = genai.Client(api_key=api_key)
    prompt = args.user_prompt
    messages = [types.Content(role="user", parts=[types.Part(text=prompt)])]
    generate_content(client, prompt, messages, args.verbose)
    

def generate_content(client, prompt, messages, verbose):
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=messages,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=[available_functions],
        ),
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
    
    if verbose:
        print(f"User prompt: {prompt}")
        print(f"Prompt tokens: {prompt_tokens}")
        print(f"Response tokens: {response_tokens}")

    function_calls = response.function_calls
    if function_calls:
        function_results = []
        for function_call_item in function_calls:
            function_call_result = call_function(function_call_item, verbose=verbose)
            if not function_call_result.parts:
                raise RuntimeError("Function call result missing parts")

            function_response = function_call_result.parts[0].function_response
            if function_response is None:
                raise RuntimeError("Function response missing")

            if function_response.response is None:
                raise RuntimeError("Function response missing data")

            function_results.append(function_call_result.parts[0])

            if verbose:
                print(f"-> {function_response.response}")
    else:
        print(response.text)
    
main()
