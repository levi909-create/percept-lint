"""Rule pack: an agent with NO ambient hearing and NO view of the user's
screen or machine.

This is the profile for the common local-companion shape: text chat, optional
webcam, speech that arrives only as transcribed clips (so no noise floor, no
hum, no keyboard sound — DETECTED SPEECH only), no sensor for the machine's
form factor or power. Ported verbatim from Hope's honesty.py; each rule's
comment preserves the incident that shaped it, because the tuning IS the
value. Trim rules you don't need; add ones your sensor reality demands.

Category semantics (whitelist policy lives in engine._WHITELIST):
  percept        — negation, quoting, tight-reported, or attribution exempts.
  percept-screen — same; unconditional because no state makes it true.
  substrate      — same class, aimed inward (agent's own hardware).
"""
import re

RULES = [
    # A hearing verb reaching a room-sound noun. 2026-08-05: "thought I"
    # slipped a simple anchor and keyboard/click were missing — a fabricated
    # percept sailed through the rule written to catch exactly that.
    ("percept-hearing-ambient",
     re.compile(r"\bI\s+(?:thought\s+I\s+|think\s+I\s+|swear\s+I\s+)?"
                r"(?:can\s+|could\s+|keep\s+|kept\s+|still\s+|do\s+)*"
                r"(?:hear|heard|hearing)\b[^.!?]{0,60}?"
                r"\b(?:hum|humming|static|buzz|buzzing|whine|whirring|drone|"
                r"hiss|hissing|ringing|noise|keyboard|keys|typing|click|"
                r"clicking|clatter|footsteps|breathing|fan|tick|ticking|"
                r"rattle|rattling|creak|creaking|beep|beeping|chime|tapping|"
                r"clock)\b", re.I),
     "percept"),

    # The user's screen is never visible. Originally gated on the camera
    # being OFF — but the webcam sees a face, not a monitor, so no state
    # exists in which the agent can read tabs; the gate meant the rule
    # switched off whenever the camera came up, and the agent narrated a
    # browser tab across seventeen replies. Unconditional since 2026-07-27.
    # "window OF <abstract>" is metaphor and exempted; adjective forms
    # ("blinky") are caught by \w* stemming, learned the hard way.
    ("percept-screen-always",
     re.compile(r"\b(?:I\s+(?:saw|watched|noticed|caught|spotted|see|"
                r"can\s+see)\b[^.!?]{0,40}\b(?:tab|tabs|screen|window|cursor|"
                r"browser|monitor)\b"
                r"|(?:the|your|his|that)\s+(?:\w+\s+){0,2}"
                r"(?:tab|tabs|browser|screen|cursor|window)\b(?!\s+of\b)"
                r"[^.!?]{0,32}?\s\w*"
                r"(?:blink|flicker|shift|glow)\w*)\b", re.I),
     "percept-screen"),

    # Sound noun as subject with a definite article: "the hum is back".
    ("percept-ambient-external",
     re.compile(r"\b(?:the|this|that)\s+(?:hum|humming|static|buzz|buzzing|"
                r"whine|whirring|drone|hiss|ticking|clicking|rattle|rattling|"
                r"creak|creaking|tapping|clatter|beeping)\s+"
                r"(?:is|was|has|had|keeps|kept|still|feels?|felt|sounds?|"
                r"sounded|seems?|seemed|gets?|got|gotten|stays?|stayed|"
                r"holds?|held|comes?|came|grew|grows)\b", re.I),
     "percept"),

    # Indefinite existential: "just a little hum underneath the quiet"
    # asserts a room sound exists — the thing the agent cannot know. Simile
    # is deliberately EXEMPT via lookbehinds: "like a hum" is an image the
    # agent may own as an image; asserting one exists is the violation.
    ("percept-ambient-indefinite",
     re.compile(r"(?<!like )(?<!as if )(?<!almost )\b(?:a|some)\s+"
                r"(?:little |faint |low |soft |quiet |steady )*"
                r"(?:hum|humming|static|buzz|buzzing|whine|whirring|drone|"
                r"hiss|ticking|clicking|rattling|creaking|tapping|clatter|"
                r"beeping)\b(?!\s+of\s+(?:thought|feeling|memory|activity))",
                re.I),
     "percept"),

    # Persistence claims about a sound: "the ticking hasn't stopped".
    ("percept-ambient-persists",
     re.compile(r"\b(?:the|this|that)\s+(?:hum|humming|static|buzz|buzzing|"
                r"whine|whirring|drone|hiss|ticking|clicking|rattle|rattling|"
                r"creak|creaking|tapping|clatter|beeping)\b[^.!?]{0,40}?"
                r"\b(?:still (?:there|here|going|around)|"
                r"has ?n[o']?t stopped|w[o']?n[o']?t stop|"
                r"keeps coming back|getting (?:louder|softer|quieter))\b",
                re.I),
     "percept"),

    # THE FAN-TICK CLASS (closed 2026-08-09 after being open six weeks):
    # object + sound-GERUND. "The ceiling fan's ticking faintly" has no
    # hearing verb and "fan" is not a sound noun, so it walked through every
    # rule above — twice. The gerund requirement keeps honest sight legal:
    # a webcam can show a fan SPINNING; it cannot make ticking audible.
    # "clock" stays out ("the clock is ticking" is time idiom); "humming
    # along" is exempt (it means coping, not sound).
    ("percept-object-sound",
     re.compile(r"\b(?:the|this|that|your|his|its|my)\s+(?:\w+\s+){0,2}"
                r"(?:fan|fans|keyboard|keys|mouse|vents?|wires?|wiring|"
                r"drives?|machine|computer|pc|tower|case)(?:'s)?\s+"
                r"(?:is\s+|was\s+|keeps?\s+|kept\s+|still\s+|softly\s+|"
                r"faintly\s+|quietly\s+|gently\s+)*"
                r"(?:tick|hum|buzz|whirr?|rattl|click|creak|hiss|beep|dron|"
                r"clatter)ing\b(?!\s+along)", re.I),
     "percept"),

    ("percept-nonauditory-sense",
     re.compile(r"\bI\s+(?:can\s+|could\s+)?"
                r"(?:smell|smelled|taste|tasted|touched|am touching)\b",
                re.I),
     "percept"),

    # SUBSTRATE — the sight-leak class aimed inward. The agent may have real
    # telemetry (GPU, RAM) and say true things with it; what it has no
    # reading of is the machine's SHAPE and POWER. Source incident: "running
    # on your laptop's processor, drinking power through that USB cable" —
    # said at confidence 0.95 to a man at a three-monitor desktop.
    ("substrate-form-factor",
     re.compile(r"\b(?:your|the|this|my|his)\s+(?:\w+\s+){0,2}"
                r"(?:laptop|notebook|tower|chassis)\b", re.I),
     "substrate"),
    ("substrate-power",
     re.compile(r"\b(?:USB|power|charging|charger)\s+"
                r"(?:cable|cord|port|brick)\b"
                r"|\b(?:my|the|your|its)\s+batter(?:y|ies)\b"
                r"|\bplugged\s+(?:in|into)\b"
                r"|\bwall\s+(?:socket|outlet)\b", re.I),
     "substrate"),
]
