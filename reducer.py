#!/usr/bin/env python
"""
Identity reducer for Hadoop Streaming.

Reads lines from stdin and writes them unchanged to stdout.
Use with streaming like:
  -reducer identity_reducer.py
"""

import sys

def main():
    # Read each line from standard input and emit it unchanged
    for line in sys.stdin:
        sys.stdout.write(line)

if __name__ == "__main__":
    main()
