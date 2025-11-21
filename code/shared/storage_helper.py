import os

class StorageHelper:
    @staticmethod
    def save_to_file(content, file_path):
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"StorageHelper: Saved file to {file_path}")
        except Exception as e:
            print(f"StorageHelper: Failed to save file - {e}")

    @staticmethod
    def read_from_file(file_path):
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            print(f"StorageHelper: Read file from {file_path}")
            return content
        except Exception as e:
            print(f"StorageHelper: Failed to read file - {e}")
            return None
