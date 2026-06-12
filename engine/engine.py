"""Scene-graph engine for SHADOW OF THE REPUBLIC.

Loads all scenes/chapterNN.json files into one node namespace and runs an
interactive loop in the terminal. See SCHEMA.md for the scene file format.
"""

import json
import os
import re
import sys
import textwrap

from . import effects, expr

WRAP = 78
SAVE_FILE = "savegame.json"

INITIAL_VARS = {
    "name": "Padawan",
    "saber": 30, "force": 30, "command": 30, "guile": 30,
    "dark": 20,
    "master_rel": 55, "havoc_rel": 50, "joren_rel": 45, "nyx_rel": 0,
    "council_rep": 50, "war_score": 50,
    "they": "they", "them": "them", "their": "their", "theirs": "theirs",
    "sir": "commander",
}

# Stats shown by the `stats` command: (label, var) or special handling below.
SKILLS = [("Lightsaber", "saber"), ("Force", "force"),
          ("Command", "command"), ("Guile", "guile")]
RELATIONSHIPS = [("Master Ilara Venn", "master_rel"),
                 ("Captain Havoc", "havoc_rel"),
                 ("Joren Kade", "joren_rel"),
                 ("Sev'ara Nyx", "nyx_rel")]

_INTERP_RE = re.compile(r"\$\{(\w+)\}")


class SceneError(Exception):
    pass


def load_scenes(scene_dir):
    """Load every chapter file; return (nodes, chapter_starts, chapter_titles)."""
    nodes, starts, titles = {}, {}, {}
    paths = sorted(
        p for p in os.listdir(scene_dir)
        if p.startswith("chapter") and p.endswith(".json")
    )
    if not paths:
        raise SceneError("no chapter files found in %s" % scene_dir)
    for path in paths:
        with open(os.path.join(scene_dir, path)) as f:
            data = json.load(f)
        num = data["chapter"]
        starts[num] = data["start"]
        titles[num] = data.get("title", "Chapter %s" % num)
        for node_id, node in data["nodes"].items():
            if node_id in nodes:
                raise SceneError("duplicate node id %r (%s)" % (node_id, path))
            nodes[node_id] = node
    return nodes, starts, titles


class Game:
    def __init__(self, scene_dir, out=sys.stdout, get_input=input):
        self.nodes, self.starts, self.titles = load_scenes(scene_dir)
        self.vars = dict(INITIAL_VARS)
        self.out = out
        self.get_input = get_input
        self.current = None
        self.endings_seen = []

    # ---- text helpers -------------------------------------------------

    def interpolate(self, text):
        def sub(m):
            name = m.group(1)
            if name in self.vars:
                return str(self.vars[name])
            if name[0].isupper() and name.lower() in self.vars:
                return str(self.vars[name.lower()]).capitalize()
            return m.group(0)
        return _INTERP_RE.sub(sub, text)

    def render_text(self, text):
        """text may be a string or a list of strings / {"if","text"} dicts."""
        if isinstance(text, str):
            parts = [text]
        else:
            parts = []
            for seg in text:
                if isinstance(seg, str):
                    parts.append(seg)
                elif "if" not in seg or expr.evaluate(seg["if"], self.vars):
                    parts.append(seg["text"])
        joined = "\n\n".join(p.strip() for p in parts if p.strip())
        return self.wrap(self.interpolate(joined))

    @staticmethod
    def wrap(text):
        out = []
        for para in text.split("\n\n"):
            para = " ".join(para.split())
            out.append(textwrap.fill(para, WRAP))
        return "\n\n".join(out)

    def emit(self, s=""):
        self.out.write(s + "\n")

    # ---- stats screen --------------------------------------------------

    def bar(self, value, width=25):
        filled = int(round(value / 100.0 * width))
        return "[" + "#" * filled + "-" * (width - filled) + "]"

    def show_stats(self):
        v = self.vars
        self.emit()
        self.emit("=" * WRAP)
        self.emit("  %s" % v["name"].upper())
        self.emit("=" * WRAP)
        for label, key in SKILLS:
            self.emit("  %-12s %s %3d" % (label, self.bar(v[key]), v[key]))
        self.emit()
        dark = v["dark"]
        self.emit("  Alignment    %s" % self.bar(dark))
        self.emit("               Light %d%%  /  Dark %d%%" % (100 - dark, dark))
        self.emit()
        for label, key in RELATIONSHIPS:
            if key == "nyx_rel" and v[key] == 0:
                continue
            self.emit("  %-20s %3d" % (label, v[key]))
        self.emit("  %-20s %3d" % ("Council standing", v["council_rep"]))
        self.emit("  %-20s %3d" % ("War effort", v["war_score"]))
        self.emit("=" * WRAP)
        self.emit()

    # ---- save / load -----------------------------------------------------

    def save(self, path=SAVE_FILE):
        with open(path, "w") as f:
            json.dump({"vars": self.vars, "node": self.current,
                       "endings_seen": self.endings_seen}, f, indent=2)

    def load(self, path=SAVE_FILE):
        with open(path) as f:
            data = json.load(f)
        self.vars = data["vars"]
        self.current = data["node"]
        self.endings_seen = data.get("endings_seen", [])

    # ---- main loop -------------------------------------------------------

    def title_screen(self):
        self.emit()
        self.emit("*" * WRAP)
        self.emit("""
        A long time ago in a galaxy far, far away....

                S T A R   W A R S
           SHADOW  OF  THE  REPUBLIC
             A Clone Wars Adventure
""")
        self.emit("*" * WRAP)
        self.emit()
        self.emit(self.wrap(
            "An interactive novel in the style of Choice of Games. Your "
            "choices shape your skills, your friendships, and your place in "
            "the Force. There are no right answers -- only consequences."))
        self.emit()
        self.emit(self.wrap(
            "At any choice prompt you may also type: stats, save, load, "
            "or quit."))
        self.emit()

    def chapter_header(self, num):
        self.emit()
        self.emit("~" * WRAP)
        self.emit("   CHAPTER %s: %s" % (num, self.titles.get(num, "").upper()))
        self.emit("~" * WRAP)
        self.emit()

    def prompt_choice(self, choices):
        while True:
            raw = self.get_input("> ").strip()
            low = raw.lower()
            if low == "stats":
                self.show_stats()
                continue
            if low == "save":
                self.save()
                self.emit("Game saved.")
                continue
            if low == "load":
                if os.path.exists(SAVE_FILE):
                    self.load()
                    self.emit("Game loaded.")
                    return None  # signal restart at loaded node
                self.emit("No save file found.")
                continue
            if low in ("quit", "exit"):
                self.emit("May the Force be with you.")
                sys.exit(0)
            if raw.isdigit() and 1 <= int(raw) <= len(choices):
                return choices[int(raw) - 1]
            self.emit("Enter a number from 1 to %d (or stats/save/load/quit)."
                      % len(choices))

    def visible_choices(self, node):
        out = []
        for choice in node.get("choices", []):
            cond = choice.get("if")
            if cond is None or expr.evaluate(cond, self.vars):
                out.append(choice)
        return out

    def run_ending(self, node):
        ending = node["ending"]
        self.endings_seen.append(ending["id"])
        self.emit()
        self.emit("#" * WRAP)
        self.emit("   THE END: %s" % ending["title"].upper())
        self.emit("#" * WRAP)
        self.emit()
        self.show_stats()
        self.emit(self.wrap(
            "Thank you for playing SHADOW OF THE REPUBLIC. Other paths -- "
            "and other destinies -- await on another playthrough."))
        self.emit()

    def goto_chapter(self, num):
        if num not in self.starts:
            raise SceneError("chapter %s not found" % num)
        self.chapter_header(num)
        return self.starts[num]

    def step(self, node_id):
        """Process one node; return next node id, or None when game over."""
        if node_id not in self.nodes:
            raise SceneError("unknown node %r" % node_id)
        self.current = node_id
        self.save()
        node = self.nodes[node_id]

        for eff in node.get("effects", []):
            effects.apply(eff, self.vars)

        text = node.get("text")
        if text:
            self.emit(self.render_text(text))
            self.emit()

        if "ending" in node:
            self.run_ending(node)
            return None

        if "input" in node:
            spec = node["input"]
            while True:
                raw = self.get_input(self.interpolate(spec.get(
                    "prompt", "?")) + " ").strip()
                if raw:
                    break
            self.vars[spec["var"]] = raw
            self.emit()
            if "goto_chapter" in node:
                return self.goto_chapter(node["goto_chapter"])
            return node["goto"]

        choices = self.visible_choices(node)
        if choices:
            for i, choice in enumerate(choices, 1):
                self.emit("  %d) %s" % (i, self.interpolate(choice["text"])))
            self.emit()
            picked = self.prompt_choice(choices)
            if picked is None:  # a save was loaded mid-prompt
                return self.current
            self.emit()
            for eff in picked.get("effects", []):
                effects.apply(eff, self.vars)
            if "goto_chapter" in picked:
                return self.goto_chapter(picked["goto_chapter"])
            return picked["goto"]

        if "goto_chapter" in node:
            return self.goto_chapter(node["goto_chapter"])
        if "goto" in node:
            return node["goto"]
        raise SceneError("node %r has no way forward" % node_id)

    def run(self):
        self.title_screen()
        if os.path.exists(SAVE_FILE):
            self.emit("A saved game exists. Continue it? (y/n)")
            if self.get_input("> ").strip().lower().startswith("y"):
                self.load()
                self.emit()
                node_id = self.current
            else:
                node_id = self.goto_chapter(1)
        else:
            node_id = self.goto_chapter(1)
        while node_id is not None:
            node_id = self.step(node_id)
