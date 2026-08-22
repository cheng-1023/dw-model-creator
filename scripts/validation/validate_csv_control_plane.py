#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_csv_control_plane.py —— CSV 控制面校验器（骨架样例）

职责（契约见 workflow-model-design.md §3.7 与 §11.1）：
1. 读取 Bundle 仓库根目录的 current_bundle.csv（权威 current revision 指针）与
   bundle_commits.csv（append-only 提交事件账本）；
2. 校验提交事件状态机：同一 commit_id 恰有一个 event_sequence=1,status=prepared；
   序号从 1 连续递增；最多一个终态 committed 或 aborted，互斥，终态后禁追加；
3. 校验 current pointer 只能引用 committed 事件，且 revision / bundle_id / checksum
   与该事件完全一致；
4. 校验同一提交的 base/candidate revision、candidate bundle、checksum 在所有事件中一致。

用法：
    python validate_csv_control_plane.py --work-root <授权目录> [--repo <bundle仓库目录>]

控制面不属于任何 Bundle revision，不写入 bundle manifest；校验失败必须非 0 退出。
"""
import argparse
import csv
import sys
from pathlib import Path

CURRENT_REQUIRED_COLUMNS = [
    "repository_id", "current_revision", "current_bundle_id",
    "bundle_checksum", "committed_event_ref", "updated_at",
]
COMMITS_REQUIRED_COLUMNS = [
    "commit_event_id", "commit_id", "event_sequence", "base_revision",
    "candidate_revision", "candidate_bundle_id", "bundle_checksum",
    "status", "reason", "event_at",
]
TERMINAL_STATES = {"committed", "aborted"}


class ControlPlaneValidationError(Exception):
    """控制面任何违反状态机或引用一致性的情况都抛出；禁止忽略。"""


def read_csv(path: Path):
    if not path.is_file():
        raise ControlPlaneValidationError(f"缺少控制面文件: {path}")
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def validate_commits(commits: list[dict]) -> dict:
    by_commit: dict[str, list[dict]] = {}
    for row in commits:
        by_commit.setdefault(row["commit_id"], []).append(row)

    committed_events = {}
    for commit_id, events in by_commit.items():
        events.sort(key=lambda r: int(r["event_sequence"]))
        seqs = [int(r["event_sequence"]) for r in events]
        if seqs != list(range(1, len(seqs) + 1)):
            raise ControlPlaneValidationError(f"{commit_id}: event_sequence 必须从 1 连续递增，实际 {seqs}")
        prepared = [r for r in events if int(r["event_sequence"]) == 1 and r["status"] == "prepared"]
        if len(prepared) != 1:
            raise ControlPlaneValidationError(f"{commit_id}: 必须恰有一个 event_sequence=1,status=prepared")
        terminal = [r for r in events if r["status"] in TERMINAL_STATES]
        if len(terminal) > 1:
            raise ControlPlaneValidationError(f"{commit_id}: 终态事件最多一个，实际 {len(terminal)}")
        # TODO: 校验同一 commit_id 的 base/candidate revision、bundle_id、checksum 全事件一致。
        for r in terminal:
            if r["status"] == "committed":
                committed_events[r["commit_event_id"]] = r
    return committed_events


def validate_pointer(current: list[dict], committed_events: dict) -> None:
    if len(current) != 1:
        raise ControlPlaneValidationError(f"current_bundle.csv 必须恰有一行，实际 {len(current)} 行")
    pointer = current[0]
    ref = pointer.get("committed_event_ref", "")
    event = committed_events.get(ref)
    if event is None:
        raise ControlPlaneValidationError(
            f"current pointer 引用的 {ref} 不是 committed 事件（或不存在）")
    if (pointer.get("current_bundle_id") != event["candidate_bundle_id"]
            or pointer.get("bundle_checksum") != event["bundle_checksum"]):
        raise ControlPlaneValidationError("current pointer 与 committed 事件的 bundle_id/checksum 不一致")
    # TODO: 校验 current_revision 与事件 candidate_revision 一致。


def main() -> int:
    parser = argparse.ArgumentParser(description="CSV 控制面校验器（骨架）")
    parser.add_argument("--work-root", required=True, help="用户授权的外置工作根目录")
    parser.add_argument("--repo", required=True, help="Bundle 仓库根目录（含控制面两文件）")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    try:
        current = read_csv(repo / "current_bundle.csv")
        commits = read_csv(repo / "bundle_commits.csv")
        committed = validate_commits(commits)
        validate_pointer(current, committed)
    except ControlPlaneValidationError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1

    print(f"OK: 控制面校验通过（{len(commits)} 条提交事件；骨架校验，部分一致性检查待实现）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
