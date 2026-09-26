"""Kiểm tra link tương đối trong mọi file Markdown được Git theo dõi.

Link trỏ ra ngoài repo (ví dụ repo tham chiếu đặt cạnh repo này) chỉ được
liệt kê để biết, không làm CI đỏ, vì máy CI không có các thư mục đó.
"""

import os
import re
import subprocess
import sys
from urllib.parse import unquote

LINK = re.compile(r"\]\(([^)\s]+)\)")
FENCE = re.compile(r"```.*?```", re.S)


def main() -> int:
    root = os.path.realpath(".")
    files = subprocess.run(
        ["git", "ls-files", "*.md"], capture_output=True, text=True, check=True
    ).stdout.split()
    broken, outside = [], []
    for path in files:
        with open(path, encoding="utf-8") as fh:
            text = FENCE.sub("", fh.read())
        for match in LINK.finditer(text):
            target = unquote(match.group(1).split("#")[0])
            if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target):
                continue
            resolved = os.path.realpath(os.path.join(os.path.dirname(path), target))
            if not resolved.startswith(root + os.sep):
                outside.append(f"{path}: {match.group(1)}")
            elif not os.path.exists(resolved):
                broken.append(f"{path}: {match.group(1)}")
    print(f"Đã kiểm tra {len(files)} file Markdown.")
    if outside:
        print(f"{len(outside)} link trỏ ra ngoài repo (bỏ qua):")
        print("\n".join(f"  {x}" for x in outside))
    if broken:
        print(f"{len(broken)} link hỏng:")
        print("\n".join(f"  {x}" for x in broken))
        return 1
    print("Không có link hỏng trong repo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
