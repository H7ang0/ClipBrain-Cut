# ClipBrain Cut

**ClipBrain Cut** 是一个由 AI 驱动的本地化“提示词剪辑”终端代理工具 (Agentic Workflow)。它将大模型的多模态视觉理解能力与 Claude Code 的 MCP (Model Context Protocol) 架构深度结合，让你只需在终端输入自然语言提示词，就能在海量本地视频素材中精准提取想要的画面，并一键生成可直接二次编辑的剪映 (CapCut) 草稿工程。

> Created by [@h7ang0](https://github.com/h7ang0)

## 核心特性

- **智能拉片引擎 (AI Indexing)**：通过调用 Gemini 视觉大模型，自动提取本地视频素材的镜头类型、动作描述、台词大意和情绪标签，建立结构化本地索引库。
- **终端语义检索 (Semantic Search)**：告别按文件名和时间轴找素材的繁琐操作。直接输入文字即可定位到精确的秒数级别。
- **原生剪映轨道生成 (Auto Draft Export)**：检索完毕后，后台脚本自动计算微秒级时间轴，直接在本地生成包含对应素材片段的剪映草稿工程 (`draft_content.json`)。
- **Claude Code 无缝集成 (MCP Ready)**：作为底层 Tool 运行，允许你在命令行中与 AI 助手进行连贯的自动化剪辑对话。

## 环境要求

- Python 3.8 或更高版本
- 有效的 Gemini API Key（推荐使用能处理长视频的 `gemini-1.5-pro` 模型）
- 剪映专业版 (Mac 或 Windows) 已安装于本地环境
- Claude Code 工具链已配置完毕

## 配置

### 1. 环境变量配置

在运行任何脚本之前，请确保在你的系统中配置了 Gemini 的 API 密钥：

```bash
# Mac / Linux
export GEMINI_API_KEY="your_api_key_here"

# Windows (PowerShell)
$env:GEMINI_API_KEY="your_api_key_here"
```

2. 剪映草稿路径配置

项目中的 clipbrain_export.py 默认配置为 Mac 版本的剪映草稿路径。如果你是 Windows 用户，请打开该脚本，将 CAPCUT_DRAFT_DIR 变量修改为你的实际路径：

· Mac 默认路径: ~/Movies/CapCut/User Data/Projects/com.lveditor.draft/
· Windows 默认路径: C:\Users\你的用户名\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft\

3. MCP (Model Context Protocol) 配置

在项目根目录下创建 .claude/settings.json 文件，并将以下内容写入，以将工具暴露给 Claude Code：

```json
{
  "mcpServers": {
    "clipbrain_search": {
      "command": "python3",
      "args": ["clipbrain_search.py"],
      "description": "ClipBrain Cut Search Tool. Use this to find specific video clips from the local database based on user prompts."
    },
    "clipbrain_export": {
      "command": "python3",
      "args": ["clipbrain_export.py"],
      "description": "ClipBrain Cut Export Tool. Use this tool AFTER retrieving clips to generate a CapCut (剪映) project timeline."
    }
  }
}
```

使用教程与指南

第一阶段：初始化与建库

1. 克隆项目并安装依赖
   ```bash
   git clone https://github.com/h7ang0/ClipBrain-Cut.git
   cd ClipBrain-Cut
   pip install -r requirements.txt
   ```
2. 准备原始视频素材
      在项目根目录下创建一个名为 raw_materials/ 的文件夹，并将你的测试视频（支持 .mp4, .mov, .webm）放入其中。
3. 执行智能拉片
      在终端运行以下命令。该脚本会自动将视频上传至 Gemini API 提取特征并生成本地索引，完成后会自动清理云端文件。
   ```bash
   python clipbrain_indexer.py
   ```
   运行结束后，项目根目录会生成 ClipBrain_Library.json 本地数据库文件。

第二阶段：终端自动化剪辑

启动你的 Claude Code，确保当前工作目录位于 ClipBrain-Cut 项目根目录下。你可以直接输入如下形式的自然语言指令：

"我准备做一个工作日常的短视频。请调用 clipbrain_search 帮我从素材库里找 3 段我敲代码或者表情严肃的片段。找到之后，将这 3 个片段通过 clipbrain_export 工具打包生成一个名为 'Dev_Vlog_01' 的剪映工程。"

Claude Code 将自动完成思考、检索以及生成草稿的工作流。执行完毕后，打开你的剪映客户端，在本地草稿列表中即可看到名为 Dev_Vlog_01 的新项目，点击进入即可进行最终的微调、转场和调色。

路线图

· 视频素材多模态拉片建库 (clipbrain_indexer.py)
· 基于提示词的本地语义检索 (clipbrain_search.py)
· 根据检索结果自动生成剪映 (CapCut) draft_content.json 草稿轨道 (clipbrain_export.py)
· 接入本地向量数据库 (如 ChromaDB) 以提升大规模素材的语义检索精度
· 支持根据 IP 配置文件 (IP Profile) 自动分配剪辑节奏
· 增加根据视频情绪自动匹配无版权 BGM 的轨道生成功能

版本历史

v1.0.0 (Current)

· 发布: 核心 AI 视频多模态拉片引擎 (clipbrain_indexer.py)。
· 发布: 本地 JSON 语义匹配与检索模块 (clipbrain_search.py)。
· 发布: 剪映 (CapCut) 轨道生成器与微秒级时间轴计算模块 (clipbrain_export.py)。
· 集成: 完成基于 MCP 的 Claude Code 终端代理完整工作流配置。

许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。


