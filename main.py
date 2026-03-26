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
    "mimo_default": "MiMo-默认",
    "default_zh": "MiMo-中文女声",
    "default_en": "MiMo-英文女声",
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


@app.get("/tts")
def tts_forwarder(request: Request):
    api_key = request.query_params.get("api_key", "")
    text = request.query_params.get("text", "")
    voice = request.query_params.get("voice", "mimo_default")

    if not api_key:
        return Response(status_code=403, content="Missing api_key")
    if not text:
        return Response(status_code=400, content="Empty text")

    text = urllib.parse.unquote(urllib.parse.unquote(text))

    try:
        client = OpenAI(api_key=api_key, base_url="https://api.xiaomimimo.com/v1")
        response = client.chat.completions.create(
            model="mimo-v2-tts",
            messages=[
                {"role": "user", "content": "请朗读"},
                {"role": "assistant", "content": text},
            ],
            audio={"format": "mp3", "voice": voice},
            stream=False,
        )
        audio_data = response.choices[0].message.audio
        audio_b64 = (
            audio_data.get("data")
            if isinstance(audio_data, dict)
            else getattr(audio_data, "data", None)
        )

        if not audio_b64:
            return Response(status_code=500, content="API Error")

        audio_bytes = base64.b64decode(audio_b64)

        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Length": str(len(audio_bytes)),
                "Cache-Control": "max-age=3600",
            },
        )
    except Exception as e:
        logger.error(f"TTS Error: {type(e).__name__}: {e}")
        return Response(status_code=502, content=f"上游API错误: {type(e).__name__}")


@app.get("/api/legado-import")
async def legado_import(request: Request, voice: str = "mimo_default"):
    api_key = request.query_params.get("api_key", "")
    base_url = str(request.base_url).replace("http://", "https://").rstrip("/")
    v_name = VOICES.get(voice, f"音色({voice})")
    safe_api_key = urllib.parse.quote(api_key)

    tts_url = f"{base_url}/tts?api_key={safe_api_key}&voice={voice}&volume=100&pitch=0&personality=undefined&rate={{{{(speakSpeed - 10) * 2}}}}&text={{{{java.encodeURI(speakText)}}}}"

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
