from config import MAX_CHARS
from functions.get_file_content import get_file_content

content = get_file_content("calculator", "lorem.txt")
truncation_message = f'[...File "lorem.txt" truncated at {MAX_CHARS} characters]'
assert content.endswith(truncation_message)
assert len(content) == MAX_CHARS + len(truncation_message)
print("Truncation test passed.")

print(get_file_content("calculator", "main.py"))
print(get_file_content("calculator", "pkg/calculator.py"))
print(get_file_content("calculator", "/bin/cat"))
print(get_file_content("calculator", "pkg/does_not_exist.py"))
