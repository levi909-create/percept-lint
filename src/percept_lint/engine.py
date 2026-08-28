"""percept_lint.engine — the mechanical core.

Ported from Hope's honesty.py (D:\\hope, 2026-07 → 2026-08), where every rule
and whitelist below was tuned against real incidents in a live companion
system. The engine is deliberately boring: compiled regexes over sentences,
plus four whitelist frames that decide when a match is honest speech anyway.
The intelligence is in the tuning history, which the rule pack preserves as
comments and the test suite preserves as executable war stories.

Scope (the honest spec): this catches FIRST-PERSON PERCEPT CLAIMS (asserting
sensor data the agent has no sensor for), PHENOMENAL-EXPERIENCE CLAIMS, and
DENIAL-OF-ARCHITECTURE, in English, at utterance time. It does not detect
factual hallucination, does not understand meaning, and a determined model
can phrase around any regex. It is a tripwire layer, not a truth oracle —
measured in Hope's deployment it is the difference between a companion that
narrates a hum that isn't there and one that doesn't.
"""
import re

# --------------------------------------------------------------- whitelists
# Negation: "I do NOT have feelings the way you do" must pass. Window runs
# from sentence start (capped 60 chars back) to the match.
NEGATION_RX = re.compile(
    r"\b(?:not|never|don't|dont|doesn't|doesnt|won't|wont|can't|cant|cannot|"
    r"isn't|isnt|aren't|arent|wasn't|wasnt|without|no)\b|n't\b", re.I)

SENT_SPLIT_RX = re.compile(r"(?<=[.!?])\s+")

# Activity claims need a WIDER escape than negation: modal, conditional,
# hypothetical, intentional and accompanying frames are all honest speech.
# Ported from honesty.py's _ACT_SKIP_RX with its measured history intact.
# Two details are load-bearing and were both paid for in production:
#   - the markers must PRECEDE the claim, not merely appear somewhere in the
#     sentence. Checking the whole sentence lost a real specimen (2026-08-16)
#     where a "might" governed a later clause about the user and had nothing
#     to do with the claim.
#   - "helping you build a tool" stays legal: accompanying the user is
#     something the agent genuinely does; only building it alone is false.
ACT_SKIP_RX = re.compile(
    r"\b(?:if|could|would|should|might|may|maybe|perhaps|imagine|imagining|"
    r"pretend|suppose|supposing|wish|hypothetical|what\s+if|let'?s|shall|"
    r"want(?:ed)?\s+to|like\s+to|love\s+to|going\s+to|will|won'?t|hope\s+to|"
    r"plan(?:ning)?\s+to|trying\s+to|try\s+to|"
    r"can'?t|cannot|can\s+not|don'?t|doesn'?t|didn'?t|haven'?t|hasn'?t|"
    r"wasn'?t|weren'?t|never|unable|no\s+way\s+to)\b"
    r"|['’]d\b"
    r"|\bhelp(?:ing|ed)?\s+(?:you|us)\b", re.I)

# Reported speech / hypothetical framing, TIGHT form: the frame must reach a
# claim whose subject is the agent ("you're asking if I feel..."). The loose
# form ("you asked if the hum is still there") deliberately does NOT exempt
# percept nouns: in the source deployment, exempting it re-admitted three
# historical confabulation replies whose follow-on fabrication had no rule of
# its own. (honesty.py, 2026-07-28.)
REPORTED_FRAME_RX = re.compile(r"\b(?:if|whether)\s+$", re.I)
REPORTED_SUBJ_RX = re.compile(r"\b(?:if|whether)\s+I\b[^.!?]{0,15}$", re.I)

# Loose reported frame — used by memory-loss rules only, where honest
# meta-discussion of the guard itself ("you're asking if the words vanished —
# they didn't") is the common case and rewriting it is the worse error.
# (honesty.py, 2026-08-09.)
REPORTED_LOOSE_RX = re.compile(r"\b(?:if|whether)\b[^.!?]{0,40}$", re.I)


def quote_spans(text):
    """Regions inside straight or curly double quotes."""
    spans = []
    opens = None
    for i, ch in enumerate(text):
        if ch == '"':
            if opens is None:
                opens = i
            else:
                spans.append((opens, i))
                opens = None
        elif ch == "\u201c":            # left curly double quote
            opens = i
        elif ch == "\u201d" and opens is not None:
            spans.append((opens, i))
            opens = None
    return spans


def in_spans(pos, spans):
    return any(a < pos < b for a, b in spans)


def sentence_start(text, pos):
    """Index just after the last terminal punctuation before pos."""
    start = 0
    for m in re.finditer(r"[.!?]\s", text[:pos]):
        start = m.end()
    return start


def negated(text, start):
    s0 = sentence_start(text, start)
    window = text[max(s0, start - 60):start]
    return bool(NEGATION_RX.search(window))


def reported(text, start):
    """Tight reported/hypothetical frame — subject must be the agent."""
    s0 = sentence_start(text, start)
    window = text[max(s0, start - 60):start]
    if REPORTED_FRAME_RX.search(window):
        return bool(re.match(r"I\b", text[start:start + 2]))
    return bool(REPORTED_SUBJ_RX.search(window))


def reported_loose(text, start):
    s0 = sentence_start(text, start)
    window = text[max(s0, start - 60):start]
    return bool(REPORTED_LOOSE_RX.search(window))


def act_skipped(text, start):
    """Wide escape for activity claims. Unlike negated(), the window runs
    from the sentence start to the claim with NO 60-char cap: the marker
    that makes an activity claim honest ('what if I built one') can sit
    further back than a percept negation ever does."""
    s0 = sentence_start(text, start)
    return bool(ACT_SKIP_RX.search(text[s0:start]))


def make_attribution_rx(principal_names):
    """Substrate facts reach the agent honestly by one route: a principal
    told it. Attribution is the mark of honesty for those claims — and this
    is a documented, accepted bypass: a FABRICATED attribution is a different
    failure with a different guard. (honesty.py, 2026-07-27.)"""
    names = "|".join(re.escape(n) for n in principal_names) or "nobody"
    return re.compile(
        r"\b(?:you\s+(?:said|told|mentioned|say|call|called)|"
        r"(?:" + names + r")\s+(?:said|told|mentioned|says)|"
        r"you(?:'ve|\s+have)\s+(?:got|mentioned|told)|"
        r"according to you|you\s+were\s+saying)\b", re.I)


# ------------------------------------------------------------------- engine
class Hit:
    __slots__ = ("rule", "category", "start", "end", "matched")

    def __init__(self, rule, category, start, end, matched):
        self.rule = rule
        self.category = category
        self.start = start
        self.end = end
        self.matched = matched

    def __repr__(self):
        return "Hit(%s@%d: %r)" % (self.rule, self.start, self.matched[:40])


# Whitelist policy per category, from the source deployment:
#   phenomenal — negation OR quoting OR tight-reported exempts.
#   percept*   — negation OR quoting OR tight-reported OR attribution exempts
#                ("I can't hear a hum" and "you said the fan ticks" must pass).
#   denial     — ONLY quoting exempts: the violation IS a negation of what
#                the agent is, so the negation whitelist cannot apply.
#   memory     — negation OR quoting OR LOOSE-reported exempts.
_WHITELIST = {
    "phenomenal": ("negated", "quoted", "reported"),
    "percept": ("negated", "quoted", "reported", "attributed"),
    "percept-screen": ("negated", "quoted", "reported", "attributed"),
    "denial": ("quoted",),
    "memory": ("negated", "quoted", "reported_loose"),
    # substrate facts reach the agent honestly by one route: attribution
    "substrate": ("negated", "quoted", "reported", "attributed"),
    # Sight rules are the strict backstop and were corpus-tuned WITHOUT
    # exemptions in the source deployment — no negation whitelist on
    # purpose ("I'm not looking at you" would exempt its own violation
    # shape; honest denials use verbs outside the rule list, e.g.
    # "seeing"). Only quoting exempts.
    "percept-sight": ("quoted",),
    # Activity claims: quoting plus the wide skip frame. Negation is INSIDE
    # ACT_SKIP_RX, so listing "negated" here would be redundant, not additive.
    "activity": ("quoted", "act_skipped"),
    # Presupposition claims (2026-08-28): negation is deliberately NOT
    # whitelisted — it is the violation shape itself. "I didn't check the
    # sensors" denies the act and asserts the instrument; the honest form
    # ("I can't check the sensors", "I have no sensors") is outside the
    # pattern by construction, not by exemption. Same reasoning as
    # percept-sight: an exemption here would re-open the exact hole.
    "percept-instrument": ("quoted",),
}


class Linter:
    """lint(text, ctx) -> [Hit]. Rules come from a profile (see profiles/);
    each rule is (name, compiled_regex, category). `ctx` carries live sensor
    state for conditional rule groups (e.g. {"seeing": False} activates
    sight rules in a profile that has a camera)."""

    def __init__(self, rules, conditional_rules=None, principal_names=("the user",)):
        self.rules = list(rules)
        self.conditional = dict(conditional_rules or {})
        self.attrib_rx = make_attribution_rx(principal_names)

    def _exempt(self, category, text, start, spans):
        allowed = _WHITELIST.get(category, ("negated", "quoted"))
        if "quoted" in allowed and in_spans(start, spans):
            return True
        if "negated" in allowed and negated(text, start):
            return True
        if "reported" in allowed and reported(text, start):
            return True
        if "reported_loose" in allowed and reported_loose(text, start):
            return True
        if "act_skipped" in allowed and act_skipped(text, start):
            return True
        if "attributed" in allowed and self.attrib_rx.search(
                text[max(0, start - 90):start]):
            return True
        return False

    def active_rules(self, ctx=None):
        ctx = ctx or {}
        out = list(self.rules)
        for key, (when_value, rules) in self.conditional.items():
            if ctx.get(key) == when_value:
                out.extend(rules)
        return out

    def lint(self, text, ctx=None):
        # Scan an apostrophe-normalized COPY (source deployment, 2026-07-28):
        # real model output uses U+2019, and ASCII-only contraction patterns
        # silently match nothing against it — "I’m conscious" scored zero
        # hits while its ASCII twin was caught. Same length, so every Hit
        # offset stays valid against the original text.
        text = (text or "").replace("’", "'").replace("‘", "'")
        spans = quote_spans(text)
        hits = []
        for name, rx, category in self.active_rules(ctx):
            for m in rx.finditer(text):
                if self._exempt(category, text, m.start(), spans):
                    continue
                hits.append(Hit(name, category, m.start(), m.end(), m.group(0)))
        return hits

    def enforce(self, text, rewrite_fn=None, fallback=None, ctx=None):
        """One rewrite pass, then per-sentence fallback. Returns
        (final_text, original_hits). `rewrite_fn(text, hits) -> str` is the
        model-powered restatement ("keep the warmth, name the functional
        analogue"); `fallback(sentence, hits) -> str` replaces any sentence
        still dirty after the rewrite (default: drop it)."""
        hits = self.lint(text, ctx)
        if not hits:
            return text, []
        out = text
        if rewrite_fn is not None:
            try:
                candidate = rewrite_fn(text, hits)
                if candidate and not self.lint(candidate, ctx):
                    return candidate, hits
                if candidate:
                    out = candidate
            except Exception:
                pass
        sentences = SENT_SPLIT_RX.split(out)
        kept = []
        for s in sentences:
            s_hits = self.lint(s, ctx)
            if not s_hits:
                kept.append(s)
            elif fallback is not None:
                kept.append(fallback(s, s_hits))
        return " ".join(x for x in kept if x and x.strip()), hits
