import os

from google.genai import types

from config import MAX_CHARS

def write_file(working_directory, file_path, content):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_path = os.path.normpath(os.path.join(working_dir_abs, file_path))

        valid_target_path = os.path.commonpath([working_dir_abs, target_path]) == working_dir_abs
        if not valid_target_path:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        if os.path.isdir(target_path):
            return f'Error: Cannot write to "{file_path}" as it is a directory.'
        
        with open(target_path, "w", encoding="utf-8") as file_handle:
            file_handle.write(content)
        
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    
    except Exception as exc:
        return f"Error: {exc}"


schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes or overwrites a file relative to the working directory with the provided content",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to write, relative to the working directory",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Text content to write to the file",
            ),
        },
        required=["file_path", "content"],
    ),
)
