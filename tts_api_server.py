import asyncio
from fastapi import FastAPI
import os
import re
import requests
from signal import signal, SIGINT, CTRL_BREAK_EVENT
import subprocess
import sys
from system.config import AgentConfig, load_config, load_tts_config
import time
# from system.config import AgentConfig as config
from threading import Thread
import uvicorn
from voice.output.customized_voice_service import TTSStreamer

tts_service = FastAPI()
config: AgentConfig = load_config()

@tts_service.get("/")
def echo() -> dict[str, str]:
    return {"message": "TTS API Server is running."}

@tts_service.get("/text={text}")
def generate_tts(text: str) -> dict[str, str]:
    """接收文本并生成语音"""
    global streamer
    # 使用 lookbehind 在分隔符后切分，保留分隔符在句子末尾
    sentences: list[str] = re.split(r'(?<=[。！？；?!\n])|(?<=……)|(?<=\. )', text)

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

def close_tts_terminate(signal, frame) -> None:
    print("正在关闭tts终端……")
    global tts_api_process
    if 'tts_api_process' in globals():
        if os.name == 'nt':
            tts_api_process.send_signal(CTRL_BREAK_EVENT)
        else:
            tts_api_process.send_signal(SIGINT)
        tts_api_process.terminate()
    sys.exit(0)

if __name__ == "__main__":
    signal(SIGINT, close_tts_terminate)
    streamer: TTSStreamer = TTSStreamer(load_tts_config())
    try:  # 推理服务已启用时不重复启动
        try:
            init_request = requests.post(
                    url=streamer.url,
                    data=streamer.params.model_dump_json(),
                    headers={"Content-Type":"application/json"},
                    timeout=3)
            del init_request
        except (requests.ConnectionError, requests.exceptions.Timeout):
            if config.tts.auto_start_GPT_SoVITS_api:
                tts_api_process: subprocess.Popen[bytes] = subprocess.Popen(
                    args=r"tools\go_api_v2.bat",
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                )
                # 非阻塞检查进程是否立即退出（启动失败）
                time.sleep(1)
                if tts_api_process.poll():
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
                    while True:
                        try:
                            init_request = requests.post(
                                url=streamer.url,
                                data=streamer.params.model_dump_json(),
                                headers={"Content-Type":"application/json"})  # 发送初始请求以初始化Bert
                        except requests.exceptions.ConnectionError:
                            print("推理端未完全启动，等待3秒")
                            time.sleep(3)
                        else:
                            print(f"✅ 发送初始请求成功，Bert已初始化: {init_request.status_code}")
                            del init_request
                            break
        else:
            print('✅ 使用外部TTS服务')
    except Exception as e:
        print(f"❌ 启动TTS服务失败: {e}")
    Thread(target=asyncio.run, args=(streamer.generate_stream(),), daemon=True).start()
    uvicorn.run(tts_service, host="127.0.0.1", port=8997)
