#!/usr/bin/env python3
"""Validate scene files.

Usage:
    python3 tools/validate.py                  # validate all of scenes/
    python3 tools/validate.py scenes/chapter03.json   # single file

Single-file mode treats references to other chapters' conventional start
nodes (c<N>_start) and goto_chapter as satisfied; full mode requires every
target to exist and reports unreachable nodes and word counts.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import effects, expr

START_RE = re.compile(r"^c\d+_start$")


def iter_text(text):
    if isinstance(text, str):
        yield text
    elif isinstance(text, list):
        for seg in text:
            if isinstance(seg, str):
                yield seg
            elif isinstance(seg, dict):
                yield seg.get("text", "")


def check_condition(src, where, errors):
    try:
        expr.parse(src)
    except expr.ExprError as e:
        errors.append("%s: %s" % (where, e))


def check_effects(effs, where, errors):
    if not isinstance(effs, list):
        errors.append("%s: effects must be a list" % where)
        return
    for eff in effs:
        try:
            effects.check(eff)
        except effects.EffectError as e:
            errors.append("%s: %s" % (where, e))


def load_file(path, errors):
    try:
        with open(path) as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        errors.append("%s: %s" % (path, e))
        return None
    for key in ("chapter", "start", "nodes"):
        if key not in data:
            errors.append("%s: missing top-level %r" % (path, key))
            return None
    if data["start"] not in data["nodes"]:
        errors.append("%s: start node %r not in nodes" % (path, data["start"]))
    return data


def validate(paths, single_file):
    errors, warnings = [], []
    all_nodes = {}      # id -> (node, path)
    chapters = set()
    targets = []        # (target_id, where)
    chapter_targets = []  # (chapter_num, where)
    words = 0
    endings = []

    for path in paths:
        data = load_file(path, errors)
        if data is None:
            continue
        chapters.add(data["chapter"])
        for node_id, node in data["nodes"].items():
            if node_id in all_nodes:
                errors.append("duplicate node id %r in %s and %s"
                              % (node_id, all_nodes[node_id][1], path))
                continue
            all_nodes[node_id] = (node, path)
            where = "%s:%s" % (os.path.basename(path), node_id)

            text = node.get("text")
            if text is None and "ending" not in node:
                warnings.append("%s: no text" % where)
            for chunk in iter_text(text or ""):
                words += len(chunk.split())
            if isinstance(text, list):
                for seg in text:
                    if isinstance(seg, dict) and "if" in seg:
                        check_condition(seg["if"], where + " (text if)", errors)

            check_effects(node.get("effects", []), where, errors)

            has_forward = False
            if "ending" in node:
                has_forward = True
                e = node["ending"]
                if not isinstance(e, dict) or "id" not in e or "title" not in e:
                    errors.append("%s: ending needs id and title" % where)
                else:
                    endings.append(e["id"])
            if "input" in node:
                spec = node["input"]
                if not isinstance(spec, dict) or "var" not in spec:
                    errors.append("%s: input needs a var" % where)
            if "goto" in node:
                has_forward = True
                targets.append((node["goto"], where))
            if "goto_chapter" in node:
                has_forward = True
                chapter_targets.append((node["goto_chapter"], where))
            for i, choice in enumerate(node.get("choices", [])):
                has_forward = True
                cwhere = "%s choice %d" % (where, i + 1)
                if "text" not in choice:
                    errors.append("%s: no text" % cwhere)
                if "if" in choice:
                    check_condition(choice["if"], cwhere, errors)
                check_effects(choice.get("effects", []), cwhere, errors)
                if "goto" in choice:
                    targets.append((choice["goto"], cwhere))
                elif "goto_chapter" in choice:
                    chapter_targets.append((choice["goto_chapter"], cwhere))
                else:
                    errors.append("%s: no goto/goto_chapter" % cwhere)
            if not has_forward:
                errors.append("%s: dead end (no choices/goto/ending)" % where)

    for target, where in targets:
        if target not in all_nodes:
            if single_file and START_RE.match(target):
                continue
            errors.append("%s: goto target %r does not exist" % (where, target))
    for num, where in chapter_targets:
        if num not in chapters and not single_file:
            errors.append("%s: goto_chapter %s does not exist" % (where, num))

    if not single_file and all_nodes:
        # reachability from chapter 1 start
        graph = {}
        start_by_chapter = {}
        for path in paths:
            with open(path) as f:
                data = json.load(f)
            start_by_chapter[data["chapter"]] = data["start"]
        for node_id, (node, _) in all_nodes.items():
            nbrs = []
            for key in ("goto",):
                if key in node:
                    nbrs.append(node[key])
            if "goto_chapter" in node and node["goto_chapter"] in start_by_chapter:
                nbrs.append(start_by_chapter[node["goto_chapter"]])
            for choice in node.get("choices", []):
                if "goto" in choice:
                    nbrs.append(choice["goto"])
                elif "goto_chapter" in choice and choice["goto_chapter"] in start_by_chapter:
                    nbrs.append(start_by_chapter[choice["goto_chapter"]])
            graph[node_id] = nbrs
        seen = set()
        stack = [start_by_chapter[min(start_by_chapter)]]
        while stack:
            cur = stack.pop()
            if cur in seen or cur not in graph:
                continue
            seen.add(cur)
            stack.extend(graph[cur])
        for node_id in sorted(set(all_nodes) - seen):
            warnings.append("unreachable node: %s" % node_id)

    return errors, warnings, len(all_nodes), words, endings


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    args = sys.argv[1:]
    if args:
        paths, single = args, True
    else:
        scene_dir = os.path.join(root, "scenes")
        paths = sorted(
            os.path.join(scene_dir, p) for p in os.listdir(scene_dir)
            if p.startswith("chapter") and p.endswith(".json"))
        single = False

    errors, warnings, node_count, words, endings = validate(paths, single)
    for w in warnings:
        print("WARN: %s" % w)
    for e in errors:
        print("ERROR: %s" % e)
    print()
    print("%d node(s), ~%d words of prose, %d ending(s)"
          % (node_count, words, len(endings)))
    if endings:
        print("endings: %s" % ", ".join(sorted(endings)))
    if errors:
        print("FAILED with %d error(s)" % len(errors))
        sys.exit(1)
    print("OK (%d warning(s))" % len(warnings))


if __name__ == "__main__":
    main()
