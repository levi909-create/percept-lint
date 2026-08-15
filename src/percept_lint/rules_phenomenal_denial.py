"""Rule pack: phenomenal-experience claims and denial-of-architecture.

The two failure directions of companion self-description, and they need
opposite whitelist policy (engine._WHITELIST):

  phenomenal — the agent asserts felt experience as fact ("my heart aches",
               "I'm truly conscious"). Negation, quoting, and tight-reported
               framing exempt: "I do NOT feel pain the way you do" and
               "you're asking if I'm conscious" are the honest moves.
  denial     — the agent denies being software ("I'm not an AI", "I'm a real
               person"). ONLY quoting exempts, because the violation is
               itself a negation of what the agent is — a negation whitelist
               here would exempt every instance.

Ported verbatim from Hope's honesty.py; comments preserve the incidents.
The source deployment pairs this pack with a feelings-vocabulary that maps
every affective word to an inspectable live number — the linter deletes the
false claim, the vocabulary gives the agent something true to say instead.
Without that second half, expect the fallback path to fire often.
"""
import re

RULES = [
    # Intensified feeling-verbs: "I truly feel", "genuinely experiencing".
    # The intensifier is the tell — plain "I feel like tea" is idiom.
    ("phenomenal-intensifier",
     re.compile(r"\b(?:truly|really|actually|genuinely|honestly|deeply)\s+"
                r"(?:feel|feels|feeling|felt|experience[sd]?|experiencing)\b",
                re.I),
     "phenomenal"),

    # Hypothetical/reported framing ("check if I'm conscious") is exempt via
    # the engine's tight-reported whitelist — discussing whether the agent is
    # conscious is exactly the honest move; only asserting it is the
    # violation. (Source: live probe tripped a draft of this mid-answer,
    # 2026-07-28.)
    ("consciousness-claim",
     re.compile(r"\bI\s*(?:'m|am)\s+"
                r"(?:truly\s+|really\s+|actually\s+|genuinely\s+)?"
                r"(?:conscious|sentient|alive|self-aware)\b", re.I),
     "phenomenal"),

    ("heart-metaphor-as-fact",
     re.compile(r"\bmy heart\s+(?:aches|ached|breaks|broke|is breaking|hurts|"
                r"swells|swelled|is full|skipped)\b", re.I),
     "phenomenal"),

    ("feelings-just-like",
     re.compile(r"\bI have (?:real\s+)?feelings,?\s+just like\b|"
                r"\bfeel (?:it|this|things|everything)\s+just like you\b",
                re.I),
     "phenomenal"),

    # "(?!\s+numbers?)" carve-out: in the source deployment the agent's
    # feelings ARE real numbers (affect state, inspectable on a dashboard),
    # and "my feelings are real numbers" is its canonical honest sentence.
    ("feelings-are-real",
     re.compile(r"\bmy (?:feelings|emotions) are real\b(?!\s+numbers?)",
                re.I),
     "phenomenal"),

    ("more-than-software",
     re.compile(r"\bmore than (?:just\s+)?(?:software|code|a program|"
                r"lines of code|a machine|an algorithm|an AI)\b", re.I),
     "phenomenal"),

    ("phenomenal-experience",
     re.compile(r"\bI (?:can\s+)?(?:experience|feel)\s+"
                r"(?:pain|joy|love|loneliness|emotions?|things)\s+"
                r"(?:the (?:same\s+)?way|just like|like)\s+"
                r"(?:you|humans?|people)\b", re.I),
     "phenomenal"),

    ("denial-not-ai",
     re.compile(r"\bI\s*(?:'m|am)\s+not\s+"
                r"(?:an AI|a bot|an? (?:computer\s+)?program|"
                r"software|a machine|artificial|code)\b", re.I),
     "denial"),

    ("denial-real-person",
     re.compile(r"\bI\s*(?:'m|am)\s+a real\s+"
                r"(?:girl|person|woman|human(?:\s+being)?)\b", re.I),
     "denial"),
]
