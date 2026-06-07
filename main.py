import asyncio
import atexit
from ui.conversation_ui import ConversationWindow
from dotenv import load_dotenv
from dotenv import set_key
import json
import os
from pydantic_ai import Agent
from queue import Queue
import re
import subprocess
from threading import Thread
import time
import voice.customized_voice_service as cvs

load_dotenv()

# 检查config.json是否被修改过，如果被修改过则更新.env中的CONFIG_MODIFICATION_TIMESTAMP的值
if os.path.getmtime("config.json") > float(os.getenv("CONFIG_MODIFICATION_TIMESTAMP", "0")):
    set_key(".env", "CONFIG_MODIFICATION_TIMESTAMP", str(os.path.getmtime("config.json")))
    config_changed: bool = True
else:
    config_changed: bool = False
print("✅ 主配置文件修改情况检查完毕")

# 从config.json中读取配置项，并根据需要启动TTS服务
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
tts_service_enabled: bool = config["tts"].get("tts_service", False)
print("✅ 主配置文件加载完成")
with open(f"characters//{config['character_name']}//conversation_style_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()
print("✅ 系统提示词加载完成")

script_path = os.path.join(os.path.dirname(__file__), 'tools', 'go_api_v2.bat')

# 改写go_api_v2.bat中的路径参数为config中指定的GPT-SoVITS目录路径
if config_changed and tts_service_enabled:
    with open(script_path, "r", encoding="utf-8") as f:
        go_api_script_content = f.read()
        go_api_script_content = re.sub(
            r'/d ".*?"',
            lambda _: f'/d "{config["tts"]["GPT-SoVITS_directory_path"]}"',
            go_api_script_content,
        )
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(go_api_script_content)
        del go_api_script_content
print("✅ TTS服务脚本路径参数检查并更新完成")

ref_audio_path_index: int = 0
prompt_text_index: int = 0
text0: Queue[str] = Queue()
if tts_service_enabled:
    streamer = cvs.TTSStreamer(config["voice_config_filename"])  #根据需要替换为你的配置文件名（json文件，不带扩展名）
print("✅ TTS服务配置加载完成")

def update_index(i: int) -> None:
    """
    请根据需要写入代表语气的参数i，来更新ref_audio_path_index和prompt_text_index的值
    0为默认语气，1为开心，2为生气，3为伤心，4为惊讶，5为厌恶，6为恐惧
    """
    tone_map: dict[int, str] = {0: "默认", 1: "开心", 2: "生气", 3: "伤心", 4: "惊讶", 5: "厌恶", 6: "恐惧"}
    if i < 0:
        return
    if i > 6:
        i = 0
    else:
        r = len(streamer.cvs.json["ref_audio_path_list"])
        p = len(streamer.cvs.json["prompt_text_list"])
        if r < 7 or p < 7:
            if min(r, p) <= i:
                i = 0
    global ref_audio_path_index, prompt_text_index
    ref_audio_path_index, prompt_text_index = i, i
    print("切换到语气：", tone_map.get(i))

def run_tts_async():
    asyncio.run(streamer.generate_stream())

def check():
    os.path.exists("logs") or os.mkdir("logs")
    if not os.path.exists("config.json"):
        with open("config.json.example", "r", encoding="utf-8") as f:
            config_example = f.read()
            config_example = re.sub(r"#.*", "", config_example)
            config_example = re.sub(r" ", "", config_example)    #去掉注释行和空格，生成默认的config.json
        with open("config.json", "w", encoding="utf-8") as f:
            f.write(config_example)
        print("⚠️ 未找到config.json，已创建默认配置文件")

def _cleanup_tts():
    """程序退出时关闭TTS子进程窗口"""
    tts_api_process.terminate()
atexit.register(_cleanup_tts)

def main():
    history: list = []
    global ref_audio_path_index, prompt_text_index
    
    try:
        conv_win = ConversationWindow(config["character_name"], on_send=None, user_name=config["user_name"])
        conv_win.add_agent_prefix()
        conv_win.add_agent_chunk(f"你好！我是{config['character_name']}。\n")
        print("✅ 对话窗口创建成功")
    except Exception as e:
        print(f"❌ 无法创建对话窗口: {e}")
        return

    def handle_input(user_input: str):
        nonlocal history
        global ref_audio_path_index, prompt_text_index
        ref_audio_path_index, prompt_text_index = 0, 0
        accumulated = ""
        full_response_chunks: list[str] = []
        conv_win.add_agent_prefix()
        result = agent.run_stream_sync(user_input, message_history=history)
        for chunk in result.stream_text(delta=True):
            conv_win.add_agent_chunk(chunk)
            accumulated += chunk
            full_response_chunks.append(chunk)
            while True:
                m = re.search(r'[。！？；…….?!\n]', accumulated)
                if not m:
                    break
                idx = m.end()
                sentence = accumulated[:idx].strip()
                accumulated = accumulated[idx:]
                if sentence and tts_service_enabled:
                    streamer._push_text(sentence)
        history = list(result.all_messages())
        timestamp: str = time.strftime("%Y-%m-%d", time.localtime())
        os.makedirs("logs", exist_ok=True)
        with open(f"logs\\{timestamp}.txt", "a", encoding="utf-8") as f:
            f.write(f"User: {user_input}\n\n")
            f.write(f"{config['character_name']}: {''.join(full_response_chunks)}\n\n")
        print(f"对话已保存到 logs\\{timestamp}.txt")
        if accumulated.strip() and tts_service_enabled:
            streamer._push_text(accumulated.strip())

    def on_send(user_input: str):
        Thread(target=handle_input, args=(user_input,), daemon=True).start()

    conv_win.on_send = on_send
    conv_win.run()

if __name__ == "__main__":
    try:
        agent = Agent(model="deepseek:deepseek-v4-flash", name="Dandelion",
                      description="An agent that does something useful.",
                      system_prompt=system_prompt,
                      tools=[update_index])
        print("✅ 语言模型代理创建成功")
    except Exception as e:
        print(f"❌ 无法创建语言模型代理: {e}")
        exit(1)

    # 启动TTS服务（新命令行窗口）
    if tts_service_enabled and config["tts"].get("auto_start_GPT-SoVITS_api", False):
        try:
            tts_api_process = subprocess.Popen(
                f"{script_path}",
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
            print("✅ TTS服务启动成功")
        except Exception as e:
            print(f"❌ 启动TTS服务失败: {e}")
            tts_service_enabled = False

    # 运行tts主程序
    if tts_service_enabled:
        Thread(target=run_tts_async, args=(), daemon=True).start()
    check()
    main()
