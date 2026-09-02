# dw-model-creator

> 项目状态：工作流设计已形成基线，Skill 正处于结构规划与基础搭建阶段，尚未达到可安装、可运行或生产可用状态。

`dw-model-creator` 是面向银行数据仓库建模工作的 Skill 项目。它接收需求分析阶段已经产出的标准化数据需求或其他合规模型产物，查询仓内资产和字段血缘，判断现有数仓是否能够提供所需数据；当存在能力缺口时，继续完成模型变更规划、影响分析、概念模型、逻辑模型、物理模型、模型评审以及 DDL 交付。

项目以 [workflow.html](workflow.html) 作为目标工作流设计基线。该页面定义了11个可独立运行的工作流、动态规划机制、14个典型任务场景以及全局治理规则。

## 文档与运行事实源

- `workflow.html`：目标能力、工作流和动态规划的设计基线，不作为运行时配置，也不打入 Skill。
- `README.md`：项目范围、目标结构和当前建设状态说明。
- `skills/dw-model-creator/SKILL.md`：未来的 Skill 运行入口；当前尚未创建。
- `skills/dw-model-creator/assets/control-plane/*.csv`：未来的工作流依赖、产物、规则和状态的机器可读事实源。
- 其他尚未与 `workflow.html` 对齐的设计草案不作为运行依据。

## 能力边界

### Skill负责

- 校验标准化数据需求的结构、引用、版本和一致性，不改写业务含义。
- 查询数仓模型、表、字段、指标、标签及其技术属性。
- 查询表级和字段级上下游血缘，并记录证据等级、覆盖范围和缺口。
- 判断需求数据项可以直接提供、通过现有资产推导、扩展存量模型，还是需要新增模型。
- 将供数缺口转化为模型缺口图、模型变更计划和设计任务。
- 分析模型变更的上下游影响、兼容性风险和未知范围。
- 完成概念模型、逻辑模型和物理模型设计。
- 校验和评审模型，绑定审批结果与模型版本指纹。
- 从已批准的物理模型确定性生成 DDL、迁移建议和交付材料。

### Skill不负责

- 从原始需求推导报表、文件或接口应该包含哪些字段。
- 定义、修改或批准字段、指标、标签的业务含义和业务口径。
- 代替需求分析阶段补写、转换或确认需求。
- 实现 ETL、调度、报表前端、API 服务端或数据推送程序。
- 直接修改生产模型、生产数据库或其他生产资产。

如果输入仍是未经需求分析的原始业务描述，Skill 应返回 `out-of-scope`，并要求先完成需求分析，而不是自行推导业务字段。

## 11个可独立运行的工作流

| ID | 工作流 | 主要输入 | 主要输出 |
|---|---|---|---|
| WF-01 | 标准化数据需求校验 | 标准化需求、Schema版本、确认信息、口径引用 | 校验报告；通过时生成 `ValidatedRequirementRef` |
| WF-02 | 数仓资产查询 | 查询范围或已校验需求范围、只读元数据源 | `AssetSnapshot`、资产覆盖报告、证据索引 |
| WF-03 | 数仓血缘查询 | 表/字段标识、方向、深度及血缘证据源 | `LineageSnapshot`、覆盖报告、血缘缺口报告 |
| WF-04 | 供数能力评估 | 已校验需求、资产快照、可选血缘快照 | `SupplyAssessment`、需求项资产映射、供数证据 |
| WF-05 | 模型缺口与变更规划 | 供数评估、资产快照、分层与建模规则 | `ModelGapGraph`、`ModelChangePlan`、设计任务集 |
| WF-06 | 模型影响分析 | 变更计划或明确差异、资产、血缘、兼容性规则 | 受影响对象、兼容性风险、分析精度和处置建议 |
| WF-07 | 概念模型设计 | 模型设计任务、已确认业务语义、可选概念基线 | `ConceptualModelSpec`、阶段检查结果 |
| WF-08 | 逻辑模型设计 | 概念模型或批准基线、设计任务、源资产信息 | `LogicalModelSpec`、字段语义映射、阶段检查结果 |
| WF-09 | 物理模型设计 | 逻辑模型或批准基线、目标引擎、物理规则 | `PhysicalModelSpec`、物理差异、计划血缘和迁移策略 |
| WF-10 | 模型校验与评审 | 单阶段模型或完整模型包、标准、影响分析 | `ModelReviewReport`、问题清单、审批结果和模型指纹 |
| WF-11 | DDL与交付物生成 | 已批准物理模型、审批凭证、引擎Profile、交付配置 | DDL、追溯矩阵、迁移/回退建议和交付包 |

每个工作流都具有独立输入契约、输出契约、局部校验、降级规则和终止状态。外部产物只要版本、指纹、状态和内容满足契约，就可以替代其生产工作流在本次任务中的执行。

## 动态规划与自动编排

动态规划器是 Skill 的编排能力，不是第12个工作流，也不产生数仓业务产物。

规划器根据以下事实生成 CSV 形式的 `ExecutionPlan`：

- 用户期望的最终产物和可选停止点。
- 当前已有且通过契约校验的产物。
- 新增模型、存量变更或混合任务。
- 资产标识、血缘覆盖、变更风险和确认策略。

规划过程包括：

1. 识别目标、停止点、范围和已有材料，不推导新的业务字段或业务含义。
2. 校验已有产物的版本、指纹、状态和内容。
3. 从目标产物反向计算 `requires` 依赖闭包。
4. 应用 `mandatory_when`、`skip_when`、`blocks_when`、风险和审批门禁。
5. 裁剪已满足步骤，执行拓扑排序和并行分组。
6. 校验输入绑定、依赖闭包、强制阶段、风险门禁和无环性，通过后才执行。
7. 工作流产生新的分支结论或风险事实后，更新产物集合并重新规划。

新增模型必须依次完成 WF-07、WF-08 和 WF-09。WF-06 的 `planning` 模式评估候选方案，`release` 模式复核最终物理差异，两次分析绑定不同版本的输入，不是循环调用。

## 典型任务场景

SC-01至SC-14是动态规划器的说明样例和回归评测基准，不是固定路线、生产配置或用户必须选择的执行入口。

- SC-01 快速直接供数判断
- SC-02 完整供数能力评估
- SC-03 模型缺口和变更决策
- SC-04 新增模型完整设计
- SC-05 存量模型概念边界变化
- SC-06 存量模型逻辑变化
- SC-07 存量模型仅物理变化
- SC-08 需求驱动的端到端新增模型
- SC-09 混合需求批量处理
- SC-10 资产与血缘盘点
- SC-11 独立模型变更影响分析
- SC-12 从任一合规模型阶段继续设计
- SC-13 存量设计包上线前复核
- SC-14 已评审模型重新生成交付物

生产运行只根据目标产物、已有产物和治理规则动态计算计划，不通过场景编号选择路线。

## 全局治理规则

- WF-01只校验需求，不生成新的标准化需求。
- “未查到资产”不等于“资产不存在”，“未查到血缘”也不等于“没有依赖”。
- 血缘证据分为 `confirmed`、`inferred`、`partial` 和 `unavailable`。
- 可推导供数必须有字段血缘或明确转换规则证据，否则结论为 `cannot-determine`。
- 删除、改名、类型收窄、主键或粒度变化在字段血缘不足时必须阻断正式交付。
- 存量模型只有在上一级模型基线仍然有效时，才能从后续模型阶段开始。
- WF-11只能使用与已批准物理模型指纹绑定的有效审批凭证。
- WF-01不通过、WF-06影响不可接受或WF-10要求修改时，本次执行结束；修改输入后以新版本重新启动。
- 所有产物都必须记录版本、输入指纹、证据、覆盖范围、假设、风险、状态和推荐后续工作流。

统一运行状态如下：

| 状态 | 含义 | 是否允许继续 |
|---|---|---|
| `completed` | 结果完整可用 | 可以 |
| `completed-with-risks` | 结果可用，但存在已声明风险 | 由下游风险规则决定 |
| `needs-input` | 输入需要用户或上游修订 | 不可以；提交新版本后重跑 |
| `blocked` | 关键证据、权限或前置条件缺失 | 不可以 |
| `out-of-scope` | 请求超出当前工作流职责 | 移交正确工作流 |
| `failed` | 发生技术执行错误 | 排除故障后重跑 |

`blocked-for-delivery` 应作为 `blocked` 的领域原因码，而不是新增一套全局状态。

## CSV结构化约束

数仓领域的结构化状态、配置、规则和工作流交换数据统一使用版本化 CsvBundle。宿主平台要求的 `SKILL.md` frontmatter、`agents/openai.yaml`、Markdown 方法说明、模板、Python 脚本、SQL 和最终可读报告不属于该结构化数据契约。

CSV继续遵守以下基础规则：

- UTF-8无BOM、LF换行、半角逗号分隔。
- 非空字段使用双引号，字段内双引号写成两个双引号。
- 布尔值只允许 `true` 和 `false`。
- 日期使用 `YYYY-MM-DD`，时间戳使用带时区的 ISO 8601。
- null使用未加引号的 `\N`。
- 每个数据集、字段和枚举值必须有非空中文说明。
- 列顺序由字段字典确定，行顺序由稳定键确定。
- 对规范化后的 UTF-8/LF 字节计算 SHA-256 指纹。

每个正式 CsvBundle 都必须具有 manifest、契约版本、记录数量、内容 checksum 和 Bundle checksum。出现未登记字段、缺失必填字段、版本不兼容、主外键错误、排序不稳定或 checksum 不一致时必须阻断，不得忽略字段或猜测含义。

当前 [CSV Schema总纲](references/contracts/csv-schema.md) 仍为草案，不代表全部运行期数据集已经定稿。

## 目标目录

```text
dw-model-creator/
├── workflow.html
├── README.md
├── skills/
│   └── dw-model-creator/
│       ├── SKILL.md
│       ├── agents/
│       │   └── openai.yaml
│       ├── references/
│       │   ├── planner.md
│       │   ├── governance.md
│       │   ├── adapters.md
│       │   ├── workflows/
│       │   │   ├── wf-01-requirement-validation.md
│       │   │   ├── wf-02-asset-query.md
│       │   │   ├── wf-03-lineage-query.md
│       │   │   ├── wf-04-supply-assessment.md
│       │   │   ├── wf-05-change-planning.md
│       │   │   ├── wf-06-impact-analysis.md
│       │   │   ├── wf-07-conceptual-design.md
│       │   │   ├── wf-08-logical-design.md
│       │   │   ├── wf-09-physical-design.md
│       │   │   ├── wf-10-model-review.md
│       │   │   └── wf-11-delivery.md
│       │   ├── contracts/
│       │   └── modeling/
│       ├── assets/
│       │   ├── control-plane/
│       │   ├── bootstrap/
│       │   ├── policies/
│       │   ├── engine-profiles/
│       │   ├── knowledge/
│       │   └── templates/
│       └── scripts/
│           ├── plan_workflows.py
│           ├── validate_artifacts.py
│           ├── normalize_snapshots.py
│           └── render_ddl.py
├── evals/
│   ├── evals.json
│   └── fixtures/
└── tests/
    ├── unit/
    ├── contract/
    ├── integration/
    └── fixtures/
```

目录职责：

| 目录 | 职责 |
|---|---|
| `skills/dw-model-creator/references/workflows/` | 保存11个可独立加载的工作流说明 |
| `skills/dw-model-creator/references/contracts/` | 保存产物信封、规划、查询、评估、模型和交付契约 |
| `skills/dw-model-creator/references/modeling/` | 保存概念、逻辑、物理模型方法及评审交付方法 |
| `skills/dw-model-creator/assets/control-plane/` | 保存工作流、输入输出、规则、产物和状态的机器可读 CSV |
| `skills/dw-model-creator/assets/policies/` | 保存依赖、分层、命名、兼容性、风险和审批规则 |
| `skills/dw-model-creator/assets/engine-profiles/` | 保存引擎类型映射、方言和 DDL 能力 |
| `skills/dw-model-creator/scripts/` | 只承担规划、校验、快照规范化和确定性 DDL 渲染 |
| `evals/` | 保存典型场景、独立工作流和健壮性评测，不参与生产路由 |
| `tests/` | 验证脚本、CSV契约和规划不变量，不作为生产数据源 |

## 运行目录

Skill目录是只读定义和发布物，不保存任务运行状态。所有运行期产物必须写入用户明确授权的外置工作目录，例如：

```text
<work-root>/runs/<run-id>/
├── input/
│   ├── planning_request.csv
│   └── artifact_inventory.csv
├── plan/
│   ├── execution_plan.csv
│   ├── plan_artifacts.csv
│   └── plan_steps.csv
├── artifacts/
├── evidence/
├── reports/
├── delivery/
└── logs/
```

禁止把运行产物、生产资产快照、用户输入或审批证据写入 Skill 根目录、`references/`、`assets/`、`evals/` 或 `tests/`。

## 当前建设状态

当前仓库中的文件主要是目标设计、开发种子和测试样例，不应被理解为对应能力已经完成。

| 内容 | 当前状态 |
|---|---|
| `workflow.html` | 目标工作流设计基线 |
| `skills/dw-model-creator/` | 空目录，尚未形成有效 Skill |
| 根目录 `assets/bootstrap/` | Bootstrap样例；字段、checksum和自描述能力仍需修复 |
| 根目录 `assets/policies/` | 规则种子；尚需治理确认、manifest和契约登记 |
| PostgreSQL Profile | 配置种子；尚未通过完整 DDL 测试 |
| `references/contracts/csv-schema.md` | 草案 |
| 两个 CSV 校验器 | 骨架实现，仍含 TODO |
| 资产目录 fixture | 仅供测试使用，不是生产资产证据 |
| `evals/` | 只有一个 Markdown 场景，尚未形成 `evals.json` |
| `tests/unit`、`tests/contract`、`tests/integration` | 尚无测试代码 |
| 模型设计、资产血缘、动态规划、DDL脚本 | 尚未实现 |

在完成契约、脚本、评测和回归验证之前，不应宣称 Skill 已经能够正式完成模型设计或生成生产交付 DDL。

## 建设顺序

1. 创建 `skills/dw-model-creator/` 的最小 Skill 骨架。
2. 定稿统一产物信封、状态、指纹和有效期规则。
3. 建立工作流、输入输出、规划规则、产物和状态控制面 CSV。
4. 编写11个独立工作流说明和共享建模方法。
5. 实现计划生成、计划校验、产物校验和快照规范化脚本。
6. 修复并迁入 Bootstrap、策略、知识和引擎 Profile。
7. 实现模型评审、审批绑定和确定性 DDL 交付。
8. 建立11个独立工作流、14个典型场景和健壮性评测。
9. 通过完整回归后再发布可用版本。
