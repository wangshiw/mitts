import base64
import time
import urllib.parse
import json
import os
from fastapi import FastAPI, Response, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from openai import OpenAI
import uvicorn

app = FastAPI()

CONFIG_FILE = "config.json"

# --- 1. 声音列表配置 ---
VOICES = {
    "mimo_default": "MiMo-默认",
    "default_zh": "MiMo-中文女声",
    "default_en": "MiMo-英文女声",
}


def load_config():
    default_config = {
        "api_key": "",
        "admin_password": "admin",
    }
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return default_config


def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


# --- 2. Web UI 管理后台 ---
@app.get("/")
async def index_page(request: Request):
    config = load_config()
    base_url = str(request.base_url).replace("http://", "https://").rstrip("/")

    options_html = "".join(
        [f'<option value="{k}">{v}</option>' for k, v in VOICES.items()]
    )

    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>小米 TTS 专属节点配置</title>
        <style>
            body {{ font-family: sans-serif; background: #f4f4f9; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }}
            .container {{ background: #fff; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); max-width: 500px; width: 100%; }}
            h2 {{ text-align: center; color: #333; margin-top: 0; }}
            h3 {{ color: #444; margin-bottom: 10px; border-bottom: 2px solid #eee; padding-bottom: 5px; }}
            label {{ font-weight: bold; margin-top: 15px; display: block; color: #555; font-size: 14px; }}
            input, select, textarea {{ width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; font-size: 14px; }}
            button {{ width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 6px; font-size: 16px; margin-top: 20px; cursor: pointer; }}
            button:hover {{ background: #0056b3; }}
            button.preview-btn {{ background: #28a745; margin-top: 10px; }}
            .info-box {{ background: #e9ecef; padding: 15px; border-radius: 6px; margin-top: 20px; font-size: 13px; border-left: 4px solid #007bff; word-break: break-all; }}
            .preview-section {{ background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef; margin-top: 20px; }}
            audio {{ width: 100%; margin-top: 15px; outline: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>⚙️ 小米 TTS 节点配置</h2>
            
            <form action="/save" method="post">
                <label>访问鉴权密码 (Token):</label>
                <input type="text" id="admin_password" name="admin_password" value="{config["admin_password"]}" required>
                <label>小米 API Key (sk-...):</label>
                <input type="password" id="api_key" name="api_key" value="{config["api_key"]}" required>
                <button type="submit">💾 保存配置</button>
            </form>

            <div class="preview-section">
                <h3>🎧 在线试听</h3>
                <label>选择发音人:</label>
                <select id="preview_voice">{options_html}</select>
                <label style="margin-top:10px">试听文本:</label>
                <textarea id="preview_text" rows="2">君不见黄河之水天上来，奔流到海不复回。</textarea>
                <button type="button" class="preview-btn" onclick="playPreview()" id="play_btn">▶️ 试听</button>
                <audio id="audio_player" controls style="display: none;"></audio>
            </div>

            <div class="info-box">
                <b>📌 阅读 App 导入链接：</b><br><br>
                <code id="import_link" style="cursor:pointer; display:block; padding:8px; background:#fff; border-radius:4px;" onclick="copyLink()" title="点击复制">{base_url}/api/legado-import?token={config["admin_password"]}&voice=mimo_default</code>
                <span id="copy_tip" style="color:#28a745; display:none;">已复制</span>
            </div>
        </div>

        <script>
            function updateImportLink() {{
                const token = document.getElementById('admin_password').value;
                const voice = document.getElementById('preview_voice').value;
                const baseUrl = "{base_url}";
                document.getElementById('import_link').innerText = `${{baseUrl}}/api/legado-import?token=${{encodeURIComponent(token)}}&voice=${{voice}}`;
            }}
            
            document.getElementById('admin_password').addEventListener('input', updateImportLink);
            document.getElementById('preview_voice').addEventListener('change', updateImportLink);

            function copyLink() {{
                const link = document.getElementById('import_link').innerText;
                const textarea = document.createElement('textarea');
                textarea.value = link;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                const tip = document.getElementById('copy_tip');
                tip.style.display = 'inline';
                setTimeout(() => tip.style.display = 'none', 1500);
            }}
            function playPreview() {{
                const token = document.getElementById('admin_password').value;
                const text = document.getElementById('preview_text').value;
                const voice = document.getElementById('preview_voice').value;
                const player = document.getElementById('audio_player');
                const btn = document.getElementById('play_btn');
                
                if (!token || !text) return alert("请填写参数！");
                
                btn.innerHTML = "⏳ 生成中...";
                btn.disabled = true;
                
                const url = `/tts?token=${{encodeURIComponent(token)}}&voice=${{encodeURIComponent(voice)}}&text=${{encodeURIComponent(text)}}`;
                player.src = url;
                player.style.display = 'block';
                player.oncanplay = function() {{ btn.innerHTML = "▶️ 试听"; btn.disabled = false; player.play(); }};
                player.onerror = function() {{ alert("生成失败！请检查 Token 或 API Key。"); btn.innerHTML = "▶️ 试听"; btn.disabled = false; player.style.display = 'none'; }};
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.post("/save")
async def save_settings(
    admin_password: str = Form(...),
    api_key: str = Form(...),
):
    save_config(
        {
            "admin_password": admin_password,
            "api_key": api_key,
        }
    )
    return RedirectResponse(url="/", status_code=303)


# --- 3. 核心功能：朗读接口 (严格校验 URL 里的 Token 防盗刷) ---
def verify_access(request: Request, config: dict):
    # 彻底放弃 Header 鉴权，只验证 URL 里的 token，规避安卓播放器吞 Header 的 Bug
    token_query = request.query_params.get("token", "")
    return token_query == config["admin_password"]


@app.get("/tts")
def tts_forwarder(request: Request):
    config = load_config()
    if not verify_access(request, config):
        print(f"[{time.strftime('%H:%M:%S')}] ❌ 拦截：播放器未携带合法 Token")
        return Response(status_code=403, content="Forbidden: Token 错误")

    text = request.query_params.get("text", "")
    voice = request.query_params.get("voice", "mimo_default")
    text = urllib.parse.unquote(urllib.parse.unquote(text))

    if not text:
        return Response(status_code=400, content="Empty text")

    try:
        client = OpenAI(
            api_key=config["api_key"], base_url="https://api.xiaomimimo.com/v1"
        )
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
                "Connection": "keep-alive",
            },
        )
    except Exception as e:
        return Response(status_code=500, content=str(e))


# --- 4. 导入接口：完美拼装你在上文指定的格式 ---
@app.get("/api/legado-import")
async def legado_import(request: Request, voice: str = "mimo_default"):
    config = load_config()

    # 验证导入请求，防止别人乱刷配置
    if request.query_params.get("token") != config["admin_password"]:
        return Response(status_code=403, content="Forbidden: 导入 Token 错误")

    base_url = str(request.base_url).replace("http://", "https://").rstrip("/")
    v_name = VOICES.get(voice, f"音色({voice})")

    # ★ 完美对齐：直接在你指定的基础 URL 里，把 token 无缝安插在 text 前面
    safe_token = urllib.parse.quote(config["admin_password"])
    tts_url = f"{base_url}/tts?voice={voice}&volume=100&pitch=0&personality=undefined&rate={{{{(speakSpeed - 10) * 2}}}}&token={safe_token}&text={{{{java.encodeURI(speakText)}}}}"

    config_data = {
        "name": f"小米 - {v_name}",
        "url": tts_url,
        "contentType": "audio/mpeg",
        "id": int(time.time() * 1000),
        "concurrentRate": "",
        "loginUrl": "",
        "loginUi": "",
        "loginCheckJs": "",
        # 严格保留官方格式装样子的 undefined 请求头
        "header": '{"Authorization":"Bearer undefined"}',
    }

    return JSONResponse(content=[config_data])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8099)
