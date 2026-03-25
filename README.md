# 小米 TTS 专属节点

基于小米 MiMo API 的 TTS 语音合成服务，支持阅读 App 一键导入。

## 功能特性

- 多种音色选择（默认、中文女声、英文女声等）
- 在线试听
- 阅读 App 一键导入
- Token 防盗刷

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/xiaomitts.git
cd xiaomitts
```

### 2. 创建虚拟环境

```bash
# 使用 uv（推荐）
uv venv py310 --python 3.10

# 或使用 venv
python -m venv py310
```

### 3. 激活虚拟环境

```bash
# Windows
py310\Scripts\activate

# Linux / macOS
source py310/bin/activate
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 配置

```bash
# 复制配置模板
cp config.example.json config.json

# 编辑 config.json，填入你的 API Key
```

### 6. 启动服务

```bash
python main.py
```

服务默认运行在 `http://localhost:8099`

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 管理后台 |
| `/tts` | GET | 语音合成 |
| `/api/legado-import` | GET | 阅读 App 导入配置 |

### TTS 请求参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `token` | 是 | 访问凭证 |
| `text` | 是 | 要合成的文本 |
| `voice` | 否 | 音色，默认 `mimo_default` |

## 可用音色

| 音色 ID | 名称 |
|---------|------|
| `mimo_default` | MiMo-默认 |
| `default_zh` | MiMo-中文女声 |
| `default_en` | MiMo-英文女声 |

## License

MIT
