import os
import argparse
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types
from call_function import available_functions, call_function
from prompts import system_prompt
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.pretty import Pretty
from rich.syntax import Syntax
from rich.table import Table
from rich.theme import Theme

DEFAULT_MEMORY_FILE = ".agent_memory.txt"
MAX_MEMORY_CHARS = 2000
MAX_DISPLAY_CHARS = 4000
SUMMARY_PROMPT = """
You are updating a running memory for a coding agent.
Summarize only the durable, useful context: user goals, preferences, important files, and notable actions.
Keep it concise (under 200 words) and avoid large code blocks or tool output dumps.
If there is nothing important to add, return the previous memory unchanged.
"""

THEME = Theme(
    {
        "user": "bold cyan",
        "agent": "bold green",
        "tool": "yellow",
        "muted": "dim",
        "error": "bold red",
        "success": "green",
    }
)
CONSOLE = Console(theme=THEME)

def load_memory(path):
    try:
        with open(path, "r", encoding="utf-8") as file_handle:
            return file_handle.read().strip()
    except FileNotFoundError:
        return ""


def save_memory(path, memory_text):
    with open(path, "w", encoding="utf-8") as file_handle:
        file_handle.write(memory_text.strip() + "\n")


def build_system_instruction(memory_text):
    if not memory_text:
        return system_prompt
    return f"{system_prompt}\n\n## Memory\n{memory_text}"


def update_memory(client, previous_memory, prompt, final_text, tool_calls, verbose):
    tool_calls_block = "None"
    if tool_calls:
        tool_calls_block = "\n".join(f"- {call}" for call in tool_calls)

    summary_input = (
        "Previous memory:\n"
        f"{previous_memory or '(empty)'}\n\n"
        "New interaction:\n"
        f"User: {prompt}\n"
        f"Tools called:\n{tool_calls_block}\n"
        f"Assistant: {final_text or '(no final response)'}\n\n"
        "Updated memory:"
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=summary_input,
        config=types.GenerateContentConfig(system_instruction=SUMMARY_PROMPT),
    )

    new_memory = (response.text or "").strip()
    if not new_memory:
        new_memory = previous_memory

    if len(new_memory) > MAX_MEMORY_CHARS:
        new_memory = new_memory[:MAX_MEMORY_CHARS].rstrip() + "..."

    if verbose:
        print("Memory updated.")

    return new_memory


def parse_files_info(output):
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if not lines:
        return None, []

    title = lines[0]
    rows = []
    for line in lines[1:]:
        if line.startswith("- "):
            line = line[2:]
        match = re.match(
            r"(.+): file_size=(\d+) bytes, is_dir=(True|False)$", line
        )
        if not match:
            continue
        name, size, is_dir = match.groups()
        rows.append((name, int(size), is_dir == "True"))
    return title, rows


def guess_lexer(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    return {
        ".py": "python",
        ".md": "markdown",
        ".toml": "toml",
        ".json": "json",
        ".txt": "text",
    }.get(ext, "text")


def render_tool_call(console, function_name, args, verbose):
    if verbose:
        console.print(
            Panel(Pretty(args or {}), title=f"Tool call: {function_name}", style="tool")
        )
    else:
        console.print(f"[muted]- Tool:[/muted] [tool]{function_name}[/tool]")


def render_files_info(console, output):
    if "Error:" in output:
        console.print(Panel(output.strip(), title="get_files_info", style="error"))
        return

    title, rows = parse_files_info(output)
    if not rows:
        console.print(Panel(output.strip(), title="get_files_info"))
        return

    table = Table(title=title or "Files", box=box.ROUNDED)
    table.add_column("Name", overflow="fold")
    table.add_column("Size", justify="right")
    table.add_column("Type")
    for name, size, is_dir in rows:
        table.add_row(name, f"{size} B", "dir" if is_dir else "file")
    console.print(table)


def render_file_content(console, args, output):
    file_path = (args or {}).get("file_path", "file")
    if output.startswith("Error:"):
        console.print(Panel(output.strip(), title=file_path, style="error"))
        return

    display = output
    if len(display) > MAX_DISPLAY_CHARS:
        display = display[:MAX_DISPLAY_CHARS].rstrip() + "\n...[display truncated]"

    lexer = guess_lexer(file_path)
    syntax = Syntax(display, lexer, theme="monokai", word_wrap=True)
    console.print(Panel(syntax, title=file_path))


def render_run_python_file(console, output):
    if output.startswith("Error:"):
        console.print(Panel(output.strip(), title="run_python_file", style="error"))
        return

    console.print(Panel(output.strip(), title="run_python_file"))


def render_write_file(console, output):
    style = "success" if output.startswith("Successfully") else "error"
    console.print(Panel(output.strip(), title="write_file", style=style))


def render_tool_result(console, function_name, args, response, verbose):
    if response is None:
        console.print(Panel("No response from tool.", title=function_name, style="error"))
        return

    if "error" in response:
        console.print(Panel(str(response["error"]), title=function_name, style="error"))
        return

    result = response.get("result", "")
    if function_name == "get_files_info":
        render_files_info(console, result)
    elif function_name == "get_file_content":
        render_file_content(console, args, result)
    elif function_name == "run_python_file":
        render_run_python_file(console, result)
    elif function_name == "write_file":
        render_write_file(console, result)
    else:
        console.print(Panel(str(result).strip(), title=function_name))

    if verbose:
        console.print(Panel(Pretty(response), title="Tool response", style="muted"))


def render_agent_response(console, text):
    if not text:
        console.print(Panel("No response.", title="Agent", style="error"))
        return
    console.print(Panel(Markdown(text), title="Agent", border_style="agent"))


def main():
    
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", nargs="?", help="User prompt")
    parser.add_argument("--chat", action="store_true", help="Start an interactive session")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--memory-file", default=DEFAULT_MEMORY_FILE, help="Path to the memory file")
    parser.add_argument("--no-memory", action="store_true", help="Disable loading/saving memory")
    parser.add_argument("--reset-memory", action="store_true", help="Clear memory before starting")
    args = parser.parse_args()
    
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        raise RuntimeError("No API key found")


    client = genai.Client(api_key=api_key)

    if not args.chat and not args.user_prompt:
        parser.error("user_prompt is required unless --chat is set")

    memory_text = ""
    if not args.no_memory:
        if args.reset_memory:
            save_memory(args.memory_file, "")
        memory_text = load_memory(args.memory_file)

    def run_turn(user_prompt, memory_snapshot):
        messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]
        system_instruction = build_system_instruction(memory_snapshot)
        final_text, tool_calls = generate_content(
            client, user_prompt, messages, args.verbose, system_instruction, CONSOLE
        )
        render_agent_response(CONSOLE, final_text)
        if not args.no_memory:
            updated_memory = update_memory(
                client, memory_snapshot, user_prompt, final_text, tool_calls, args.verbose
            )
            save_memory(args.memory_file, updated_memory)
            return updated_memory
        return memory_snapshot

    if args.chat:
        CONSOLE.print(
            Panel(
                "Ask questions about the repo or request actions. Type 'exit' to quit.",
                title="AI Agent",
                border_style="agent",
            )
        )
        while True:
            try:
                user_prompt = CONSOLE.input("[user]You>[/user] ").strip()
            except EOFError:
                break

            if not user_prompt or user_prompt.lower() in {"exit", "quit"}:
                break

            memory_text = run_turn(user_prompt, memory_text)
            CONSOLE.print()
    else:
        memory_text = run_turn(args.user_prompt, memory_text)
    

def generate_content(client, prompt, messages, verbose, system_instruction, console):
    if verbose:
        console.print(f"[muted]User prompt:[/muted] {prompt}")

    tool_calls_log = []
    for _ in range(20):
        with console.status("[muted]Thinking...[/muted]", spinner="dots"):
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=messages,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
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
            console.print(f"[muted]Prompt tokens:[/muted] {prompt_tokens}")
            console.print(f"[muted]Response tokens:[/muted] {response_tokens}")

        candidates = response.candidates or []
        for candidate in candidates:
            if candidate.content:
                messages.append(candidate.content)

        function_calls = response.function_calls
        if function_calls:
            function_results = []
            for function_call_item in function_calls:
                tool_calls_log.append(
                    f"{function_call_item.name}({function_call_item.args})"
                )
                render_tool_call(
                    console, function_call_item.name or "", function_call_item.args, verbose
                )
                function_call_result = call_function(function_call_item, verbose=verbose)
                if not function_call_result.parts:
                    raise RuntimeError("Function call result missing parts")

                function_response = function_call_result.parts[0].function_response
                if function_response is None:
                    raise RuntimeError("Function response missing")

                if function_response.response is None:
                    raise RuntimeError("Function response missing data")

                function_results.append(function_call_result.parts[0])
                render_tool_result(
                    console,
                    function_call_item.name or "",
                    function_call_item.args,
                    function_response.response,
                    verbose,
                )

            if function_results:
                messages.append(types.Content(role="user", parts=function_results))

            continue

        return response.text, tool_calls_log

    console.print(
        Panel(
            "Error: maximum iterations reached without a final response.",
            title="Agent",
            style="error",
        )
    )
    raise SystemExit(1)
    
main()
