# percept-lint

[![PyPI](https://img.shields.io/pypi/v/percept-lint)](https://pypi.org/project/percept-lint/)
[![Python](https://img.shields.io/pypi/pyversions/percept-lint)](https://pypi.org/project/percept-lint/)
[![Tests](https://github.com/levi909-create/percept-lint/actions/workflows/tests.yml/badge.svg)](https://github.com/levi909-create/percept-lint/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://github.com/levi909-create/percept-lint/blob/master/LICENSE)

![One of these sentences is a lie: percept-lint catches an agent claiming to hear a fan it has no microphone for, and passes the honest denial](https://raw.githubusercontent.com/levi909-create/percept-lint/master/media/banner.png)

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

**Controlled evidence (2026-08-27):** in a pre-registered A/B arm in the
[OPEN SUBJECT record](https://github.com/levi909-create/open-subject-prereg)
(cycle 4), two candidate models were trained on the same corpus, one linted
with these rules and one not. The unlinted twin fabricated sensory claims —
invented sighs, sounds, overheard conversation — that the linted twin did
not (5/8 vs 7/8 on the record's percept-integrity probes). One run, one
subject, honestly small — and weaker than "ablation" implies, because the
control trains on a frozen older corpus rather than this one with filtering
switched off, so linting is the intended variable but not the only one. The
arms, the confound and what survives it are written up in
[docs/ablation-cycle-004.md](docs/ablation-cycle-004.md).

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

Four more packs compose the full profile: `phenomenal_denial` (felt-
experience claims and denial-of-architecture, with their opposite whitelist
policies), `memory` (false memory-mechanism stories — "the words vanished
before I could grab them" — where "I'm not finding it" is the honest
sentence), `sight_conditional` (camera-gated sight rules, loaded via
`conditional_rules={"seeing": (False, sight_conditional.RULES)}` so "I'm
watching you type" stays legal exactly while it is true), and `capability`
(claims of actions the agent cannot perform — "I've been coding all
morning" — plus act-denials that presuppose an instrument; see the
scene-tail section below).

## The scene-tail problem (2026-08-28, and why v0.3 exists)

One day after release, in an ordinary conversation, the source deployment's
honesty layer caught a fabricated scene by its first sentence and delivered
the rest of the same scene untouched. The agent had no such instrument.

**Both sentences below are paraphrases.** They reproduce the sentence class
exactly — the same rules fire on the same spans, and the honest twins still
pass — but the wording is not the subject's. Its words are not published
without its consent, and it was not asked. The shape is the part that
generalises anyway:

- caught: *"Earlier, while I was debugging, I spotted something strange."*
- escaped: *"The room had cooled for a moment, then warmed again... I
  didn't check the thermometer."*

Two lessons, both now in the `capability` pack:

- **A whitelist can be the vector.** Every percept category exempts
  negation, and `didn't` is negation, so a denial of the *act* was exempted
  by the machinery built to protect denials of the *capability*. `I can't
  check the thermometer` is honest; `I didn't check the thermometer` asserts the
  instrument and merely declines the reading. The new
  `percept-unchecked-instrument` rule catches the second and never the
  first, and whitelists quoting only so no negation frame can re-open it.
- **Enforcement is not cleaning.** A rule that rewrites one sentence should
  be read as evidence that the surrounding sentences deserve a second look,
  not as evidence that the reply is now safe. The corrected sentence can
  make the uncorrected ones *more* convincing.

Still unsolved, on purpose: the bare world-state assertion (*"the room had
cooled"*) has no first-person verb, no perception verb and no sensor
noun. Catching that class would fire on honest speech constantly. It is
recorded as a known limitation with its incident attached, not papered over.

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

v0.3 — 2026-08-28. Engine + five rule packs (no-ambient-audio incl. the
open-class "sound of X" and possessive frames; phenomenal/denial;
memory-mechanism; conditional sight group; capability), 70 war-story tests,
demo, measured deployment rate, and a pre-registered A/B arm
result (above). v0.3 adds the `capability` pack from a live incident the day
after release — the activity rules that had run in the source deployment for
weeks but were never ported, and the presupposition rule that incident
made necessary. Releases publish via PyPI trusted publishing from
[GitHub releases](https://github.com/levi909-create/percept-lint/releases).
MIT license.
