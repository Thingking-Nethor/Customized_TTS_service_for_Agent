from pathlib import Path
from typing import Any
import subprocess
import os

base_dir = Path("./test_zone")

def read_file(name: str) -> str:
    """Return file content. If the file does not exist, return an error message."""
    print(f"Reading file: {name}")
    try:
        with open(base_dir / name, "r") as f:
            content: str = f.read()
        return content
    except Exception as e:
        return f"An error occurred: {e}"

def list_files() -> list[str]:
    print("Listing files ")
    file_list: list[Any] = []
    for item in base_dir.rglob("*"):
        if item.is_file():
            file_list.append(item.name)
    return file_list

def rename_file(old_name: str, new_name: str) -> str:
    print(f"Renaming file from {old_name} -> {new_name}")
    try:
        old_path: Path = base_dir / old_name
        new_path: Path = base_dir / new_name
        if not old_path.exists():
            return f"File {old_name} does not exist."
        if new_path.exists():
            return f"File {new_name} already exists."
        os.rename(old_path, new_path)
        return f"File renamed from {old_name} to {new_name} successfully."
    except Exception as e:
        return f"An error occurred: {e}"

def file_list_dir(dir: Path) -> dict[str, Any]:
    """List files in the specified directory."""
    if not dir.exists() or not dir.is_dir():
        return {f"Directory {dir} does not exist or is not a directory."}
    print(f"Listing files in directory: {dir}")
    try:
        return [item.name for item in dir.iterdir() if item.is_file()]
    except Exception as e:
        return {f"An error occurred: {e}"}

def open_spec_app(app_name: str) -> str:
    """
    Open the specified application.
    Here are the application names you can only use:
    - "cc-switch": Opens the CC-Switch application.
    - "追放": Opens the GF2_Exilium game.
    """
    app_path_list: dict[str] = {
        "cc-switch": "D:\\Program Files\\CC-Switch\\cc-switch.exe",
        "追放": "D:\\Program Files\\GF2_Exilium\\Games\\GF2_Exilium.exe"
        }
    print(f"Attempting to open specified application: {app_name}")
    try:
        subprocess.Popen([app_path_list[app_name]],
                        creationflags=subprocess.CREATE_NEW_CONSOLE)
        return f"{app_name} opened successfully."
    except Exception as e:
        return f"An error occurred while opening {app_name}: {e}"