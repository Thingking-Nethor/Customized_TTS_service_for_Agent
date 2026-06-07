import asyncio
from fastapi import FastAPI
import json
import re
from system.config import AgentConfig as config
from threading import Thread
import uvicorn
import voice.output.customized_voice_service as cvs

tts_service = FastAPI()
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

@tts_service.get("/")
def echo():
    return {"message": "TTS API Server is running."}

@tts_service.get("/text={text}")
def generate_tts(text: str):
    """接收文本并生成语音"""
    global streamer
    m: re.Match[str] | None = re.search(r'[。！？；…….?!\n]', text)
    if m is None:
        if text.strip() and config["tts"]["tts_service"]:
            try:
                streamer._push_text(text.strip())
            except Exception as e:
                print(f"❌ 发送文本到TTS服务失败: {e}")
        return {"message": "文本已接收，但未检测到完整句子。"}
    idx = m.end()
    sentence = text[:idx].strip()
    text = text[idx:]
    try:
        if sentence :
            streamer._push_text(sentence)
        if text.strip():
            streamer._push_text(text.strip())
    except Exception as e:
        print(f"❌ 发送文本到TTS服务失败: {e}")
    return {"message": "文本已接收并发送给TTS服务。"}

if __name__ == "__main__":
    #根据需要替换为你的配置文件名（json文件，不带扩展名）
    streamer = cvs.TTSStreamer(config["tts"]["voice_config_filename"])
    Thread(target=asyncio.run, args=(streamer.generate_stream(),), daemon=True).start()
    uvicorn.run(tts_service, host="127.0.0.1", port=8997)
