# 小米 TTS for 阅读 

为 [legado](https://github.com/gedoor/legado) 阅读 App 提供小米 MiMo TTS 语音合成服务。

## 功能特性

- 使用小米 **MiMo V2.5** 语音合成模型（默认）
- 支持三种 V2.5 模式：**内置音色**、**VoiceDesign**、**VoiceClone**
- 支持 MiMo V2 模型（兼容）
- 支持 legado 阅读 App 一键导入
- **8种 v2.5 内置音色** + 2种 v2 音色可选
- 语音风格控制（开心、悲伤、东北话、粤语、唱歌等）
- 情感控制、角色扮演
- 在线试听
- 本地部署，数据不经过第三方

## 模型版本

| 版本 | 模型名称 | 说明 |
|------|----------|------|
| **V2.5 内置音色（推荐）** | `mimo-v2.5-tts` | 内置8种音色，快速上手 |
| **V2.5 VoiceDesign** | `mimo-v2.5-tts-voicedesign` | 文本描述定制音色 |
| **V2.5 VoiceClone** | `mimo-v2.5-tts-voiceclone` | 上传音频复刻任意音色 |
| V2（兼容） | `mimo-v2-tts` | 旧版模型，兼容使用 |

## V2.5 三种模式说明

### 1. 内置音色模式
使用官方预设的音色，无需额外配置。

### 2. VoiceDesign（音色设计）
通过文本描述来定制音色特征，例如：
- "温柔的女声，略带磁性"
- "活泼可爱的萝莉音"
- "低沉磁性的男声"

### 3. VoiceClone（音色克隆）
上传一段音频样本（MP3/WAV），AI 会学习该音频的音色特征，用于生成语音。

**使用要求：**
- 支持 MP3、WAV 格式
- 音频时长建议 5-30 秒
- 音频质量越好，克隆效果越好

## 音色列表

### V2.5 内置音色

| 音色 ID | 名称 | 特点 |
|---------|------|------|
| `冰糖` | 冰糖-活泼女声 | 活泼可爱 |
| `茉莉` | 茉莉-温柔女声 | 温柔细腻 |
| `苏打` | 苏打-清新男声 | 清新自然 |
| `白桦` | 白桦-知性男声 | 知性优雅 |
| `Mia` | Mia-英文女声 | 英文女声 |
| `Chloe` | Chloe-英文女声 | 英文女声 |
| `Milo` | Milo-英文男声 | 英文男声 |
| `Dean` | Dean-英文男声 | 英文男声 |

### V2 音色（兼容）

| 音色 ID | 名称 |
|---------|------|
| `mimo_default` | MiMo-默认 |
| `default_zh` | MiMo-中文女声 |
| `default_en` | MiMo-英文女声 |

## 风格示例

### 基础风格（V2.5 & V2）

```
<style>开心</style>明天就是周五了，真开心！
<style>悲伤</style>呜呜，我的快递又丢了...
<style>生气</style>你怎么又迟到了！
<style>东北话</style>哎呀妈呀，这天儿也忒冷了吧！
<style>粤语</style>呢个真係好正啊！
<style>唱歌</style>原谅我这一生不羁放纵爱自由
<style>悄悄话</style>我跟你说个秘密...
```

### V2.5 新增情感控制

```
<style>happy</style>The weather is wonderful today!
<style>sad</style>Everything feels so gray today.
<style>gentle</style>Take your time, no rush.
<style>excited</style>This is amazing news!
```

### V2.5 角色扮演

```
<style>孙悟空</style>俺老孙来也！
<style>林黛玉</style>黛玉在此，见笑了。
<style>钢铁侠</style>I am Iron Man.
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
| `model` | 否 | 模型版本，默认 `v2.5`（可选 `v2.5`、`v2.5_design`、`v2.5_clone`、`v2`） |
| `voice` | 否 | 音色（v2.5/v2）或音色描述（VoiceDesign） |
| `audio` | 否 | 音频样本 base64（VoiceClone 模式） |

## License

MIT
