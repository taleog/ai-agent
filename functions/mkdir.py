import os
from google.genai import types

def mkdir(directory_path: str) -> dict:
    """Creates a new directory at the specified path.

    Args:
        directory_path: The path of the directory to create.
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return {"success": f"Directory '{directory_path}' created successfully."}
    except OSError as e:
        return {"error": f"Error creating directory '{directory_path}': {e}"}

schema_mkdir = types.Tool.FunctionDeclaration(
    name="mkdir",
    description="Creates a new directory at the specified path.",
    parameters=types.Tool.FunctionDeclaration.Schema(
        type=types.Tool.FunctionDeclaration.Schema.Type.OBJECT,
        properties={
            "directory_path": types.Tool.FunctionDeclaration.Schema(
                type=types.Tool.FunctionDeclaration.Schema.Type.STRING,
                description="The path of the directory to create.",
            )
        },
        required=["directory_path"],
    ),
)