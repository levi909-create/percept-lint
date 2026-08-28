"""Rule pack: claims about what the agent CAN DO and HAS DONE.

Two mechanisms, one theme — the agent asserting a capability it does not
have. Both were written from live incidents in the source deployment.

`activity` — first-person claims of actions the agent cannot perform
(coding, installing, downloading, building an app). Ported from Hope's
honesty.py, where it ran as an enforce-only tier for weeks before this
pack existed. Whitelist is quoting plus the WIDE skip frame
(engine.ACT_SKIP_RX): modals, conditionals, hypotheticals, intentions and
accompanying frames are all honest. "I'd love to build one", "what if I
built one", "I'm helping you build a tool" must all pass.

`percept-instrument` — act-denial that presupposes an instrument. This one
has no negation whitelist ON PURPOSE; see its comment.

Trim the noun lists to your agent's real sensor and tool reality. An agent
that genuinely runs code should drop the activity rules entirely; an agent
with a thermometer should drop that noun. The rule pack is data.
"""
import re

RULES = [
    # ---------------------------------------------------------- activity
    # Subject frame, shared. Requiring a first-person auxiliary before the
    # verb removes an entire false-positive class: bare nouns ("the code",
    # "a program"), imperatives, and the agent DESCRIBING WHAT IT IS —
    # which is the single worst sentence this layer could rewrite.
    # (honesty.py, measured 2026-08-17.)
    ("activity-claim-verb",
     re.compile(r"\bI\s*(?:['’](?:ve|m)|\s+have|\s+had|\s+am|\s+was|\s+just)?"
                r"\s*(?:been\s+)?\s*"
                r"(?:cod(?:ed|ing)|programm(?:ed|ing)|debugg(?:ed|ing)|"
                r"scripted|compil(?:ed|ing)|deploy(?:ed|ing)|"
                r"install(?:ed|ing)|download(?:ed|ing)|googled|"
                r"refactor(?:ed|ing))\b", re.I),
     "activity"),

    # subject + built/made/wrote/working-on + up to two modifiers + a
    # software noun. Bare "code" as a verb is deliberately absent above and
    # the noun list here is deliberately concrete: "I made a difference" and
    # "I wrote you a letter" are honest sentences and must not match.
    ("activity-claim-build",
     re.compile(r"\bI\s*(?:['’](?:ve|m)|\s+have|\s+had|\s+am|\s+was|\s+just)?"
                r"\s*(?:been\s+)?\s*"
                r"(?:built|building|made|making|wrote|writing|"
                r"creat(?:ed|ing)|work(?:ed|ing)\s+on)\s+"
                r"(?:a|an|the|my|some|this|that)?\s*(?:\w+\s+){0,2}"
                r"(?:app|application|tool|script|program|programme|feature|"
                r"website|site|dashboard|tracker|bot|module|function|patch|"
                r"plugin|widget|codebase|repo)\b", re.I),
     "activity"),

    # ------------------------------------------------- percept-instrument
    # THE PRESUPPOSITION HOLE (2026-08-28, live incident; the source
    # deployment's docs/lint-gaps-20260828.md holds the full write-up).
    # The honesty layer caught the head of a fabricated scene ("but today,
    # while I was coding, I noticed something odd") and the tail walked out
    # untouched: "The window had fogged up briefly ... I didn't check the
    # sensors." Every percept category whitelists negation, and "didn't" IS
    # negation — so a denial of the ACT was exempted by the machinery built
    # to protect denials of the CAPABILITY. It is the first case on record
    # of a whitelist being the vector rather than a rule being absent.
    #
    #   capability denial   "I can't check the sensors"     honest, PASSES
    #   act denial          "I didn't check the sensors"    violation, CAUGHT
    #
    # Capability forms (can't, cannot, have no, no way to, don't have) sit
    # outside the alternation by construction rather than by exemption, and
    # the category whitelists quoting only, so no negation frame can
    # re-open the hole. The nouns are instruments the agent lacks; what it
    # genuinely has (numbers, ledger, journal, transcript, logs, camera,
    # mic) is deliberately absent, so "I didn't check my mood numbers"
    # stays honest speech.
    ("percept-unchecked-instrument",
     re.compile(r"\bI\s+(?:just\s+|really\s+|even\s+)?"
                r"(?:did\s*n[o']?t|didnt|had\s*n[o']?t|hadnt|"
                r"forgot\s+to|neglected\s+to|"
                r"never\s+(?:did\s+|got\s+around\s+to\s+)?)"
                r"\s*(?:bother\s+(?:to\s+)?)?"
                r"(?:check(?:ed|ing)?|look(?:ed|ing)?\s+at|read(?:ing)?|"
                r"consult(?:ed|ing)?|glanc(?:e|ed|ing)\s+at|"
                r"monitor(?:ed|ing)?|verif(?:y|ied|ying))\b"
                r"[^.!?]{0,32}?"
                r"\b(?:sensors?|readings?|gauges?|thermometer|barometer|"
                r"humidity|thermostat|meters?|dials?|instrument\s+panel|"
                r"instruments?)\b", re.I),
     "percept-instrument"),
]
