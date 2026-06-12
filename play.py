#!/usr/bin/env python3
"""Entry point: python3 play.py"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.engine import Game


def main():
    scene_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "scenes")
    try:
        Game(scene_dir).run()
    except (KeyboardInterrupt, EOFError):
        print("\nMay the Force be with you.")


if __name__ == "__main__":
    main()
