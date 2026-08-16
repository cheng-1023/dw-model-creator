# dw-model-creator

`dw-model-creator` 是面向银行数据仓库场景的建模 Skill 项目，用于把报表、数据文件、API、推送、指标、标签及物理模型等需求，转换为可递归求解、可追溯、可校验的数仓设计。

项目采用“反向定义、正向验证”的工作方式：先从应用端字段和粒度出发，按应用端 → DM → DWM → DWD 识别能力缺口，再从 DWD → DWM → DM → 应用端验证模型、字段和依赖链。每个数仓模型必须依次完成概念模型、逻辑模型和物理模型设计；物理模型确认后，才允许按目标引擎生成 DDL，默认引擎为 PostgreSQL。

核心设计约束：

- 所有数仓领域状态、配置和组件交换数据使用 CSV；宿主平台强制的 Skill 发现元数据不属于该领域数据契约。
- 所有模型和字段依赖严格遵守版本化依赖矩阵。
- 所有类型、枚举、CSV 字段及数仓模型字段必须具有明确说明。
- DWD、DWM、DM 使用独立的物理设计处理单元，具体分层规则按阶段补充。
- 缺少关键证据或命中红线时进入人工介入，人工输入回流反向求解后仍失败才形成最终失败。
- Skill 只生成设计、检查结果和变更建议，不直接修改生产资产或实施生产作业。

## 规划目录

以下仅展示规划目录，不列出尚未创建的具体文件。

```text
dw-model-creator/
├── references/
│   ├── contracts/
│   ├── runtime/
│   ├── application-design/
│   ├── semantic-objects/
│   ├── model-design/
│   │   ├── conceptual/
│   │   ├── logical/
│   │   └── physical/
│   │       ├── dwd/
│   │       ├── dwm/
│   │       └── dm/
│   ├── asset-catalog/
│   └── examples/
├── assets/
│   ├── bootstrap/
│   ├── knowledge/
│   │   ├── business-glossary/
│   │   └── word-roots/
│   ├── policies/
│   │   ├── dependency/
│   │   ├── naming/
│   │   ├── subject/
│   │   ├── layering/
│   │   ├── quality/
│   │   └── security/
│   ├── engine-profiles/
│   │   └── postgresql-default/
│   └── templates/
├── scripts/
│   ├── runtime/
│   ├── validation/
│   ├── knowledge/
│   ├── asset-catalog/
│   ├── physical-design/
│   │   ├── dwd/
│   │   ├── dwm/
│   │   └── dm/
│   └── ddl/
├── evals/
└── tests/
    ├── fixtures/
    │   └── examples/
    ├── unit/
    ├── contract/
    └── integration/
```

| 目录 | 说明 |
|---|---|
| `references/contracts/` | 保存 CSV Schema、CsvBundle、处理单元输入输出及字段说明等人工可读契约。 |
| `references/runtime/` | 保存递归求解、分支固定点、人工介入、回流和恢复协议。 |
| `references/application-design/` | 保存报表、CSV 文件、API 和推送等应用实体的设计方法。 |
| `references/semantic-objects/` | 保存粒度、维度、度量、指标和标签等跨阶段语义对象的定义与处理方法。 |
| `references/model-design/conceptual/` | 保存概念模型的范围、实体、事件、关系和阶段门禁方法。 |
| `references/model-design/logical/` | 保存逻辑模型的粒度、事实维度角色、字段、键、时态和可加性方法。 |
| `references/model-design/physical/` | 保存物理模型的通用契约，并分别维护 DWD、DWM、DM 的专属设计理念。 |
| `references/asset-catalog/` | 保存外置动态资产库的只读接入、查询、快照和覆盖性判定方法。 |
| `references/examples/` | 按完整业务场景保存优秀设计实践与反例；只用于推理参考，不作为资产存在性证据。 |
| `assets/bootstrap/` | 保存解析 CsvBundle 所需的基础类型、枚举、字段和键定义；作为只读版本化 Bootstrap CsvBundle 发布，其 manifest 格式、根 checksum 算法以及允许的版本/checksum 组合由校验器发布物固定。 |
| `assets/knowledge/` | 保存随 Skill 发布的只读版本化知识 CSV Bundle，当前包括业务术语和词根；每个 Bundle 都登记 manifest、schema version 和 checksum。 |
| `assets/policies/` | 保存只读版本化的依赖矩阵、命名、主题、分层、质量和安全规则 CSV Bundle；Markdown 只解释规则，具有 manifest 和 checksum 的 CSV 是执行事实源。 |
| `assets/engine-profiles/` | 保存只读版本化的目标引擎方言、类型映射和生成规则 CSV Bundle；一期提供默认 PostgreSQL Profile。 |
| `assets/templates/` | 保存待确认模型、最终设计和检查报告等 Markdown 交付物模板。 |
| `scripts/runtime/` | 保存工作队列、分支收敛、人工回流和版本提交等运行编排脚本。 |
| `scripts/validation/` | 保存 CSV、字段字典、指纹、依赖图、阶段门禁和控制面校验脚本。 |
| `scripts/knowledge/` | 保存知识 CSV 的有界查询和术语规范化脚本；知识结果不得参与资产命中、覆盖性或新建/复用判定。 |
| `scripts/asset-catalog/` | 保存外置资产库的有界查询、裁剪、来源校验和快照规范化脚本。 |
| `scripts/physical-design/` | 预留 DWD、DWM、DM 物理设计处理单元；具体分层流程实现前不得返回成功。 |
| `scripts/ddl/` | 保存仅读取已确认物理模型的确定性 DDL 生成与校验脚本。 |
| `evals/` | 保存真实触发场景和预期结果，评估 Skill 的触发、推理和产物质量。 |
| `tests/fixtures/` | 保存脱敏测试资产、需求、模型和预期结果；仅显式测试模式可读，所有模式下均为只读。 |
| `tests/unit/` | 测试单个校验器、规范化算法、处理单元和 DDL 生成器。 |
| `tests/contract/` | 测试 CsvBundle、三阶段模型、依赖矩阵和工作流状态迁移等跨文件契约。 |
| `tests/integration/` | 测试递归求解、独立分支、人工回流、固定点收敛和 DDL 生成的完整链路。 |

实际运行产生的 RunState、CsvBundle revision、人工证据、DDL、最终 Markdown 和执行日志不存入 Skill 目录，而是写入用户授权的外置工作目录。production 模式必须校验规范化路径，拒绝向 Skill 根目录及 `assets/`、`references/`、`tests/` 写入运行产物。生产资产快照和人工输入也不得写入 `assets/`。
