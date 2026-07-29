<<<<<<< HEAD
=======
import json
>>>>>>> eece9ea (连接远程仓库)
import tkinter as tk
from tkinter import scrolledtext
from queue import Queue
from typing import Callable


class ConversationWindow:
    """带输入框的对话窗口（tkinter 必须在主线程运行）"""

<<<<<<< HEAD
    def __init__(self, character_name: str, on_send: Callable[[str], None], user_name: str = "User"):
        self.character_name = character_name
        self.user_name = user_name
        self.on_send = on_send
=======
    def __init__(self, character_name: str, on_send: Callable[[str], None],
                 user_name: str = "User", opacity: float = 1.0):
        self.character_name = character_name
        self.user_name = user_name
        self.on_send = on_send
        self.opacity = opacity
>>>>>>> eece9ea (连接远程仓库)
        self.queue: Queue = Queue()
        self._streaming = True
        self._start_ui()

    def _start_ui(self):
        self.root = tk.Tk()
        self.root.title(f"对话窗口 - {self.character_name}")
        self.root.geometry("700x550")
        self.root.configure(bg="#1e1e1e")
<<<<<<< HEAD
=======
        self.root.attributes("-alpha", self.opacity)
>>>>>>> eece9ea (连接远程仓库)

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

<<<<<<< HEAD
=======
        settings_btn = tk.Button(
            input_frame,
            text="设置",
            command=self._open_settings,
            bg="#3c3c3c",
            fg="#d4d4d4",
            font=("Microsoft YaHei", 10),
            relief=tk.FLAT,
            padx=12,
        )
        settings_btn.pack(side=tk.RIGHT, padx=(5, 0))

>>>>>>> eece9ea (连接远程仓库)
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

<<<<<<< HEAD
=======
    def _open_settings(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("设置")
        settings_win.geometry("360x180")
        settings_win.configure(bg="#2d2d2d")
        settings_win.resizable(False, False)
        settings_win.transient(self.root)
        settings_win.grab_set()

        # 居中于父窗口
        settings_win.update_idletasks()
        px = self.root.winfo_x() + (self.root.winfo_width() - 360) // 2
        py = self.root.winfo_y() + (self.root.winfo_height() - 180) // 2
        settings_win.geometry(f"+{px}+{py}")

        # 标题
        title_lbl = tk.Label(
            settings_win,
            text="窗口透明度",
            bg="#2d2d2d",
            fg="#d4d4d4",
            font=("Microsoft YaHei", 12, "bold"),
        )
        title_lbl.pack(pady=(20, 10))

        # 滑块框架
        slider_frame = tk.Frame(settings_win, bg="#2d2d2d")
        slider_frame.pack(fill=tk.X, padx=30)

        self.opacity_var = tk.DoubleVar(value=self.opacity)

        value_lbl = tk.Label(
            slider_frame,
            text=f"{self.opacity:.1f}",
            bg="#2d2d2d",
            fg="#4ec9b0",
            font=("Consolas", 14, "bold"),
            width=4,
        )
        value_lbl.pack()

        def on_slider_change(val):
            v = round(float(val), 1)
            self.opacity_var.set(v)
            value_lbl.config(text=f"{v:.1f}")
            self.root.attributes("-alpha", v)

        scale = tk.Scale(
            slider_frame,
            from_=0.3, to=1.0,
            orient=tk.HORIZONTAL,
            resolution=0.1,
            variable=self.opacity_var,
            command=on_slider_change,
            bg="#2d2d2d",
            fg="#d4d4d4",
            troughcolor="#3c3c3c",
            activebackground="#0e639c",
            highlightthickness=0,
            length=280,
        )
        scale.pack(pady=(5, 0))

        # 按钮框架
        btn_frame = tk.Frame(settings_win, bg="#2d2d2d")
        btn_frame.pack(pady=15)

        def save_and_close():
            new_opacity = round(self.opacity_var.get(), 1)
            self.opacity = new_opacity
            self._save_opacity_to_config(new_opacity)
            settings_win.destroy()

        cancel_btn = tk.Button(
            btn_frame,
            text="取消",
            command=settings_win.destroy,
            bg="#3c3c3c",
            fg="#d4d4d4",
            font=("Microsoft YaHei", 10),
            relief=tk.FLAT,
            padx=16,
        )
        cancel_btn.pack(side=tk.LEFT, padx=(0, 10))

        save_btn = tk.Button(
            btn_frame,
            text="保存",
            command=save_and_close,
            bg="#0e639c",
            fg="white",
            font=("Microsoft YaHei", 10),
            relief=tk.FLAT,
            padx=16,
        )
        save_btn.pack(side=tk.LEFT)

    def _save_opacity_to_config(self, opacity: float):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            config.setdefault("window", {})["opacity"] = opacity
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

>>>>>>> eece9ea (连接远程仓库)
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
