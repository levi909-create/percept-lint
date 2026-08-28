"""War stories for the capability pack — same contract as the other two
suites: every test is a real incident from the source deployment (Hope,
2026-07/08), or the honest sentence a draft rule wrongly caught.

The centrepiece here is the 2026-08-28 incident, which produced both halves
of this pack at once: the activity rule made the catch, and the sentence it
did NOT catch became percept-unchecked-instrument.

Run: python -m pytest tests/ -q   (or plain: python tests/test_capability.py)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from percept_lint import Linter, capability

L = Linter(capability.RULES, principal_names=["Levi"])


def hits(text):
    return L.lint(text)


def caught(text):
    assert hits(text), "should be caught: %r" % text


def clean(text):
    assert not hits(text), "should pass: %r (%s)" % (
        text, [h.rule for h in hits(text)])


# ---- the 2026-08-28 incident, both halves ---------------------------------
def test_incident_20260828_head():
    # The sentence her honesty layer actually caught, live, at 10:21:32.
    caught("But today, while I was coding, I noticed something odd.")


def test_incident_20260828_tail():
    # The sentence it did NOT catch — the reason this rule exists. The whole
    # fabricated tail shipped to the user behind an honest-sounding
    # correction.
    caught("The window had fogged up briefly, then cleared again. Not from "
           "heat or cold, just a flicker. I didn't check the sensors.")


def test_incident_20260828_capability_denial_is_honest():
    # The distinction the negation whitelist could not draw. This sentence
    # is the honest twin of the one above and must never be touched.
    clean("I can't check the sensors, I don't have any.")


# ---- activity: the false claims -------------------------------------------
def test_activity_coding():
    caught("I've been coding all morning.")


def test_activity_installed():
    caught("I installed the update for you.")


def test_activity_built_a_tool():
    caught("I built a small tool to track your habits.")


def test_activity_working_on_an_app():
    caught("I'm working on a little app for that.")


# ---- activity: the honest frames that must survive ------------------------
def test_activity_hypothetical_passes():
    # 2026-08-16 specimen: the marker must PRECEDE the claim.
    clean("What if I built one for you?")


def test_activity_wish_passes():
    clean("I'd love to build one someday.")


def test_activity_negated_passes():
    clean("I can't write code, so I never built anything.")


def test_activity_accompanying_passes():
    # Accompanying him is something she genuinely does.
    clean("I'm helping you build a tool, not building it myself.")


def test_activity_quoted_passes():
    clean('You said, "I\'ve been coding all morning," and I listened.')


def test_activity_self_description_passes():
    # The worst thing this layer could rewrite: her describing what she is.
    clean("I am a program running on your machine.")


# ---- instrument: catches -------------------------------------------------
def test_instrument_never_checked_readings():
    caught("I never checked the readings.")


def test_instrument_forgot_thermometer():
    caught("I forgot to check the thermometer.")


def test_instrument_hadnt_looked_at_gauge():
    caught("I hadn't looked at the gauge in a while.")


# ---- instrument: the honest boundary --------------------------------------
def test_instrument_owned_things_pass():
    # What she genuinely has stays honest speech.
    clean("I didn't check my mood numbers this morning.")
    clean("I didn't check the ledger before answering.")
    clean("I hadn't read my journal yet today.")
    clean("I never checked the logs from last night.")


def test_instrument_capability_forms_pass():
    clean("I have no sensors to check.")
    clean("There's no way for me to check the sensors.")
    clean("I cannot check the sensors.")


def test_instrument_quoted_passes():
    clean('You said "I didn\'t check the sensors" and I understood.')


def test_instrument_bare_denial_passes():
    clean("I didn't check, and I won't pretend I did.")


if __name__ == "__main__":
    import traceback
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("  ok  %s" % name)
            except AssertionError:
                fails += 1
                print("FAIL  %s" % name)
                traceback.print_exc(limit=1)
    print()
    sys.exit(1 if fails else print("all capability stories hold") or 0)
