import os

from google.genai import types

def get_files_info(working_directory, directory="."):
    working_dir_abs = os.path.abspath(working_directory)
    target_dir = os.path.normpath(os.path.join(working_dir_abs, directory))

    valid_target_dir = os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs
    
    lines = []
    if not valid_target_dir:
        lines.append(f"Result for '{directory}' directory:")
        lines.append(f'  Error: Cannot list "{directory}" as it is outside the permitted working directory')
    else:
        files_info = []
        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            files_info.append({
                'name': item,
                'file_size': os.path.getsize(item_path),
                'is_dir': os.path.isdir(item_path)
            })

        if directory == ".":
            lines.append("Result for current directory:")
        else:
            lines.append(f"Result for '{directory}' directory:")

        for item in files_info:
            lines.append(
                f"  - {item['name']}: file_size={item['file_size']} bytes, is_dir={item['is_dir']}"
            )

    lines.append("")
    output = "\n".join(lines)
    return output

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)
