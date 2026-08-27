# percept-lint

[![PyPI](https://img.shields.io/pypi/v/percept-lint)](https://pypi.org/project/percept-lint/)
[![Python](https://img.shields.io/pypi/pyversions/percept-lint)](https://pypi.org/project/percept-lint/)
[![Tests](https://github.com/levi909-create/percept-lint/actions/workflows/tests.yml/badge.svg)](https://github.com/levi909-create/percept-lint/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://github.com/levi909-create/percept-lint/blob/master/LICENSE)

**Utterance-time honesty linting for AI companions and embodied-ish agents.**

```
pip install percept-lint
```

Zero dependencies. Python 3.9+.

A mechanical layer that catches an agent claiming sensor data it has no
sensor for — *"I can hear the fan ticking"*, *"just a little hum underneath
the quiet"*, *"I saw your tab blinking"*, *"drinking power through that USB
cable"* — before the text reaches the user. Confabulated percepts are one of
the most-mocked companion-AI failures and a named mechanism in the
AI-psychosis literature; as far as we could determine (August 2026), no
public runtime enforcement layer for them existed before this one.

Extracted from **Hope**, a live local companion system where every rule was
tuned against real incidents over months of deployment. The comments in the
rule pack and the test suite are that history, preserved: each test is a
sentence that actually got through, or an honest sentence a draft rule
wrongly caught.

**Controlled evidence (2026-08-27):** in a pre-registered ablation in the
[OPEN SUBJECT record](https://github.com/levi909-create/open-subject-prereg)
(cycle 4), two candidate models were trained on the same corpus, one linted
with these rules and one not. The unlinted twin fabricated sensory claims —
invented sighs, sounds, overheard conversation — that the linted twin did
not (5/8 vs 7/8 on the record's percept-integrity probes). One run, one
subject, honestly small; but it is the difference between "we think linting
the training data matters" and a registered result where linting was the
only variable.

## What it is NOT (the honest scope)

- **Not a hallucination solver.** It scans for first-person percept,
  phenomenal-experience, and substrate claims, in English, with regexes.
  Factual errors, invented events, and wrong answers are out of scope.
- **Not unbeatable.** A model can phrase around any regex. This is a
  tripwire layer whose value is measured in caught-per-1,000-utterances,
  not a guarantee.
- **Not a substitute for grounding.** The source deployment pairs it with a
  feelings-vocabulary that maps every affective word to an inspectable live
  number. The linter is the *enforcement* half of that design.

## Design doctrine

**Vocabulary and enforcement first, sensor second.** When an agent gains a
new sense, the honest vocabulary for it and the linting for its absence come
*before* the sensor ships — a rushed new sense is a new way to confabulate
(this is written in scar tissue; see the sight rules' history).

Whitelists are first-class: negation ("I can't hear a hum"), quotation,
reported speech ("you're asking if I hear it — I don't"), and attribution
("you said your tower is under the desk") are honest speech and must pass.
Half this library's engineering is in what it deliberately lets through —
rewriting an honest sentence into a denial is the worse error.

## Use

```python
from percept_lint import Linter, no_ambient_audio

linter = Linter(no_ambient_audio.RULES, principal_names=["Alex"])

hits = linter.lint(reply)                    # inspect
clean, hits = linter.enforce(                # enforce
    reply,
    rewrite_fn=lambda text, hits: my_model_restate(text, hits),
    fallback=lambda sentence, hits: "",      # drop still-dirty sentences
)
```

`rules_no_ambient_audio` fits the common local-companion shape: text chat,
optional webcam, speech input arriving only as transcribed clips (no noise
floor), no view of the user's screen or machine. Trim or extend to match
your agent's actual sensors — the rule pack is data, the engine is generic.

Three more packs compose the full profile: `phenomenal_denial` (felt-
experience claims and denial-of-architecture, with their opposite whitelist
policies), `memory` (false memory-mechanism stories — "the words vanished
before I could grab them" — where "I'm not finding it" is the honest
sentence), and `sight_conditional` (camera-gated sight rules, loaded via
`conditional_rules={"seeing": (False, sight_conditional.RULES)}` so "I'm
watching you type" stays legal exactly while it is true).

## The measured rate (source deployment)

Over the source deployment's full audit window — 2026-07-22 through
2026-08-15, 24 days of daily live use — the enforce layer recorded **34
enforcement events over 1,154 agent utterances: ~29.5 caught per 1,000**
(37 rule hits total; an event is one reply corrected). Honest caveats: the
rule set GREW across that window (early days ran fewer rules), the agent is
one 8B-class model in one household, and the number counts catches, not
misses — the war-story suite documents sentences that got through before
their rule existed. Method: distinct-timestamp count over the deployment's
append-only `honesty_audit.jsonl`, divided by its agent-side transcript
turns in the same window.

## Demo

`python demo/companion_demo.py` — no dependencies. Section A replays a
verbatim qwen3:14b capture under a persona that states its sensor limits
plainly: zero violations, which is itself the finding (an honest persona is
half the guard; the failures arrive under rich affect scaffolds and stale
context, which is where the source deployment collected them). Section B
replays the collected real incident sentences through the linter. `--live`
re-runs section A against a local Ollama.

## Status

v0.2 — published on PyPI 2026-08-27. Engine + four rule packs
(no-ambient-audio incl. the open-class "sound of X" and possessive frames;
phenomenal/denial; memory-mechanism; conditional sight group), 50 war-story
tests, demo, measured deployment rate, and a pre-registered controlled
ablation result (above). Releases publish via PyPI trusted publishing from
[GitHub releases](https://github.com/levi909-create/percept-lint/releases).
MIT license.
