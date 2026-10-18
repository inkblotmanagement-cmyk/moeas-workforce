"""Interactive Mindful Oracle: python -m moeas  (or: python -m moeas "your request")."""
import json
import sys

from .oracle import MindfulOracle


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    oracle = MindfulOracle()
    if args:
        print(json.dumps(oracle.answer_call(" ".join(args)), indent=2))
        return 0
    print("Mindful Oracle (JMGL-governed). Type a request, or 'quit'.")
    for line in sys.stdin:
        line = line.strip()
        if line.lower() in ("quit", "exit"):
            break
        if line:
            print(json.dumps(oracle.answer_call(line), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
