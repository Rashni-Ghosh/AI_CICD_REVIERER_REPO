from pathlib import Path

ALLOWED_EXTENSIONS = {
    ".py",
    ".yml",
    ".yaml",
    ".json",
    ".js",
    ".ts",
    ".java",
    ".go",
    ".txt",
}

ALLOWED_FILENAMES = {
    "Dockerfile",
    "dockerfile",
}

def scan_repository(repo_path: str):
    repository = Path(repo_path)
    files = []

    for file_path in repository.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.name in ALLOWED_FILENAMES:
            files.append(str(file_path))
            continue

        if file_path.suffix.lower() in ALLOWED_EXTENSIONS:
            files.append(str(file_path))

    return files