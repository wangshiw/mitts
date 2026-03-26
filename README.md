# 小米 TTS for 阅读

为 [legado](https://github.com/gedoor/legado) 阅读 App 提供小米 MiMo TTS 语音合成服务。

## 功能特性

- 支持 legado 阅读 App 一键导入
- 多种音色（默认、中文女声、英文女声）
- 语音风格控制（开心、悲伤、东北话、粤语、唱歌等）
- 在线试听
- 本地部署，数据不经过第三方

## 音色列表

| 音色 ID | 名称 |
|---------|------|
| `mimo_default` | MiMo-默认 |
| `default_zh` | MiMo-中文女声 |
| `default_en` | MiMo-英文女声 |

## 风格示例

```
<style>开心</style>明天就是周五了，真开心！
<style>东北话</style>哎呀妈呀，这天儿也忒冷了吧！
<style>粤语</style>呢个真係好正啊！
<style>唱歌</style>原谅我这一生不羁放纵爱自由
```

## 快速部署

### Vercel 部署（推荐）

[![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/new)

fork 本项目后，点击上方按钮进入 Vercel，选择并导入您的仓库即可一键部署。部署完成后在页面手动输入 API Key 即可使用。

### 本地部署

#### 1. 克隆项目

```bash
git clone https://github.com/ISuuuu/xiaomitts.git
cd xiaomitts
```

#### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 3. 启动服务

```bash
python main.py
```

服务默认运行在 `http://localhost:8099`

#### 后台运行（推荐）

```bash
pm2 start python --name "mitts" -- main.py
```

## 导入到阅读 App

1. 打开阅读 App
2. 进入 **我的** → **朗读引擎**
3. 点击右上角 **+**
4. 选择 **网络导入**
5. 在本项目页面输入 API Key，点击 **直接导入** 或 **扫码导入**

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | Web 管理界面 |
| `/tts` | GET | 语音合成接口 |
| `/api/legado-import` | GET | 阅读 App 导入配置 |

### TTS 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `api_key` | 是 | 小米 API Key |
| `text` | 是 | 要合成的文本 |
| `voice` | 否 | 音色，默认 `mimo_default` |

## License

MIT
