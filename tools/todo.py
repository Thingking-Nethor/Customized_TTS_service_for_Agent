'''
一个简单的命令行待办事项管理器
支持添加、查看、完成和删除任务
'''

import json
import os
from datetime import datetime

TODO_FILE = "todos. json"

def load_todos():
    """!从文件加载待办事项"""
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            return json. load(f)
    return []

def save_todos(todos):
    """保存待办事项到文件"""
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2, ensure_ascii=False)

def show_todos(todos):
    """显示所有待办事项"""
    if not todos:
        print("\n 待办列表是空的!\n")
        return

    print("\n" + "=" * 50)
    print("■ 待办事项列表")
    print("=" * 50)
    for i, todo in enumerate(todos, 1):
        status = "" if todo.get("done") else "O"
        print(f" {status} {i}. {todo['title' ]}")
        if todo.get("note"):
            print(f"    {todo['note' ]} ")
        print(f"    {todo ['created' ]} ")
    print("=" * 50 + "\n")
