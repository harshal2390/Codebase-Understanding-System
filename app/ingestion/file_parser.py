import os
import ast
import re


class FileParser:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

        # Allowed file types
        self.allowed_extensions = [".py", ".js", ".ts"]

        # Ignore folders
        self.ignore_dirs = ["node_modules", ".git", "venv", "__pycache__"]

    # =========================
    # FILE COLLECTION
    # =========================
    def get_all_files(self):
        """
        Traverse repo and collect valid files
        """
        file_paths = []

        for root, dirs, files in os.walk(self.repo_path):
            # Remove ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]

            for file in files:
                if any(file.endswith(ext) for ext in self.allowed_extensions):
                    full_path = os.path.join(root, file)
                    file_paths.append(full_path)

        return file_paths

    # =========================
    # PYTHON PARSER
    # =========================
    def parse_python_file(self, file_path):
        """
        Extract functions, classes, imports from Python file
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            functions = []
            classes = []
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)

                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)

                elif isinstance(node, ast.Import):
                    for n in node.names:
                        imports.append(n.name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            return {
                "file": file_path,
                "functions": list(set(functions)),
                "classes": list(set(classes)),
                "imports": list(set(imports)),
                "content": content,
            }

        except Exception as e:
            print(f"[ERROR] Python parsing failed {file_path}: {e}")
            return None

    # =========================
    # JS/TS PARSER (REGEX BASED)
    # =========================
    def parse_js_file(self, file_path):
        """
        Basic JS/TS parsing using regex
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Function patterns
            functions = re.findall(r'function\s+(\w+)', content)

            # Arrow functions
            arrow_functions = re.findall(
                r'const\s+(\w+)\s*=\s*\(.*?\)\s*=>', content
            )

            # Classes
            classes = re.findall(r'class\s+(\w+)', content)

            # Imports (require)
            imports_require = re.findall(
                r'require\([\'"](.+?)[\'"]\)', content
            )

            # Imports (ES6)
            imports_es6 = re.findall(
                r'import\s+.*?\s+from\s+[\'"](.+?)[\'"]', content
            )

            return {
                "file": file_path,
                "functions": list(set(functions + arrow_functions)),
                "classes": list(set(classes)),
                "imports": list(set(imports_require + imports_es6)),
                "content": content,
            }

        except Exception as e:
            print(f"[ERROR] JS parsing failed {file_path}: {e}")
            return None

    # =========================
    # MAIN PARSER
    # =========================
    def parse_files(self):
        """
        Parse all files in repo
        """
        all_files = self.get_all_files()
        parsed_data = []

        for file_path in all_files:

            if file_path.endswith(".py"):
                parsed = self.parse_python_file(file_path)
                if parsed:
                    parsed_data.append(parsed)

            elif file_path.endswith(".js") or file_path.endswith(".ts"):
                parsed = self.parse_js_file(file_path)
                if parsed:
                    parsed_data.append(parsed)

        return parsed_data