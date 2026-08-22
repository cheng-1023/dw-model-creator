# bootstrap Bundle 说明

本目录是整套系统的**信任根**（Bootstrap CsvBundle），包含四个数据字典 CSV：

| 文件 | 作用 |
|---|---|
| `type_dictionary.csv` | 类型字典：所有逻辑类型、枚举类型的定义 |
| `type_values.csv` | 枚举值字典：每个枚举类型的合法取值及中文说明 |
| `field_dictionary.csv` | 字段字典：每个 CSV 数据集的字段定义（本样例自描述了前两个数据集） |
| `dataset_keys.csv` | 键定义：主键、唯一键、稳定排序键 |
| `bundle_manifest.csv` | 数据包清单：文件名、行数、校验和、bundle 封条 |

## ⚠️ 样例状态（使用前必读）

1. **checksum 全部是占位符**（`PLACEHOLDER-RECOMPUTE-BY-VALIDATOR`）。正式发布前必须用
   `scripts/validation/validate_csv_bundle.py` 重算每个文件的 `content_checksum` 和根记录的
   `bundle_checksum`，并把允许的 `(bootstrap_version, expected_bundle_checksum)` 组合固定进校验器发布物。
2. **行数必须与文件实际数据行数一致**——增删样例行后要同步更新 `bundle_manifest.csv` 的 `row_count`。
3. `field_dictionary.csv` 当前只自描述了 `type_dictionary`、`type_values` 两个数据集作为样例；
   正式版必须覆盖 Bundle 内全部数据集（含 `field_dictionary`、`dataset_keys`、`bundle_manifest` 自身）。
4. 硬性格式：UTF-8 无 BOM、LF 换行、非空字段双引号包裹、空值写未加引号的 `\N`、布尔只用 `true/false`。
