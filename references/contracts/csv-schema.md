# CSV Schema 总纲（草案）

> 状态：**草案**。本文档是 workflow-model-design.md 第 11.4 节要求的阻断性产物之一。
> 每个数据集必须逐字段定义：权威列集合、逻辑类型、必填性、空值、中文说明、主外键、唯一键、
> 稳定排序键和枚举引用。**状态为"待定义"的数据集完成定义之前，不得实现对应处理器。**

## 数据集状态总表

| 数据集 | 状态 | 说明 |
|---|---|---|
| `bundle_manifest.csv` | ✅ 已定义（见 workflow §11.1） | 数据包清单 |
| `type_dictionary.csv` | ✅ 已定义（bootstrap 样例已建） | 类型字典 |
| `type_values.csv` | ✅ 已定义（bootstrap 样例已建） | 枚举值字典 |
| `field_dictionary.csv` | ✅ 已定义（bootstrap 样例已建） | 字段字典 |
| `dataset_keys.csv` | ✅ 已定义（bootstrap 样例已建） | 主键/唯一键/排序键 |
| `dependency_matrix.csv` | 🔶 草案（见下文，待评审定稿） | 依赖矩阵 |
| `matrix_conditions.csv` | 🔶 草案（见下文，待评审定稿） | 矩阵条件 |
| `engine_profile_metadata.csv` | ✅ 已定义（见 workflow §4.4） | 引擎 Profile 声明 |
| `engine_type_mappings.csv` | ✅ 已定义（见 workflow §4.4） | 引擎类型映射 |
| `engine_dialect_rules.csv` | ✅ 已定义（见 workflow §4.4） | 引擎方言规则 |
| `current_bundle.csv` / `bundle_commits.csv` | ✅ 已定义（见 workflow §11.1） | Bundle 控制面 |
| `requests.csv` 及 3.7 节其余运行期数据集 | ⬜ 待定义 | 逐一定稿后方可实现处理器 |

## 通用硬性规则（适用于所有 CSV）

1. UTF-8 无 BOM、LF 换行、半角逗号分隔；非空字段一律双引号包裹，字段内双引号写成两个双引号。
2. 布尔只写 `true/false`；日期 `YYYY-MM-DD`；时间戳带时区 ISO 8601；空值写未加引号的 `\N`。
3. 反斜杠转义：非 null 文本中的 `\` 先加倍为 `\\` 再做 CSV 引号转义。
4. 每个数据集、每个字段、每个枚举值必须有非空中文说明；说明缺失即门禁失败。
5. fingerprint 计算：按 `field_dictionary.csv.ordinal` 排列列，按 `dataset_keys.csv` 稳定键排列行，
   对 UTF-8、LF 规范化字节计算 SHA-256。

## 草案：dependency_matrix.csv

| 字段 | 逻辑类型 | 必填 | 说明 |
|---|---|---|---|
| `matrix_rule_id` | string | 是 | 依赖矩阵规则稳定 ID，主键 |
| `decision` | enum:MatrixDecision | 是 | ALLOW / DENY / CONDITIONAL |
| `consumer_layer` | enum:PhysicalLayer | 是 | 引用方所在层 |
| `provider_layer` | enum:PhysicalLayer | 是 | 被引用方所在层 |
| `condition_ref` | reference | 否 | CONDITIONAL 时引用 matrix_conditions.csv.condition_id |
| `description` | string | 是 | 规则中文说明 |
| `version` | string | 是 | 规则版本 |
| `active` | boolean | 是 | 是否生效 |

键：primary = `matrix_rule_id`；sort = `matrix_rule_id`。

## 草案：matrix_conditions.csv

| 字段 | 逻辑类型 | 必填 | 说明 |
|---|---|---|---|
| `condition_id` | string | 是 | 条件稳定 ID，主键 |
| `matrix_rule_id` | reference | 是 | 引用 dependency_matrix.csv.matrix_rule_id |
| `condition_kind` | string | 是 | 条件类别（如 cross-layer-exception） |
| `required_evidence` | enum:EvidenceType | 是 | 满足条件所需证据类型 |
| `description` | string | 是 | 条件中文说明 |

键：primary = `condition_id`；sort = `condition_id`。

## 新增数据集 / 字段的流程

同一变更内必须同步更新：本文件、bootstrap 四件套、校验 fixture、契约测试——四处缺一即 Schema 收口门禁失败。
