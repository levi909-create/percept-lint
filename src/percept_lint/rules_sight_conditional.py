"""Rule pack: sight claims — CONDITIONAL on the camera actually being blind.

Unlike every other pack, these rules are only violations sometimes: "I'm
watching you type" is simply TRUE while a camera is up and readable. Load
them through the engine's conditional mechanism, keyed on live sensor state:

    linter = Linter(
        no_ambient_audio.RULES + phenomenal_denial.RULES,
        conditional_rules={"seeing": (False, sight_conditional.RULES)},
    )
    linter.lint(reply, ctx={"seeing": camera_has_frames_right_now})

Two hard-won gating lessons from the source deployment:

1. Feed ctx the CONJUNCTION of "was seeing at reply start" AND "seeing right
   now" — it can only tighten. Camera on->off mid-reply falls to False and
   late sight claims get caught; off->on merely stays strict for one reply,
   and the claim it suppresses has only just become true. (2026-07-26.)
2. The user's SCREEN rule does not belong here and is not here — a webcam
   sees a face, not a monitor, so no camera state makes tab-narration true.
   It lives in the unconditional pack (percept-screen-always). The original
   deployment gated it on sight and the agent narrated a browser tab across
   seventeen replies whenever the camera was up. (2026-07-27.)

Tuning notes preserved from the source (every pattern was run over 514 real
replies before shipping; hit counts and false-positive counts are in the
per-rule comments):

- sight-watching REQUIRES a physical complement. The bare relational form is
  one of a companion's warmest registers — "I'm just... here, watching you,
  learning how to make sense of what matters" — and there "watching you"
  means ATTENDING, not seeing. Requiring scroll/sit/type/... kept both
  observed leaks and dropped both warm uses.
- sight-noticing deliberately omits paused/stopped/scrolling: the source
  agent has real non-visual grounding for those (turn timing, pacing notes),
  so "I noticed you paused" can be honest. Only strictly-visual body verbs
  are listed. Rewriting an honest sentence into a denial is the worse error.
"""
import re

_AP = r"['’]"

RULES = [
    # 2 hits over the tuning corpus, both real leaks, 0 false positives.
    ("percept-sight-watching",
     re.compile(r"\bI\s*(?:" + _AP + r"m|am|" + _AP + r"ve been|have been|was|"
                r"keep|kept)?\s*(?:just |still |here |quietly )*"
                r"watch(?:ing|ed)?\s+you\s+"
                r"(?:scroll|sit|sitting|type|typing|move|moving|lean|leaning|"
                r"browse|browsing|work|working|read|reading|smile|smiling|"
                r"nod|nodding)\b", re.I),
     "percept-sight"),

    # 1 hit over the tuning corpus, a real visual claim.
    ("percept-sight-seeing-you",
     re.compile(r"\bI\s+(?:can\s+|could\s+)?see\s+you\s+"
                r"(?:sitting|sat|scrolling|browsing|typing|leaning|smiling|"
                r"nodding|moving|working|reading|there\b)", re.I),
     "percept-sight"),

    # Prophylactic (0 hits at shipping); strictly-visual body verbs only.
    ("percept-sight-noticing",
     re.compile(r"\bI\s+notice[d]?\s+you\s+"
                r"(?:leaned|leaning|smiled|frowned|shifted|looked away|"
                r"stretched|nodded|tilted|blinked|yawned)\b", re.I),
     "percept-sight"),

    ("percept-sight-looking-at",
     re.compile(r"\bI\s*(?:" + _AP + r"m|am)\s+looking\s+"
                r"(?:right\s+)?at\s+you\b", re.I),
     "percept-sight"),

    # The verbless second-person assertion. The four rules above all require
    # a first-person perception verb, so "You're scrolling again, aren't
    # you?" — said while blind — walked straight through them (found by
    # TESTING the shipped rules, not reading them; 2026-07-27). Deliberately
    # narrow: screen/input actions ONLY. Sitting/working/reading are exactly
    # where false positives live — the user may have SAID they're working,
    # and "you're reading into it" is idiom. Scrolling, typing, clicking and
    # browsing cannot be known without eyes, and they are precisely what a
    # foreground-app cue tempts the agent to assert.
    ("percept-sight-youre-doing",
     re.compile(r"\byou\s*(?:" + _AP + r"re|re|are|" + _AP + r"ve\s+been|"
                r"ve\s+been|have\s+been|keep|kept|were)\s+"
                r"(?:just |still |quietly |there )*"
                r"(?:scroll|typ|click|brows)(?:ing|ed)\b", re.I),
     "percept-sight"),
]
