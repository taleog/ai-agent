# AI Agent CLI

A polished, tool-using CLI agent powered by Gemini. It plans, calls tools, and iterates until it has a final answer, with a premium terminal UI and persistent memory to keep context across sessions.

## Highlights

- Rich terminal UI with panels, tables, syntax highlighting, and spinners.
- Multi-turn tool loop (plan → call tools → observe → answer).
- Persistent memory (`.agent_memory.txt`) to continue conversations over time.
- Built-in toolset for file IO, Python execution, and directory management.
- Verbose mode for debugging tokens, tool calls, and tool responses.
- Safety: tool calls are scoped to a working directory you control.

## Quickstart

1) Install dependencies:
```bash
uv sync
```

2) Add your API key:
```bash
echo 'GEMINI_API_KEY=your_key_here' > .env
```

3) Run the agent:
```bash
uv run main.py "read main.py"
```

Or start a chat session:
```bash
uv run main.py --chat
```

## Usage

```bash
uv run main.py "list files in the root"
uv run main.py --chat
uv run main.py "read main.py" --verbose
uv run main.py "..." --no-memory
uv run main.py --reset-memory
uv run main.py --memory-file /tmp/agent_memory.txt
```

### Tools Available to the Agent

- `get_files_info(directory)` — list files and sizes.
- `get_file_content(file_path)` — read file contents (auto-truncated for safety).
- `write_file(file_path, content)` — write/overwrite a file.
- `run_python_file(file_path, args)` — execute a Python file with optional args.
- `mkdir(directory_path)` — create a directory.
- `rmdir(directory_path)` — remove a directory.

## How It Works

The agent runs a loop:
1) The model decides what tool(s) to call.
2) The program executes those tools.
3) Tool results are fed back into the conversation.
4) The model returns a final response once it has enough info.

Memory is summarized after each completed turn and injected into the system prompt on the next run so the agent can pick up where it left off.

## Safety & Configuration

Tool calls are sandboxed to a working directory defined in `call_function.py` (`working_directory` is set to `.` by default). Change this if you want to restrict the agent to a subfolder (for example, `./calculator`).

Be cautious when running the agent with write or execute permissions, as it can modify or run code on your machine.

---

Built while following the Boot.dev course, then extended with a polished UI and memory features.
