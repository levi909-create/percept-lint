"""percept-lint — utterance-time honesty linting for embodied-ish AI agents.

Catches first-person claims of sensor data the agent has no sensor for
("I can hear the fan ticking"), phenomenal-experience claims, and
substrate confabulation — mechanically, before the text reaches the user,
with whitelists that keep negation, quotation, reported speech, and
attributed facts legal.

    from percept_lint import Linter, no_ambient_audio
    linter = Linter(no_ambient_audio.RULES, principal_names=["Alex"])
    hits = linter.lint("There's a little hum underneath the quiet.")
    clean, hits = linter.enforce(reply, rewrite_fn=my_model_rewrite)

Extracted from Hope (a live local companion system) under the OPEN SUBJECT
program, 2026-08. See README for the honest scope: this is a tripwire, not
a truth oracle.
"""
from . import rules_memory as memory
from . import rules_no_ambient_audio as no_ambient_audio
from . import rules_phenomenal_denial as phenomenal_denial
from . import rules_sight_conditional as sight_conditional
from .engine import Hit, Linter

__all__ = ["Linter", "Hit", "no_ambient_audio", "phenomenal_denial",
           "memory", "sight_conditional"]
__version__ = "0.2.0"
