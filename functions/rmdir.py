import os

from google.genai import types


def rmdir(working_directory, directory_path):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_path = os.path.normpath(os.path.join(working_dir_abs, directory_path))

        valid_target_path = os.path.commonpath([working_dir_abs, target_path]) == working_dir_abs
        if not valid_target_path:
            return (
                f'Error: Cannot remove "{directory_path}" as it is outside the permitted working directory'
            )

        if not os.path.isdir(target_path):
            return f'Error: "{directory_path}" does not exist or is not a directory'

        os.rmdir(target_path)
        return f'Successfully removed directory "{directory_path}"'
    except Exception as exc:
        return f"Error: {exc}"

schema_rmdir = types.FunctionDeclaration(
    name="rmdir",
    description="Removes a directory relative to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the directory to remove, relative to the working directory",
            )
        },
        required=["directory_path"],
    ),
)
