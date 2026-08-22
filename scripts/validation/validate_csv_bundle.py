#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_csv_bundle.py —— CsvBundle 校验器（骨架样例）

职责（契约见 references/contracts/csv-schema.md 与 workflow-model-design.md §11.4）：
1. 按固定 bootstrap 契约解析列集，bootstrap 版本不匹配立即失败；
2. 验证 bundle_manifest.csv：唯一 bundle-root 记录、file 行完整性、行数一致；
3. 验证每个登记文件的存在性与行数；
4. 复算 content_checksum 与 bundle_checksum（TODO，见下）；
5. 验证字段字典、类型字典、外键引用（TODO）。

用法：
    python validate_csv_bundle.py --input-bundle <目录> --work-root <授权目录>

遇到未登记字段、缺字段、非法状态迁移或版本不兼容必须失败退出（非 0），
不得忽略或推测列含义。
"""
import argparse
import csv
import sys
from pathlib import Path

# 校验器发布物中外部固定的允许 (bootstrap_version, expected_bundle_checksum) 组合。
# 正式发布前必须用真实 bootstrap Bundle 重算并写入此处；当前为样例占位。
TRUSTED_BOOTSTRAP = {
    # "1.0.0": "<64位小写十六进制 bundle checksum>",
}

MANIFEST_REQUIRED_COLUMNS = [
    "entry_type", "bundle_id", "file_name", "dataset_name", "record_type",
    "contract_version", "row_count", "content_checksum", "bundle_checksum",
    "generated_at", "source_ref",
]


class BundleValidationError(Exception):
    """任何校验失败都抛出本异常；禁止降级为警告。"""


def read_csv(path: Path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def validate_manifest(bundle_dir: Path) -> list[dict]:
    manifest_path = bundle_dir / "bundle_manifest.csv"
    if not manifest_path.is_file():
        raise BundleValidationError(f"缺少 bundle_manifest.csv: {bundle_dir}")
    with open(manifest_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
    missing = [c for c in MANIFEST_REQUIRED_COLUMNS if c not in (header or [])]
    if missing:
        raise BundleValidationError(f"manifest 缺少必需列: {missing}")

    rows = read_csv(manifest_path)
    roots = [r for r in rows if r["entry_type"] == "bundle-root"]
    if len(roots) != 1:
        raise BundleValidationError(f"bundle-root 记录必须恰有一条，实际 {len(roots)} 条")
    files = [r for r in rows if r["entry_type"] == "file"]
    if not files:
        raise BundleValidationError("manifest 未登记任何 file 记录")
    bundle_ids = {r["bundle_id"] for r in rows}
    if len(bundle_ids) != 1:
        raise BundleValidationError(f"bundle_id 不一致: {bundle_ids}")
    return rows


def validate_files(bundle_dir: Path, manifest_rows: list[dict]) -> None:
    for row in (r for r in manifest_rows if r["entry_type"] == "file"):
        path = bundle_dir / row["file_name"]
        if not path.is_file():
            raise BundleValidationError(f"manifest 登记的文件不存在: {row['file_name']}")
        rows = read_csv(path)
        actual = len(rows)
        declared = int(row["row_count"])
        if actual != declared:
            raise BundleValidationError(
                f"行数不一致: {row['file_name']} manifest={declared} 实际={actual}")
        # TODO: 复算 content_checksum（SHA-256，64 位小写十六进制）并与 manifest 比对。
        # TODO: 校验 file 记录的 bundle_checksum 必须为规范 null \N。
        # TODO: bundle-root 的 bundle_checksum 对全部 file 记录规范投影复算。


def main() -> int:
    parser = argparse.ArgumentParser(description="CsvBundle 校验器（骨架）")
    parser.add_argument("--input-bundle", required=True, help="待校验的 Bundle 目录")
    parser.add_argument("--work-root", required=True, help="用户授权的外置工作根目录")
    args = parser.parse_args()

    bundle_dir = Path(args.input_bundle).resolve()
    work_root = Path(args.work_root).resolve()
    if not bundle_dir.is_dir():
        print(f"FAIL: 输入目录不存在: {bundle_dir}", file=sys.stderr)
        return 2
    # 所有写入目标必须位于 work_root 内；本脚本只读校验，不产生写入。
    try:
        rows = validate_manifest(bundle_dir)
        validate_files(bundle_dir, rows)
    except BundleValidationError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1

    print(f"OK: bundle={bundle_dir.name} 登记文件 {len(rows) - 1} 个（骨架校验通过；checksum 复算待实现）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
