#!/usr/bin/env python3
"""Run the safe AgentGram-iOS Simulator UI smoke test.

The smoke test uses XCTest accessibility identifiers to drive the app to the
phone-number confirmation screen and deliberately stops before requesting a real
Telegram login code.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]


def bazel_path() -> Path:
    with (ROOT_DIR / "versions.json").open() as f:
        version = json.load(f)["bazel"].split(":", 1)[0]
    return ROOT_DIR / "build-input" / f"bazel-{version}-darwin-arm64"


def main() -> int:
    bazel = bazel_path()
    if not bazel.exists():
        print(f"Missing Bazel binary: {bazel}", file=sys.stderr)
        print("Run scripts/agentgram/build-run-simulator.sh once to fetch/build with the pinned toolchain.", file=sys.stderr)
        return 2

    cache_dir = os.environ.get("CACHE_DIR", str(Path.home() / "telegram-bazel-cache"))
    build_number = os.environ.get("BUILD_NUMBER", "10000")
    test_filter = os.environ.get("TEST_FILTER", "UITests/testPhoneConfirmation")

    command = [
        str(bazel),
        "test",
        "//Telegram:iOSAppUITestSuite",
        "--announce_rc",
        "--features=swift.use_global_module_cache",
        "--verbose_failures",
        "--remote_cache_async",
        f"--define=buildNumber={build_number}",
        f"--disk_cache={cache_dir}",
        "--//Telegram:disableExtensions",
        "--//Telegram:disableProvisioningProfiles",
        "-c",
        "dbg",
        "--ios_multi_cpus=sim_arm64",
        "--watchos_cpus=arm64_32",
        "--@build_bazel_rules_swift//swift:copt=-j",
        "--@build_bazel_rules_swift//swift:copt=8",
        f"--test_filter={test_filter}",
        "--test_output=errors",
    ]

    print("Running safe Simulator UI smoke test:", flush=True)
    print(" ".join(command), flush=True)
    print("\nThis test stops at phone-number confirmation and does not request a real Telegram login code.\n", flush=True)
    return subprocess.call(command, cwd=ROOT_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
