# AI Agent with Gemini and Function Calling

This project implements an AI agent capable of interacting with users, understanding their prompts, and executing various tools (functions) to fulfill requests. It leverages the Google Gemini API, specifically `gemini-2.5-flash`, to enable multi-turn conversations and dynamic tool use.

This repo was made by following along the course from boot.dev, and this README was written with the tool itself to test its capabilities.

## Features

*   **Gemini API Integration**: Utilizes the `gemini-2.5-flash` model for intelligent conversational abilities.
*   **Function Calling**: The agent can dynamically call predefined Python functions based on user prompts, enabling it to perform actions like listing files, reading content, executing scripts, and writing files.
*   **Multi-turn Conversations**: Supports ongoing interactions, maintaining context across multiple exchanges.
*   **Verbose Output**: An optional verbose mode provides detailed insights into the agent's thought process, including token usage and function call details.
*   **Extensible Toolset**: Easily add new functions to `call_function.py` to expand the agent's capabilities.

## Setup

To get this project up and running, follow these steps:

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Install dependencies**:
    We recommend using `uv` for dependency management.
    ```bash
    uv pip install .
    ```

3.  **Set up your Gemini API Key**:
    Obtain a Gemini API key from the Google AI Studio. Create a `.env` file in the root directory of the project and add your API key:
    ```
    GEMINI_API_KEY=YOUR_API_KEY_HERE
    ```

## Usage

Run the agent from the command line with a user prompt.

```bash
python main.py "Your prompt here"
```

### Examples:

*   **List files in the current directory (verbose mode)**:
    ```bash
    python main.py "List the files in the current directory." --verbose
    ```

*   **Read the content of a file**:
    ```bash
    python main.py "What is in main.py?"
    ```

*   **Perform a calculation (if a calculator tool is available)**:
    ```bash
    python main.py "What is 5 + 3 * 2?"
    ```

## Project Structure

*   `main.py`: The main entry point for the AI agent, handling argument parsing, API interaction, and conversation flow.
*   `call_function.py`: Contains the logic for defining and calling available tools (functions) that the AI agent can use.
*   `prompts.py`: Stores the system prompt that guides the AI's behavior and persona.
*   `.env`: (Not committed) Stores your `GEMINI_API_KEY`.
*   `README.md`: This file.
