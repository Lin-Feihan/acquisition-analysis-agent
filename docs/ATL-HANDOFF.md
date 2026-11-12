# ATL 上架交接说明

## 交付目标

将本仓库中的两个独立研究 agent 接入现有 `atl-research-service` 并分别上架 ATL。本次交付包含任务内容、输入规范、本地运行程序及离线检查，不要求先完成金融案例研究。

当前不是已部署的 HTTP 服务，也未修改现有 ATL 服务仓库。部署环境、平台表单、任务管理及网关联调由接手的技术同学完成。

## 两个独立注册项

| 项目 | 收购方 | 目标公司 |
|---|---|---|
| Agent ID | `acquirer-acquisition-analysis` | `target-acquisition-analysis` |
| 显示名称 | Acquirer-Side Acquisition Analysis Agent | Target-Side Acquisition Offer Analysis Agent |
| 内容目录 | `agents/acquirer/` | `agents/target/` |
| 输入规范 | `agents/acquirer/manifest.json` | `agents/target/manifest.json` |
| 研究程序入口 | `agents.acquirer.runtime.agent_runner.run_agent` | `agents.target.runtime.agent_runner.run_agent` |
| 本地命令入口 | `python -m agents.acquirer.runtime.main` | `python -m agents.target.runtime.main` |

两套独立运行、独立展示；不要增加 `perspective` 字段或合并为一个 ATL agent。可以共用同一后台服务及通用基础代码。

## 需要带入服务的文件

- `acquisition_runtime/`：共享的输入校验、提示词组装、服务调用、结果保存和导出代码。
- `agents/acquirer/` 与 `agents/target/`：分别保留 manifest、prompt、question list、output specification 和运行入口。
- `requirements.txt`：真实模型调用所需依赖。
- `requirements-export.txt`：可选文档导出依赖。

不要只复制两个 agent 目录而遗漏 `acquisition_runtime/`。可以将本仓库代码合并至服务仓库根目录，保留相同导入路径；注意合并现有 `agents/` 目录，而不是覆盖原有找壳和尽调 agent。若改用其他包路径，需同步调整导入。

## 平台输入表单

分别读取各自 `manifest.json` 中的 `settings_schema.fields`，生成对应表单。每个 agent 有 16 个字段：6 个基础字段、9 个 question-list 字段、1 个补充说明字段。

- 公司与信息截止日按 manifest 标为必填。
- 九个问题可以不回答；保留 `Not specified`、`Unknown`、`Not available` 等状态，不能编造偏好或事实。
- 未填估值日期时，运行程序采用信息截止日，不是运行当日。
- 前端提交的键名必须与 manifest 一致；不接受多余字段。
- `available_documents_and_scope` 是材料与范围说明，不是文件上传功能。
- 研究语言及币种沿用各自 manifest 的默认值，支持用户修改。

建议基础字段直接展示，九个问题放入可展开区域。具体页面布局由 ATL 前端决定，字段内容保持一致。

## 对接现有任务接口

沿用服务已有的认证和后台任务机制，分别注册两个 ID：

```text
GET  /manifest?agent_id=acquirer-acquisition-analysis
GET  /manifest?agent_id=target-acquisition-analysis
POST /runs
GET  /runs/{run_id}
GET  /runs/{run_id}/result
```

这些是接入目标，不是本仓库已经提供的 HTTP 接口。保留现有 `X-Service-Token` 认证；它属于平台到服务的认证，与模型 API key 分开管理。

### 推荐后台调用方式

在现有后台 worker 中使用 `run_agent(settings, provider)`，避免将交互式 CLI 放进 HTTP 请求。调用前校验输入；worker 负责保存和更新 ATL 任务状态。

以下示意明确了实际函数签名；不是已经部署的服务补丁：

```python
import json
import os
from pathlib import Path

from acquisition_runtime.settings import validate_settings
from acquisition_runtime.providers import get_provider
from acquisition_runtime.output_handler import save_report
from agents.acquirer.runtime.agent_runner import run_agent as run_acquirer
from agents.target.runtime.agent_runner import run_agent as run_target

SPECS = {
    "acquirer-acquisition-analysis": (Path("agents/acquirer"), run_acquirer),
    "target-acquisition-analysis": (Path("agents/target"), run_target),
}

# In the existing authenticated route/worker:
root, run_agent = SPECS[agent_id]  # reject unknown IDs before this lookup
settings = validate_settings(root, submitted_settings)
gateway = bool(os.getenv("OPENAI_BASE_URL", "").strip())
config = json.loads((root / "runtime/config.yaml").read_text(encoding="utf-8"))
provider = get_provider(
    "commonstack" if gateway else "openai",
    config=config["providers"]["commonstack" if gateway else "openai"],
)
result = run_agent(settings=settings, provider=provider)
paths = save_report(
    result,
    output_directory=per_run_output_directory,
    save_docx=True,
    save_pdf=False,
)
```

服务端需以仓库根目录为工作目录，或把上例的路径解析为绝对路径。不要直接套用旧 worker 中向 `save_report` 传入公司名称的位置参数；新签名为 `save_report(result, output_directory, *, save_docx=True, save_pdf=False)`。

本仓库另有 `execute_run` 可生成本地运行编号和记录。现有 ATL worker 已有 run ID 时，建议使用上述底层入口，避免形成两套相互混淆的任务编号。任务输入快照、状态和使用量应写入现有服务的持久化记录。

## 模型与服务配置

| 环境变量 | 用途 |
|---|---|
| `OPENAI_API_KEY` | 原生 OpenAI 或 ATL 提供的网关密钥 |
| `OPENAI_BASE_URL` | 使用 CommonStack 时配置 ATL 提供的兼容 API 地址 |
| `RESEARCH_MODEL` | 网关使用的实际可用模型；CommonStack 路径应显式配置 |

不要在生产 worker 中等待终端输入密钥。不要提交真实 `.env`，也不要把密钥放进用户输入或平台返回结果。

当前支持原生 OpenAI Responses 的后台轮询，以及 CommonStack 兼容 Responses 的同步完成路径。其他研究供应商尚未移植。模型、搜索工具及网关是否兼容，需在部署环境联调；本地离线检查不证明接口可用。

`runtime/config.yaml` 使用 JSON 兼容的 YAML 写法；当前通过 JSON 解析器读取，修改时不要加入 YAML 专有语法或注释。

默认启用搜索请求，Code Interpreter 关闭。不要把 prompt 中的计算要求当作已实现的独立计算引擎。若需要开启计算工具，应先确认平台与模型支持，并保留实际返回的工具证据。

## 平台结果映射

- `report_markdown`：读取 `paths["markdown"]` 对应文件。
- `evidence`：读取 `paths["evidence"]` 对应 JSON。
- `usage.provider`：`result.provider`。
- `usage.model`：`result.metadata.get("model")`。
- `usage.input_tokens`、`usage.output_tokens`：从 `result.metadata.get("usage", {})` 的实际返回值映射；缺失值按平台协议表示，不解释成真实的零消耗。
- `usage.actual_cost_micro`：`result.metadata.get("actual_cost_micro")`；没有返回时保留 `null`，不要按估计值伪造实际费用。
- DOCX/PDF：只有文件存在时才附加，按现有 ATL 契约编码并遵守附件大小限制。
- `paths["warnings"]`：保存并在平台允许时展示；无结构化来源或导出失败均可能产生警告。

`evidence.metadata` 保存服务实际返回的来源与工具执行信息，不代表独立认证。程序不会保存模型的内部推理摘要。

## 错误、导出及保存

- 不合法的输入应在启动研究前返回字段错误，未知 agent ID 返回未找到。
- 模型调用失败、返回未完成结果或核心文件保存失败，应将任务标为失败。
- DOCX/PDF 导出失败只产生警告，已生成的 Markdown 和证据仍可返回。
- Linux 或未安装 Word 的环境可关闭 PDF。不得为等待 PDF 阻断报告返回。
- 保存失败信息前使用脱敏处理；不把供应商原始异常体直接返回用户。
- 轮询超时会尝试取消，但不能保证远端停止或费用停止。部署方仍需设置适当的任务生命周期及异常处理。
- 不要依赖临时磁盘长期保存报告；平台应沿用现有结果归档机制。

## 已完成与交接验收

已完成：两份独立任务内容与问题清单、输入校验、提示词组装、独立运行入口、服务调用适配、报告与证据保存、运行记录、可选 DOCX/PDF 导出、运行前预览。

已在本地通过 17 项离线检查，包含两套入口隔离、九项回答注入、默认值、失败处理、服务返回解析及 DOCX 内容保存。它们使用模拟服务，不产生研究调用费用。

技术同学接手后需要完成：

1. 在服务中分别注册两个 manifest、执行入口和平台表单。
2. 配置生产服务地址、密钥与模型，并安装依赖。
3. 验证认证、输入校验、任务创建、状态查询、结果获取和附件展示。
4. 在部署环境完成实际接口联调，确认搜索工具、使用量与错误返回兼容。
5. 确认结果能被 ATL 保存，再分别上架两个 agent。

上述是部署联调工作，不要求交付方先完成金融案例报告。当前未进行真实研究质量评估，不宣称上架完成、财务建议可靠性得到验证、XBRL 核验完成或报告获得认证。

## 无密钥快速检查

在仓库根目录运行：

```powershell
python -m unittest discover -s tests -v
python -m agents.acquirer.runtime.main --settings agents/acquirer/examples/hypothetical.json --dry-run
python -m agents.target.runtime.main --settings agents/target/examples/hypothetical.json --dry-run
```

示例只是测试配置的假设输入，不是必须完成的研究案例。Python 3.12 以上可完成核心离线检查；DOCX 检查需要可选依赖。
