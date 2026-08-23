# config.py - 简化配置系统
"""
Agent 配置系统 - 基于Pydantic实现类型安全和验证
支持配置热更新和变更通知
"""
import os
import sys
import json
import re
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # Python < 3.11 fallback
from pathlib import Path
from datetime import datetime
from typing import NoReturn

from pydantic import BaseModel, Field, field_validator, ConfigDict

IS_PACKAGED: bool = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def get_version() -> str:
    """从 pyproject.toml 读取版本号（唯一版本源）。
    开发环境从项目根目录读取，PyInstaller 打包后从 _MEIPASS 读取。
    """
    if IS_PACKAGED:
        pyproject = Path(sys._MEIPASS) / "pyproject.toml"
    else:
        pyproject = Path(os.getcwd()).resolve() / "pyproject.toml"
    try:
        with open(pyproject, "rb") as f:
            return tomllib.load(f)["project"]["version"]
    except Exception:
        return "0.0.0"


def _get_root_dir() -> Path:
    """返回项目根目录"""
    if IS_PACKAGED:
        return Path(sys._MEIPASS)
    return Path(os.getcwd()).resolve()


# ============================================================
# Pydantic 配置模型
# ============================================================

class SystemConfig(BaseModel):
    """系统基础配置"""
    character_name: str = Field(default="", description="角色名称")
    user_name: str = Field(default="", description="用户名称")


class ApiConfig(BaseModel):
    """LLM API 配置"""
    base_url: str = Field(default="", description="API 基础地址，空字符串使用默认 DeepSeek 服务")
    api_key: str = Field(default="", description="API 密钥，空字符串从 .env 读取")
    model: str = Field(default="", description="模型名称，空字符串使用默认模型")
    max_history_rounds: int = Field(default=10, ge=1, description="最大保留的历史对话轮数")

    @field_validator("max_history_rounds", mode="before")
    @classmethod
    def _ensure_positive(cls, v: int) -> int:
        if v < 1:
            return 10
        return v


class TtsBasicConfig(BaseModel):
    """TTS 语音合成基础配置"""
    tts_service: bool = Field(default=True, description="是否启用 TTS 语音服务")
    voice_config_filename: str = Field(default="config", description="语音具体配置文件名，不含扩展名")
    auto_start_GPT_SoVITS_api: bool = Field(default=True, description="是否自动启动 GPT-SoVITS API")
    GPT_SoVITS_directory_path: str = Field(default="", description="GPT-SoVITS 根目录路径")


class PostParams(BaseModel):
    """POST请求参数"""
    text: str = Field(default="Hello world!")
    text_lang: str = Field(default="zh")
    ref_audio_path: str = Field(default="")
    aux_ref_audio_paths: list = Field(default=[])
    prompt_text: str = Field(default="")
    prompt_lang: str = Field(default="all_ja")
    top_k: float = Field(default=5)
    top_p: float = Field(default=1 )
    temperature: float = Field(default=1)
    text_split_method: str = Field(default="cut0")
    batch_size: int = Field(default=1)
    batch_threshold: float = Field(default=0.75)
    split_bucket: bool = Field(default=True)
    speed_factor: float = Field(default=1.0)
    streaming_mode: bool = Field(default=False)
    seed: float = Field(default=-1)
    parallel_infer: bool = Field(default=True)
    repetition_penalty: float = Field(default=1.35)
    sample_steps: int = Field(default=32)
    super_sampling: bool = Field(default=False)


class TtsConfig(BaseModel):
    """TTS 语音合成具体配置"""
    name: str = Field(default="config")
    text_sign: str = Field(default="${text}")
    curl: str = Field(default="http://127.0.0.1:9880/tts")
    params: PostParams = Field(default_factory=PostParams)
    variable_ref_audio_and_prompt_text: bool = Field(default=False)
    ref_audio_path_list: list[str] = Field(default_factory=list)
    prompt_text_list: list[str] = Field(default_factory=list)
    filter_brackets: bool = Field(default=True)
    filter_special_chars: bool = Field(default=True)
    output_frequency: int = Field(default=44100)
    output_channels: int = Field(default=1, gt=0, lt=3)
    output_size: int = Field(default=-16)
    save_audio: bool = Field(default=False)
    output_path: str = Field(default="")
    
    model_config = ConfigDict(extra='forbid')


class SttConfig(BaseModel):
    """STT 语音识别配置（暂未上线）"""
    stt_service: bool = Field(default=True, description="是否启用 STT 语音识别服务")
    base_url: str = Field(default="http://", description="STT API 地址")
    api_key: str = Field(default="", description="STT API 密钥")
    model: str = Field(default="whisper-1", description="STT 模型名称")


class WindowConfig(BaseModel):
    """对话窗口配置"""
    opacity: float = Field(default=0.9, ge=0.3, le=1.0, description="窗口透明度，0.3~1.0")


class AgentConfig(BaseModel):
    """Agent 完整配置"""
    system: SystemConfig = Field(default_factory=SystemConfig, description="系统基础配置")
    api: ApiConfig = Field(default_factory=ApiConfig, description="API 配置")
    tts: TtsBasicConfig = Field(default_factory=TtsBasicConfig, description="TTS 配置")
    stt: SttConfig = Field(default_factory=SttConfig, description="STT 配置")
    window: WindowConfig = Field(default_factory=WindowConfig, description="窗口配置")
    
    model_config = ConfigDict(extra='forbid')


# ============================================================
# 配置加载 / 保存
# ============================================================

def _strip_json_comments(text: str) -> str:
    """去除 JSON 中的行内注释（// 和 # 风格）"""
    result: list[str] = []
    for line in text.splitlines():
        in_string = False
        stripped = ""
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == '"' and (i == 0 or line[i - 1] != '\\'):
                in_string = not in_string
                stripped += ch
            elif not in_string and ch == '#' and (i == 0 or line[i - 1] == ' ' or line[i - 1] == '\t'):
                break  # 行内注释，丢弃剩余部分
            elif not in_string and i + 1 < len(line) and ch == '/' and line[i + 1] == '/':
                break  # // 注释
            else:
                stripped += ch
            i += 1
        result.append(stripped)
    return "\n".join(result)


def load_config() -> AgentConfig:
    """加载主配置文件。
    优先从 config.json 读取，不存在时从 config.json.example 生成默认配置。
    """
    root = _get_root_dir()
    config_path = root / "config.json"

    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            raw = f.read()
        return AgentConfig.model_validate_json(json_data=raw)
    else:
        print(f"警告：配置文件 {config_path} 不存在，使用默认配置")

    # 回退到示例配置
    example_path = root / "config.json.example"
    if example_path.exists():
        return load_example_config()
    return AgentConfig()


def load_example_config() -> AgentConfig:
    """从 config.json.example 加载默认配置"""
    root = _get_root_dir()
    example_path = root / "config.json.example"
    with open(example_path, "r", encoding="utf-8") as f:
        raw = f.read()
    raw = _strip_json_comments(raw)
    return AgentConfig.model_validate_json(json_data=raw)


def load_tts_config(base_config: AgentConfig | str | None = None) -> TtsConfig | NoReturn:
    """加载tts具体配置文件。
    优先从 output/config/config.json 读取，不存在时从 output/config/config.json.example 生成默认配置。
    """
    root = _get_root_dir()
    if isinstance(base_config, AgentConfig):
        character: str = base_config.tts.voice_config_filename
    elif isinstance(base_config, str):
        character: str = base_config
    else:
        config_path = root / "config.json"
        with open(config_path, "r", encoding="utf-8") as f:
            raw: str = f.read()
        character: str = json.loads(raw)["tts"]["voice_config_filename"]
    tts_config_path: Path = root / f"voice/output/config/{character}.json"

    if tts_config_path.exists():
        with open(tts_config_path, "r", encoding="utf-8") as f:
            tts_raw = f.read()
        data: dict = json.loads(tts_raw)
        return TtsConfig(name=character, **data)
    else:
        raise ValueError(f"警告：配置文件 {tts_config_path} 不存在，请检查配置")


def save_config(config: AgentConfig, config_path: str | Path | None = None) -> None:
    """保存配置到文件"""
    root = _get_root_dir()
    if config_path is None:
        config_path = root / "config.json"
    else:
        config_path = Path(config_path)
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config.model_dump_json(indent=4, ensure_ascii=False))


def create_default_config_if_missing() -> bool:
    """如果 config.json 不存在，从示例配置创建。
    返回 True 表示创建了新文件。
    """
    root = _get_root_dir()
    config_path = root / "config.json"
    if config_path.exists():
        return False
    cfg = load_example_config()
    save_config(cfg, config_path)
    return True


# ============================================================
# 变更检测
# ============================================================

def get_config_mtime() -> float:
    """获取 config.json 的修改时间，不存在返回 0"""
    config_path = _get_root_dir() / "config.json"
    if config_path.exists():
        return os.path.getmtime(config_path)
    return 0.0


def is_config_changed(last_mtime: float) -> bool:
    """检查配置文件是否自 last_mtime 后被修改"""
    return get_config_mtime() > last_mtime


# ============================================================
# 全局单例
# ============================================================

_config: AgentConfig | None = None
_config_mtime: float = 0.0


def get_config(reload: bool = False) -> AgentConfig:
    """获取全局配置单例。
    设置 reload=True 强制重新从文件加载。
    """
    global _config, _config_mtime
    current_mtime = get_config_mtime()
    if _config is None or reload or current_mtime > _config_mtime:
        _config = load_config()
        _config_mtime = current_mtime
    return _config


def reset_config() -> None:
    """重置全局配置缓存"""
    global _config, _config_mtime
    _config = None
    _config_mtime = 0.0
