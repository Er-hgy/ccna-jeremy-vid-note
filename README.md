# Jeremy's IT Lab CCNA 本地学习资料生成器

这个项目使用 Python 和 `yt-dlp` 保存播放列表中每个视频的元数据、描述和英文字幕，提取描述中的章节时间轴，并生成适合交给 AI 的中文章节精讲与 quiz 解析 prompt。它设置了 `skip_download`，**不会下载视频或音频本体**。

## 输出结构

```text
CCNA/
├─ videos_raw/
│  └─ 001_Windows-safe title/
│     ├─ source.info.json
│     ├─ source.description
│     ├─ source.en.vtt（具体语言后缀可能略有不同）
│     ├─ chapters.txt
│     └─ local_metadata.json
├─ prompts/
│  ├─ chapter_note_prompt.md
│  └─ quiz_prompt.md
├─ generated_prompts/
│  ├─ video_001_day_001_chapter_notes_prompt.md
│  └─ video_001_day_001_quiz_prompt.md
├─ logs/
├─ scripts/
└─ index.md
```

## Windows + VS Code 安装

1. 安装 [Python 3.11 或更高版本](https://www.python.org/downloads/windows/)。安装时勾选 **Add Python to PATH**。
2. 在 VS Code 中打开本文件夹，然后打开终端（`Ctrl+``）。
3. 创建并激活虚拟环境：

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

4. 安装依赖：

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

5. 在 VS Code 中按 `Ctrl+Shift+P`，选择 **Python: Select Interpreter**，然后选择 `.venv` 中的 Python。

## 运行

下载整个播放列表的非视频资料并生成 `index.md`：

```powershell
python scripts\download_playlist.py
```

首次测试建议只处理第一个视频：

```powershell
python scripts\download_playlist.py --limit 1
```

从本地字幕和章节生成两类 prompt：

```powershell
python scripts\build_prompts.py
```

脚本可重复运行。`yt-dlp` 会覆盖同名元数据文件；生成 prompt 也会更新。完整播放列表可能需要较长时间，并可能受到 YouTube 限速。

## 行为与日志

- 文件夹名会移除 Windows 禁止的字符，并规避 `CON`、`NUL`、`COM1` 等保留名。
- `chapters.txt` 仅从视频描述的时间戳行提取。
- 下载阶段若没有英文人工字幕，会继续尝试英文自动字幕。
- 没有字幕或章节时，原始资料仍会保留，但该视频不会生成 prompt。
- 下载日志：`logs/download.log`；prompt 日志：`logs/build_prompts.log`。

## 常见问题排查

### `py` 或 `python` 找不到

重新安装 Python 并勾选 **Add Python to PATH**，关闭后重新打开 VS Code。也可在 Windows 的“管理应用执行别名”中关闭冲突的 Microsoft Store Python 别名。

### PowerShell 禁止运行 Activate.ps1

只对当前终端临时放行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### YouTube 返回 403、429、Sign in 或 bot 检测

先升级 `yt-dlp`：

```powershell
python -m pip install -U yt-dlp
```

稍后重试，避免频繁重复运行。部分地区或年龄限制内容可能需要浏览器 cookies；如确有需要，可在脚本的 `options` 中加入 `"cookiesfrombrowser": ("chrome",)`，并先完全关闭 Chrome。cookies 属于敏感登录凭据，不要提交或分享。

### 没有生成 prompt

查看 `logs/build_prompts.log`。最常见原因是视频描述没有章节时间轴，或没有可用英文字幕。检查对应 `videos_raw/.../` 中是否同时存在 `chapters.txt` 和 `source.en*.vtt`。

### 字幕文本有重复或识别错误

自动字幕本身可能重复或误识别。生成脚本会去除连续重复 cue，但不会擅自改写技术内容；prompt 已要求 AI 标记并谨慎纠正疑似错误。

## 自定义播放列表

```powershell
python scripts\download_playlist.py --url "你的播放列表 URL"
```

修改 `prompts/` 中的模板后，只需重新运行 `build_prompts.py`，无需重新下载资料。

文件名中的 `video_010` 是播放列表顺序，`day_005` 是课程标题里的实际 Day。两者特意同时保留，因为同一个 Day 可能包含正课、多个 Part、Extra 和 Lab。

## 每日课程笔记工作流

`notes/` 中每个实际课程 Day 对应一个空白 Markdown 文件，文件名包含当天的核心 topic，例如：

```text
notes/day_005_ethernet_lan_switching.md
notes/day_011_routing_fundamentals_static_routing.md
```

同一天可能有正课、Part 2、Extra 和 Lab。制作 Day N 笔记时，在 `generated_prompts/` 中搜索 `day_NNN`，把搜索到的该日全部文件上传给 ChatGPT。例如 Day 1 上传：

```text
video_001_day_001_chapter_notes_prompt.md
video_001_day_001_quiz_prompt.md
video_002_day_001_chapter_notes_prompt.md
video_002_day_001_quiz_prompt.md
video_003_day_001_chapter_notes_prompt.md
video_003_day_001_quiz_prompt.md
```

上传文件后，把下面这段固定模板复制粘贴给 ChatGPT。只需替换 `{DAY}`、`{NOTE_FILENAME}` 和 `{TOPIC}`：

```text
我要制作 Jeremy's IT Lab CCNA 课程的 Day {DAY} 中文学习笔记。

目标笔记文件：{NOTE_FILENAME}
当天主题：{TOPIC}

我已上传当天所有 chapter notes prompt 和 quiz prompt 文件。请完整阅读全部文件，并把同一天的正课、Part、Extra、Lab 和 Quiz 整合成一篇连贯的 Markdown 课程笔记。

要求：
1. 这不是视频摘要。请像中文 CCNA 老师重新授课一样完整解释，保留原课程的知识顺序和推导过程。
2. 不要逐文件机械复述；请按知识结构合并重复内容，同时注明 Lab、配置演示和 Quiz 的来源。
3. 首次出现的术语使用“中文解释（English term）”，Cisco IOS 命令必须放入代码块并逐行解释。
4. 对协议流程、报文或帧字段、设备行为、选路逻辑和配置命令，解释为什么、何时使用、如何验证及常见错误。
5. Quiz 必须逐题给出正确答案、推理过程和错误选项的错因。材料缺失时明确说明，不要臆造。
6. 自动字幕可能有误；结合 CCNA 知识修正明显错误，并标记“字幕疑似有误”。
7. 输出必须是可以直接保存到目标文件的完整 Markdown，不要写开场白，不要用 Markdown 代码围栏包住整篇笔记。
8. 使用下面的结构：

# Day {DAY}: {TOPIC}

## 学习目标
## 核心概念与原理
## 分章节详细讲解
## 配置与 Lab（如适用）
## 验证与故障排查
## Quiz 逐题解析
## 必须记住的规则
## 常见误区
## 主动回忆问题
## 本日复习清单

请一次输出完整笔记。如果内容超出单次输出限制，请在自然章节边界停止并写“【待续：下一章节名称】”；我回复“继续”后，从该位置继续，不要重复前文。
```

把 ChatGPT 的最终回答复制到对应的 `notes/day_NNN_topic.md` 中即可。建议先完成 Day 1，用它校准你喜欢的讲解深度，再继续后面的课程。

如果播放列表以后新增或调整课程，可重新生成缺少的空笔记文件。脚本不会覆盖已经存在的笔记：

```powershell
.\.venv\Scripts\python.exe scripts\create_note_files.py
```
