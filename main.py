import base64
import time
import urllib.parse
import logging
from fastapi import FastAPI, Response, Request
from fastapi.responses import JSONResponse, HTMLResponse
from openai import OpenAI
import uvicorn
from jinja2 import Environment, FileSystemLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
env = Environment(loader=FileSystemLoader("templates"))
env.cache = None

VOICES = {
    # v2.5 TTS 音色（默认冰糖）
    "冰糖": "冰糖-活泼女声",
    "mimo_default": "MiMo-默认",
    "茉莉": "茉莉-温柔女声",
    "苏打": "苏打-清新男声",
    "白桦": "白桦-知性男声",
    "Mia": "Mia-英文女声",
    "Chloe": "Chloe-英文女声",
    "Milo": "Milo-英文男声",
    "Dean": "Dean-英文男声",
    # v2 TTS 音色（兼容）
    "default_zh": "MiMo-中文女声",
    "default_en": "MiMo-英文女声",
}

# 可用模型列表
TTS_MODELS = {
    "v2.5": "mimo-v2.5-tts",
    "v2.5_clone": "mimo-v2.5-tts-voiceclone",
    "v2.5_design": "mimo-v2.5-tts-voicedesign",
    "v2": "mimo-v2-tts",
}


@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)


@app.get("/")
async def index_page(request: Request):
    base_url = str(request.base_url).replace("http://", "https://").rstrip("/")
    options_html = "".join(
        [f'<option value="{k}">{v}</option>' for k, v in VOICES.items()]
    )
    template = env.get_template("index.jinja2")
    html = template.render(
        request=request, base_url=base_url, options_html=options_html
    )
    return HTMLResponse(content=html)


@app.api_route("/tts", methods=["GET", "POST"])
async def tts_forwarder(request: Request):
    if request.method == "POST":
        body = await request.json()
        api_key = body.get("api_key", "")
        text = body.get("text", "")
        voice = body.get("voice", "冰糖")
        model = body.get("model", "v2.5")
        audio_b64 = body.get("audio", "")
    else:
        api_key = request.query_params.get("api_key", "")
        text = request.query_params.get("text", "")
        voice = request.query_params.get("voice", "冰糖")
        model = request.query_params.get("model", "v2.5")
        audio_b64 = request.query_params.get("audio", "")
        text = urllib.parse.unquote(urllib.parse.unquote(text))
        audio_b64 = urllib.parse.unquote(urllib.parse.unquote(audio_b64))

    # 获取实际模型名称
    model_name = TTS_MODELS.get(model, TTS_MODELS["v2.5"])

    try:
        client = OpenAI(api_key=api_key, base_url="https://api.xiaomimimo.com/v1")
        
        # 根据不同模型构建请求
        if model == "v2.5_clone" and audio_b64:
            # VoiceClone: voice 格式是 data:audio/mpeg;base64,{base64}
            voice_data = f"data:audio/mpeg;base64,{audio_b64}"
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "assistant", "content": text},
                ],
                audio={"format": "wav", "voice": voice_data},
                stream=False,
            )
        elif model == "v2.5_design":
            # VoiceDesign: user 消息是音色描述，assistant 消息是要朗读的文本
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": voice},  # voice 是音色描述
                    {"role": "assistant", "content": text},  # text 是要朗读的文本
                ],
                audio={"format": "mp3"},
                stream=False,
            )
        else:
            # v2.5 内置音色 或 v2
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "assistant", "content": text},
                ],
                audio={"format": "mp3", "voice": voice},
                stream=False,
            )
        
        # 提取音频数据
        result_b64 = response.choices[0].message.audio.data
        audio_bytes = base64.b64decode(result_b64)
        
        # VoiceClone 返回 wav，其他返回 mp3
        media_type = "audio/wav" if model == "v2.5_clone" else "audio/mpeg"

        return Response(
            content=audio_bytes,
            media_type=media_type,
            headers={
                "Content-Length": str(len(audio_bytes)),
                "Cache-Control": "max-age=3600",
            },
        )
        
    except Exception as e:
        logger.error(f"TTS Error: {type(e).__name__}: {e}")
        return Response(status_code=502, content=f"上游API错误: {type(e).__name__}")


@app.get("/api/legado-import")
async def legado_import(request: Request, voice: str = "冰糖", model: str = "v2.5"):
    api_key = request.query_params.get("api_key", "")
    base_url = str(request.base_url).replace("http://", "https://").rstrip("/")
    v_name = VOICES.get(voice, f"音色({voice})")
    safe_api_key = urllib.parse.quote(api_key)

    tts_url = f"{base_url}/tts?api_key={safe_api_key}&voice={voice}&model={model}&volume=100&pitch=0&personality=undefined&rate={{{{(speakSpeed - 10) * 2}}}}&text={{{{java.encodeURI(speakText)}}}}"

    return JSONResponse(
        content=[
            {
                "name": f"小米 - {v_name}",
                "url": tts_url,
                "contentType": "audio/mpeg",
                "id": int(time.time() * 1000),
                "concurrentRate": "",
                "loginUrl": "",
                "loginUi": "",
                "loginCheckJs": "",
                "header": '{"Authorization":"Bearer undefined"}',
            }
        ]
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8099)
