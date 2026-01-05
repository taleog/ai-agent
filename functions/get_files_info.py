import os

def get_files_info(working_directory, directory="."):
    working_dir_abs = os.path.abspath(working_directory)
    target_dir = os.path.normpath(os.path.join(working_dir_abs, directory))

    valid_target_dir = os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs
    
    files_info = []
    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)
        files_info.append({
            'name': item,
            'file_size': os.path.getsize(item_path),
            'is_dir': os.path.isdir(item_path)
        })
    if directory == ".":
        print("Result for current directory:")
        for item in files_info:
            print(f"  - {item['name']}: file_size={item['file_size']} bytes, is_dir={item['is_dir']}")
        print(" ")
    elif not valid_target_dir:
        print(f"Result for '{directory}' directory:")
        print(f'  Error: Cannot list "{directory}" as it is outside the permitted working directory')
        print(" ")
    else:
        print(f"Result for '{directory}' directory:")
        for item in files_info:
            print(f"  - {item['name']}: file_size={item['file_size']} bytes, is_dir={item['is_dir']}")
        print(" ")

  