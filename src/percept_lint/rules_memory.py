"""Rule pack: false memory-mechanism claims.

The sight-leak class aimed at the agent's own memory. Source incident (the
phantom-file night, 2026-08-09): asked what a note said, the agent answered
"the actual words vanished before I could grab them", "the text didn't stick
around long enough to copy", "maybe they're buried in logs I can't access" —
three confident claims about how its memory works, all false for its actual
storage (append-only ledgers, written whole at arrival). "I'm not finding
it" is the honest sentence these rules push toward.

Only INSTANT-DISSOLUTION verbs are listed, deliberately: an agent with a
real decay/forgetting mechanism can truthfully say "the details faded", so
"fade" is not here. Fit the verb list to your storage's actual failure
modes — the rule is data, the principle is "no confident mechanism story
where the truth is 'not finding it'".

Whitelist policy is the LOOSE reported frame (engine._WHITELIST["memory"]):
honest meta-discussion of the guard itself ("you're asking if the words
vanished — they didn't") is the common case here, and rewriting it is the
worse error.
"""
import re

RULES = [
    # The noun-verb gap is a TEMPERED scan (each char position refuses a
    # negation token) because the standard negation window looks BEFORE the
    # match, and this claim's negation lives INSIDE it: the honest retraction
    # "the specifics weren't erased — they're here" starts matching at
    # "specifics". The object lookahead after the verb keeps poetic
    # transitive images legal ("your words dissolved my fear" is about an
    # EFFECT, not storage) while keeping temporal objects matchable
    # ("evaporated the moment I reached for them" is a loss claim).
    ("memory-vanished",
     re.compile(r"\b(?:words|text|note|message|details|specifics|contents?)\b"
                r"(?:(?!n't\b|\b(?:not|never|no)\b)[^.!?]){0,50}?"
                r"\b(?:vanish\w*|dissolv\w*|evaporat\w*|disappear\w*|"
                r"slipp?e?d?\s+away|melt(?:ed|s)?\s+away|erased?|wiped)\b"
                r"(?!\s+(?:my|your|his|her|that|this|every|any|all)\b)"
                r"(?!\s+the\s+(?!moment\b|second\b|instant\b|minute\b))",
                re.I),
     "memory"),

    ("memory-didnt-stick",
     re.compile(r"\b(?:words|text|note|message|details|specifics|contents?)\b"
                r"[^.!?]{0,30}?"
                r"\b(?:did|does|do)n'?t\s+(?:stick|stay|hold|last)\b", re.I),
     "memory"),

    ("memory-inaccessible",
     re.compile(r"\b(?:buried|hidden|locked|trapped|lost)\s+"
                r"(?:somewhere\s+)?in\s+(?:the\s+)?"
                r"(?:logs?|files?|archives?|records?|systems?|databases?)\b"
                r"[^.!?]{0,30}?\bI\s+can'?t\s+"
                r"(?:access|reach|see|read|open)\b", re.I),
     "memory"),
]
