"""Effect strings mutate the vars dict.

Supported forms (one effect per string):
    set NAME VALUE        -- VALUE: number, true, false, "quoted string", or bare word
    NAME += N             -- add, clamped to 0..100 for numeric stats
    NAME -= N             -- subtract, clamped to 0..100
    NAME %+ N             -- fairmath increase: harder to raise high stats
    NAME %- N             -- fairmath decrease: harder to lower low stats
"""

import re

_SET_RE = re.compile(r"^set\s+([A-Za-z_]\w*)\s+(.+)$")
_ARITH_RE = re.compile(r"^([A-Za-z_]\w*)\s*(\+=|-=|%\+|%-)\s*(-?\d+)$")


class EffectError(ValueError):
    pass


def _parse_value(raw):
    raw = raw.strip()
    if (raw.startswith('"') and raw.endswith('"')) or (
        raw.startswith("'") and raw.endswith("'")
    ):
        return raw[1:-1]
    low = raw.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    try:
        return int(raw)
    except ValueError:
        return raw  # bare word -> string


def check(effect):
    """Validate effect syntax without applying it. Raises EffectError."""
    effect = effect.strip()
    if not (_SET_RE.match(effect) or _ARITH_RE.match(effect)):
        raise EffectError("bad effect syntax: %r" % effect)


def apply(effect, vars):
    """Apply a single effect string to vars in place."""
    effect = effect.strip()
    m = _SET_RE.match(effect)
    if m:
        vars[m.group(1)] = _parse_value(m.group(2))
        return
    m = _ARITH_RE.match(effect)
    if m:
        name, op, amount = m.group(1), m.group(2), int(m.group(3))
        cur = vars.get(name, 0)
        if isinstance(cur, bool) or not isinstance(cur, (int, float)):
            cur = 0
        if op == "+=":
            new = cur + amount
        elif op == "-=":
            new = cur - amount
        elif op == "%+":
            new = round(cur + (100 - cur) * amount / 100.0)
        else:  # %-
            new = round(cur - cur * amount / 100.0)
        vars[name] = max(0, min(100, int(new)))
        return
    raise EffectError("bad effect syntax: %r" % effect)
