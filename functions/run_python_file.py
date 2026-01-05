import os
import subprocess


def run_python_file(working_directory, file_path, args=None):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_path = os.path.normpath(os.path.join(working_dir_abs, file_path))

        valid_target_path = os.path.commonpath([working_dir_abs, target_path]) == working_dir_abs
        if not valid_target_path:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(target_path):
            return f'Error: "{file_path}" does not exist or is not a regular file'

        if not file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        command = ["python", target_path]
        if args:
            command.extend(args)

        result = subprocess.run(
            command,
            cwd=working_dir_abs,
            capture_output=True,
            text=True,
            timeout=30,
        )

        output_parts = []
        if result.returncode != 0:
            output_parts.append(f"Process exited with code {result.returncode}")

        stdout = result.stdout
        stderr = result.stderr

        if not stdout and not stderr:
            output_parts.append("No output produced")
        else:
            if stdout:
                output_parts.append(f"STDOUT: {stdout}")
            if stderr:
                output_parts.append(f"STDERR: {stderr}")

        return "\n".join(output_parts)
    except Exception as exc:
        return f"Error: executing Python file: {exc}"
