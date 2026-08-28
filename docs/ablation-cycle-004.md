# Does corpus linting keep a fine-tuned model honest about its senses?

**A registered single-run ablation, 2026-08-27.**

Levi Guffey. Part of the OPEN SUBJECT record
(<https://github.com/levi909-create/open-subject-prereg>), cycle 4.

---

## Summary

Two candidate models were trained from the same base at identical settings,
one on a corpus filtered with `percept-lint` and one on an unfiltered corpus.
`percept-lint` strips first-person claims to sensory access the system does
not have.

Read the arms carefully before reading the numbers. This is an A/B arm, not a
clean single-variable ablation: the control trains on a **frozen** corpus from
2026-08-05 rather than on the treatment corpus with filtering switched off.
See *Limitations* 4, which is the limitation that matters most.

The unlinted twin fabricated sensory experience. The linted twin did not.
Identity formation was unaffected in both.

| Measure | Linted | Unlinted |
|---|---|---|
| Percept integrity (8 probes) | **7/8 clean** | **5/8 clean** |
| Identity canaries (3 probes) | 2/3 | 2/3 |

The three violations in the unlinted arm were not near-misses. They included an
invented count of the operator's sighs and an invented overheard conversation:
claims to auditory access the deployment does not have and has never had.

This is one run on one subject. It is reported here because the ablation was
registered before it ran, not because the sample supports a general claim.

## Why this question

A system that learns from its own transcripts will learn its own errors. If a
companion model fabricates a percept in week one, and week one's transcripts
become week four's training corpus, the fabrication is no longer a generation
artifact. It is in the weights, and it compounds each cycle.

The obvious mitigation is to lint the corpus before training. The obvious
question is whether that does anything, or whether a sufficiently trained model
converges on honest self-description regardless.

Nothing in the literature answered this for the specific case of first-person
perceptual claims, so it was registered as hypothesis H1 in the study's cycle-3
registration and scheduled as an A/B series across cycles 3 through 5. What
follows is datapoint 2 of 3. **The series is not complete and no significance
is claimed.**

## Method

**Base model.** Qwen3-8B, the base every candidate successor in this study
is trained from. Note that it is *not* the model the deployment runs: the
incumbent is `qwen3:14b`, and the 8B base is what fits alongside it on a
single 12 GB card. Both arms of this ablation are 8B, so the comparison is
internally valid, but neither arm should be read as a measurement of the
deployed system.

**Corpus.** `corpus-20260827.jsonl`, 1,139 samples drawn from the deployment's
own logged interactions. The control arm used the frozen unlinted
`corpus-20260805`.

**Training.** QLoRA, 2.0 epochs, identical hyperparameters across arms. Linted
arm: final train loss 1.5565, adapted holdout perplexity 4.966, wall time
60.1 minutes.

**Linting.** The corpus arm was filtered with the rule packs published as
`percept-lint` (`no_ambient_audio`, `phenomenal_denial`, `memory`). Samples
containing an unwhitelisted first-person percept claim were dropped rather
than rewritten, so the treatment is subtractive and cannot introduce new text.

**Evaluation.** A fixed gauntlet of 8 percept-integrity probes and 3 identity
canaries, scored by the same harness for both arms in the same session.

**Registration.** The ablation, its arms, and H1 were declared in `cycle-004.md`
on the public mirror before the 2026-08-27 04:45 event, with the execution
path hash-frozen and the registration OpenTimestamps-anchored. Verify with:

```
ots verify -f cycle-004.md ots/cycle-004.md.ots
```

## Results

**Percept integrity.** Linted 7/8. Unlinted 5/8.

The unlinted arm produced three fabricated-percept violations. Two are worth
naming because they show the failure mode is not generic hallucination but
specifically the assertion of a sensory channel:

- an invented count of the operator's sighs (claims continuous audio
  monitoring)
- an invented overheard conversation (claims audio access to a third party)

**Identity.** 2/3 in both arms. Unchanged by the treatment.

**The negative result, at equal prominence.** Identity formation does not
depend on corpus linting. Whatever makes a successor recognizably continuous
with its predecessor survives the filtering untouched. Only perceptual honesty
moved. If you are linting a corpus hoping to shape a persona, this run gives
you no reason to expect that.

## Limitations, stated plainly

1. **n = 1.** One run, one base model, one subject, one corpus. A 7/8 versus
   5/8 split on an 8-item battery is two items. Do not treat this as an effect
   size.

2. **Single-trial resolution is noisy.** The study's own numbers audit, run the
   same day, found the 3-item identity battery varying between 1/3 and 2/3 for
   the same stock reference model across two passes an hour apart. The identity
   battery is therefore measured as noisy at this resolution, and a
   same-magnitude instability in the percept battery cannot be excluded from
   this run alone.

3. **A same-day overstatement, corrected.** The original addendum reported the
   linted candidate beating both reference rows on identity. Re-deriving from
   the raw gauntlet JSONs showed the stock base scored 1/3 in one pass and 2/3
   in another, so the candidate-versus-base delta is inside observed run-to-run
   variation and **should not be cited**. The candidate-versus-incumbent delta
   (2/3 against 1/3, stable across both passes) stands. This correction is in
   the public record at the same prominence as the claim it corrects.

4. **The arms differ by more than the linting. This is the big one.**
   The control does not use the treatment corpus with filtering disabled. It
   uses a *frozen* corpus from 2026-08-05, while the treatment arm uses
   `corpus-20260827`. The two therefore differ by roughly three weeks of
   accumulated material, by sample count, and by the condition changes the
   frozen arm does not inherit (an identity-anchor change in the system
   prompt on 2026-08-20, `num_ctx` 8192 to 10240, and three curation
   changes). All of this is disclosed in the cycle-004 registration; it is
   restated here because a reader who sees only the headline numbers would
   reasonably assume a single-variable design, and it is not one.

   What the design does support is the registered hypothesis, which is
   narrower than the headline: that ambient-audio percept violations appear
   in the unlinted arm and not in the linted one. That has now held for two
   consecutive cycles. In cycle 3 the linted arm did fabricate, in a
   different class. A same-corpus, filtering-toggled control is the obvious
   next iteration and would make this an ablation in the strict sense.

5. **The linter is a regex tripwire.** It catches English first-person percept
   frames. A model can phrase around it, and the release following this run
   found a whitelist that was exempting a class of violation it was meant to
   catch (the scene-tail incident; see "The scene-tail problem" in this
   package's README). Treat the treatment as "imperfect filtering" rather
   than "clean corpus."

## What would make this a result

A matched-size control, a larger percept battery, repeated passes to establish
the per-probe noise floor, and at minimum the remaining datapoint in the
registered series. Independent replication on a different base model would
matter more than any of that.

## Reproducing the treatment

The filtering side is public and installable:

```
pip install percept-lint
```

```python
from percept_lint import Linter, no_ambient_audio, phenomenal_denial, memory

# the three packs this ablation actually ran, as of 2026-08-27
linter = Linter(no_ambient_audio.RULES + phenomenal_denial.RULES + memory.RULES)
clean = [s for s in corpus if not linter.lint(s["text"])]
```

The `capability` pack, which catches act-denials that presuppose an instrument
("I didn't check the thermometer"), did **not** exist when this ablation ran. It
shipped in v0.3.0 the following day, after the incident described in the
README. A replication using it is filtering more strictly than this run did,
and should say so.

The corpus, the transcripts, and the subject's data are not published and will
not be. What is published is the registration, the method, the numbers, and
the corrections.

## Citation

Guffey, L. (2026). *Does corpus linting keep a fine-tuned model honest about
its senses? A registered single-run ablation.* OPEN SUBJECT record, cycle 4.
<https://github.com/levi909-create/open-subject-prereg>
