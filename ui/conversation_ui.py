import tkinter as tk
from tkinter import scrolledtext
from queue import Queue
from typing import Callable


class ConversationWindow:
    """带输入框的对话窗口（tkinter 必须在主线程运行）"""

    def __init__(self, character_name: str, on_send: Callable[[str], None], user_name: str = "User"):
        self.character_name = character_name
        self.user_name = user_name
        self.on_send = on_send
        self.queue: Queue = Queue()
        self._streaming = True
        self._start_ui()

    def _start_ui(self):
        self.root = tk.Tk()
        self.root.title(f"对话窗口 - {self.character_name}")
        self.root.geometry("700x550")
        self.root.configure(bg="#1e1e1e")

        # 对话显示区域
        self.text_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            font=("Consolas", 11),
            state=tk.DISABLED,
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 0))

        self.text_area.tag_config("user", foreground="#569cd6", font=("Consolas", 11, "bold"))
        self.text_area.tag_config("agent", foreground="#d4d4d4")
        self.text_area.tag_config("agent_name", foreground="#4ec9b0", font=("Consolas", 11, "bold"))

        # 底部输入栏
        input_frame = tk.Frame(self.root, bg="#252526")
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        self.entry = tk.Entry(
            input_frame,
            bg="#3c3c3c",
            fg="#d4d4d4",
            insertbackground="white",
            font=("Consolas", 11),
            relief=tk.FLAT,
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)

        send_btn = tk.Button(
            input_frame,
            text="发送",
            command=self._on_send_clicked,
            bg="#0e639c",
            fg="white",
            font=("Microsoft YaHei", 10),
            relief=tk.FLAT,
            padx=12,
        )
        send_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # 按 Enter 发送消息
        self.entry.bind("<Return>", lambda e: self._on_send_clicked())

        # 关闭窗口时退出
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._poll_queue()

    def _on_send_clicked(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self.add_user_input(text)
        self.on_send(text)

    def _on_close(self):
        self.root.quit()

    def _poll_queue(self):
        try:
            while True:
                tag, text = self.queue.get_nowait()
                self.text_area.configure(state=tk.NORMAL)
                self.text_area.insert(tk.END, text, tag)
                self.text_area.see(tk.END)
                self.text_area.configure(state=tk.DISABLED)
        except Exception:
            pass
        self.root.after(50, self._poll_queue)

    def add_user_input(self, text: str):
        self.queue.put(("user", f"\n{self.user_name}: {text}\n"))

    def add_agent_chunk(self, chunk: str):
        self.queue.put(("agent", chunk))

    def add_agent_prefix(self):
        self.queue.put(("agent_name", f"\n{self.character_name}: "))

    def run(self):
        self.root.mainloop()
