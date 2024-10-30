import os

def exists_directory(directory: str):
    if not os.path.isdir(directory):
        print(f'{directory} directory does not exist')
        return False
    return True