import asyncio
from collections.abc import Iterable
from fastapi import FastAPI
import json
import re
import subprocess
# from system.config import AgentConfig as config
from threading import Thread
import uvicorn
from voice.output.customized_voice_service import TTSStreamer

tts_service = FastAPI()
with open("config.json", "r", encoding="utf-8") as f:
    config: dict[str, dict[str, str|bool]] = json.load(f)

@tts_service.get("/")
def echo() -> dict[str, str]:
    return {"message": "TTS API Server is running."}

@tts_service.get("/text={text}")
def generate_tts(text: str) -> dict[str, str]:
    """接收文本并生成语音"""
    global streamer
    # 使用 lookbehind 在分隔符后切分，保留分隔符在句子末尾
    sentences: list[str] = re.split(r'(?<=[。！？；…….?!\n])', text)

    if not sentences:
        return {"message": "文本已接收，但未检测到完整句子。"}

    try:
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:  # 确保不发送空句子
                streamer._push_text(sentence)
    except Exception as e:
        print(f"❌ 发送文本到TTS服务失败: {e}")
    return {"message": "文本已接收并发送给TTS服务。"}

if __name__ == "__main__":
    try:
        tts_api_process = subprocess.Popen(
            r"tools\go_api_v2.bat",
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        # 非阻塞检查进程是否立即退出（启动失败）
        import time
        time.sleep(1)
        if tts_api_process.poll() is not None and config["tts"]["auto_start_GPT-SoVITS_api"]:
            stdout: bytes
            stderr: bytes
            stdout, stderr = tts_api_process.communicate()
            print(f"❌ TTS外部服务启动失败 (exit code: {tts_api_process.returncode})")
            if stderr:
                print(f"stderr:\n{stderr}")
            if stdout:
                print(f"stdout:\n{stdout}")
        else:
            print("✅ TTS外部服务启动成功")
    except Exception as e:
        print(f"❌ 启动TTS服务失败: {e}")
    #根据需要替换为你的配置文件名（json文件，不带扩展名）
    streamer: TTSStreamer = TTSStreamer(config["tts"]["voice_config_filename"])
    Thread(target=asyncio.run, args=(streamer.generate_stream(),), daemon=True).start()
    uvicorn.run(tts_service, host="127.0.0.1", port=8997)
