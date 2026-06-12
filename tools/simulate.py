#!/usr/bin/env python3
"""Random-walk playtester: plays N full games with random choices and
reports endings reached, node coverage, and any crashes.

Usage: python3 tools/simulate.py [N] [--seed S]
"""

import io
import os
import random
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import effects, expr
from engine.engine import Game


class Walker(Game):
    """Headless Game that picks choices at random and never touches disk."""

    def __init__(self, scene_dir, rng):
        super().__init__(scene_dir, out=io.StringIO(),
                         get_input=lambda *_: "")
        self.rng = rng
        self.visited = set()
        self.ending = None

    def save(self, path=None):
        pass

    def step(self, node_id):
        if node_id not in self.nodes:
            raise RuntimeError("unknown node %r" % node_id)
        self.visited.add(node_id)
        self.current = node_id
        node = self.nodes[node_id]
        for eff in node.get("effects", []):
            effects.apply(eff, self.vars)
        if node.get("text"):
            self.render_text(node["text"])  # exercise interpolation/conditions
        if "ending" in node:
            self.ending = node["ending"]["id"]
            return None
        if "input" in node:
            self.vars[node["input"]["var"]] = "Tester"
            if "goto_chapter" in node:
                return self.goto_chapter(node["goto_chapter"])
            return node["goto"]
        choices = self.visible_choices(node)
        if choices:
            picked = self.rng.choice(choices)
            for eff in picked.get("effects", []):
                effects.apply(eff, self.vars)
            if "goto_chapter" in picked:
                return self.goto_chapter(picked["goto_chapter"])
            return picked["goto"]
        if "goto_chapter" in node:
            return self.goto_chapter(node["goto_chapter"])
        if "goto" in node:
            return node["goto"]
        raise RuntimeError("dead end at %r" % node_id)

    def goto_chapter(self, num):
        return self.starts[num]

    def play(self, max_steps=5000):
        node_id = self.starts[min(self.starts)]
        steps = 0
        while node_id is not None:
            steps += 1
            if steps > max_steps:
                raise RuntimeError("loop suspected; last node %r"
                                   % self.current)
            node_id = self.step(node_id)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    runs = int(args[0]) if args else 200
    seed = 1138
    for i, a in enumerate(sys.argv):
        if a == "--seed":
            seed = int(sys.argv[i + 1])
    rng = random.Random(seed)
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scene_dir = os.path.join(root, "scenes")

    endings = Counter()
    coverage = set()
    failures = []
    word_counts = []
    for run in range(runs):
        walker = Walker(scene_dir, random.Random(rng.random()))
        try:
            walker.play()
            endings[walker.ending] += 1
            coverage |= walker.visited
        except Exception as e:
            failures.append((run, walker.current, e))

    total_nodes = len(Walker(scene_dir, rng).nodes)
    print("%d runs, %d failures" % (runs, len(failures)))
    for run, node, e in failures[:10]:
        print("  FAIL run %d at node %r: %s" % (run, node, e))
    print("node coverage: %d/%d (%.0f%%)"
          % (len(coverage), total_nodes, 100.0 * len(coverage) / total_nodes))
    print("endings reached:")
    for ending, count in endings.most_common():
        print("  %4d  %s" % (count, ending))
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
