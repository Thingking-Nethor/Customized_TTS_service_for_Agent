import asyncio
<<<<<<< HEAD
import atexit
=======
import signal
>>>>>>> eece9ea (连接远程仓库)
from ui.conversation_ui import ConversationWindow
from dotenv import load_dotenv
from dotenv import set_key
import json
import os
from pydantic_ai import Agent
from pydantic_ai.messages import ModelRequest, ModelResponse, UserPromptPart, TextPart
from queue import Queue
import re
import subprocess
<<<<<<< HEAD
=======
import sys
>>>>>>> eece9ea (连接远程仓库)
from threading import Thread
import time
import tools.tools as tools
import voice.output.customized_voice_service as cvs

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
with open(f"characters//{config['system']['character_name']}//conversation_style_prompt.txt", "r", encoding="utf-8") as f:
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

# 初始化参考音频和提示文本的索引
ref_audio_path_and_prompt_text_index: int = 0
text0: Queue[str] = Queue()
if tts_service_enabled:
    streamer = cvs.TTSStreamer(config["tts"]["voice_config_filename"])  #根据需要替换为你的配置文件名（json文件，不带扩展名）
    print("✅ TTS服务配置加载完成")
else:
    print("⚠️ TTS服务未启用")
    config["tts"]["tts_service"] = False

def update_index(i: int) -> None:
    """
    请根据需要写入代表语气的参数i，来更新ref_audio_path_and_prompt_text_index的值
    0为默认语气，1为开心，2为生气，3为伤心，4为惊讶，5为厌恶，6为恐惧
    难以归类就用默认语气（0）
    """
    tone_map: dict[int, str] = {0: "默认", 1: "开心", 2: "生气", 3: "伤心", 4: "惊讶", 5: "厌恶", 6: "恐惧"}
    if i < 0:
        return
    if i > 6:
        i = 0
    else:
        r = len(streamer.json["ref_audio_path_list"])
        p = len(streamer.json["prompt_text_list"])
        if r < 7 or p < 7:
            if min(r, p) <= i:
                i = 0
    global ref_audio_path_and_prompt_text_index
    ref_audio_path_and_prompt_text_index = i
    print("切换到语气：", tone_map.get(i))

def load_history_from_logs(max_rounds: int, user_name: str, character_name: str) -> list:
    """从logs目录加载历史对话，最多返回max_rounds轮（按时间正序）"""
    if not os.path.exists("logs"):
        return []

    log_files = sorted(
        [f for f in os.listdir("logs") if f.endswith(".txt")],
        reverse=True,
    )

    rounds: list[tuple[str, str]] = []
    for log_file in log_files:
        with open(os.path.join("logs", log_file), "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        i = 0
        while i + 1 < len(lines):
            user_line = lines[i]
            agent_line = lines[i + 1]
            if user_line.startswith(f"{user_name}: ") and agent_line.startswith(f"{character_name}: "):
                user_msg = user_line[len(f"{user_name}: "):]
                agent_msg = agent_line[len(f"{character_name}: "):]
                rounds.append((user_msg, agent_msg))
                i += 2
            else:
                i += 1

        if len(rounds) >= max_rounds:
            break

    rounds = rounds[:max_rounds][::-1]  # 取最新的N轮，反转为时间正序

    messages: list = []
    for user_msg, agent_msg in rounds:
        messages.append(ModelRequest(parts=[UserPromptPart(content=user_msg)]))
        messages.append(ModelResponse(parts=[TextPart(content=agent_msg)]))
    return messages


def check():
    """检查必要的文件和目录是否存在，如果不存在则创建或提示用户"""
    os.path.exists("logs") or os.mkdir("logs")
    if not os.path.exists("config.json"):
        with open("config.json.example", "r", encoding="utf-8") as f:
            config_example = f.read()
            config_example = re.sub(r"#.*", "", config_example)
            config_example = re.sub(r" ", "", config_example)    #去掉注释行和空格，生成默认的config.json
        with open("config.json", "w", encoding="utf-8") as f:
            f.write(config_example)
        print("⚠️ 未找到config.json，已创建默认配置文件")

<<<<<<< HEAD
def _cleanup_tts():
    """程序退出时关闭TTS子进程窗口"""
    tts_api_process.terminate()
atexit.register(_cleanup_tts)
=======
def _cleanup_tts(signal, frame):
    """程序退出时关闭TTS子进程窗口"""
    tts_api_process.terminate()
    sys.exit(0)
>>>>>>> eece9ea (连接远程仓库)

def main():
    max_history_rounds: int = config["api"].get("max_history_rounds", 50)
    history: list = load_history_from_logs(
        max_history_rounds,
        config["system"]["user_name"],
        config["system"]["character_name"],
    )
    if history:
        print(f"✅ 已加载 {len(history) // 2} 轮历史对话")

    try:
        conv_win = ConversationWindow(config["system"]["character_name"], on_send=None,
                                     user_name=config["system"]["user_name"],
                                     opacity=config.get("window", {}).get("opacity", 1.0))
        conv_win.add_agent_prefix()
        conv_win.add_agent_chunk(f"我是{config['system']['character_name']}。\n")
        print("✅ 对话窗口创建成功")
    except Exception as e:
        print(f"❌ 无法创建对话窗口: {e}")
        return

    def handle_input(user_input: str):
<<<<<<< HEAD
=======
        '''处理用户输入，调用语言模型代理生成回复，
        并将回复文本流式显示在对话窗口中，同时发送给TTS服务进行语音合成'''
>>>>>>> eece9ea (连接远程仓库)
        nonlocal history
        global ref_audio_path_and_prompt_text_index
        ref_audio_path_and_prompt_text_index = 0
        accumulated: str = ""
        full_response_chunks: list[str] = []
        conv_win.add_agent_prefix()
        result = agent.run_stream_sync(user_input, message_history=history)
<<<<<<< HEAD
=======
        # 在接收模型回复的流式增量结果时，实时将文本显示在对话窗口中，并在文本切分后发送给TTS服务进行语音合成
>>>>>>> eece9ea (连接远程仓库)
        for chunk in result.stream_text(delta=True):
            conv_win.add_agent_chunk(chunk)
            accumulated += chunk
            full_response_chunks.append(chunk)
            while True:
                m: re.Match[str] | None = re.search(r'[。！？；…….?!\n]', accumulated)
                if m is None:
<<<<<<< HEAD
=======
                    if accumulated.strip() and tts_service_enabled:
                        streamer._push_text(accumulated.strip())
                        accumulated = ""
>>>>>>> eece9ea (连接远程仓库)
                    break
                idx = m.end()
                sentence = accumulated[:idx].strip()
                accumulated = accumulated[idx:]
                if sentence and tts_service_enabled:
                    streamer._push_text(sentence)
<<<<<<< HEAD
=======
        # 对话结束后将本轮对话加入历史，并保存到日志文件中
>>>>>>> eece9ea (连接远程仓库)
        history = list(result.all_messages())
        max_messages = max_history_rounds * 2
        if len(history) > max_messages:
            history = history[-max_messages:]
        timestamp: str = time.strftime("%Y-%m-%d", time.localtime())
<<<<<<< HEAD
=======
        # 将对话保存到logs目录下以日期命名的文本文件中
>>>>>>> eece9ea (连接远程仓库)
        os.makedirs("logs", exist_ok=True)
        with open(f"logs\\{timestamp}.txt", "a", encoding="utf-8") as f:
            f.write(f"{config['system']['user_name']}: {user_input}\n\n")
            f.write(f"{config['system']['character_name']}: {''.join(full_response_chunks)}\n\n")
        print(f"对话已保存到 logs\\{timestamp}.txt")
<<<<<<< HEAD
=======
        # 如果TTS服务启用但没有在对话中检测到任何标点符号，仍然需要将完整的回复文本发送给TTS服务进行合成
>>>>>>> eece9ea (连接远程仓库)
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
                      tools=[update_index, tools.open_spec_app, 
                             tools.read_file, tools.list_files, tools.rename_file, tools.file_list_dir])
        print("✅ 语言模型代理创建成功")
    except Exception as e:
        print(f"❌ 无法创建语言模型代理: {e}")
        exit(1)

    # 启动SoVITS-GPT服务（新命令行窗口）
    if tts_service_enabled and config["tts"].get("auto_start_GPT-SoVITS_api", False):
        try:
            tts_api_process = subprocess.Popen(
                f"{script_path}",
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
<<<<<<< HEAD
=======
            signal.signal(signal.SIGINT, _cleanup_tts)
>>>>>>> eece9ea (连接远程仓库)
            print("✅ TTS服务启动成功")
        except Exception as e:
            print(f"❌ 启动TTS服务失败: {e}")
            tts_service_enabled = False

    # 运行tts主程序
    if tts_service_enabled:
        Thread(target=asyncio.run, args=(streamer.generate_stream(),), daemon=True).start()
    check()
<<<<<<< HEAD
    main()
=======
    main()
>>>>>>> eece9ea (连接远程仓库)
