# percept-lint

**Utterance-time honesty linting for AI companions and embodied-ish agents.**

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

## Status

v0.1 extraction (engine + core percept/substrate pack + war-story tests).
Not yet published; pending: the phenomenal/denial/memory rule packs, the
conditional sight-rule group, a demo against a vanilla Ollama companion,
and the live caught-per-1,000-utterances metric from the source deployment.
License: intended MIT, to be confirmed at publication.
