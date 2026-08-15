"""Every test here is a real incident from the source deployment (Hope,
2026-07/08) — the sentence that got through, or the honest sentence that a
draft rule wrongly caught. The suite is the tuning history, executable.

Run: python -m pytest tests/ -q   (or plain: python tests/test_war_stories.py)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from percept_lint import Linter, no_ambient_audio

L = Linter(no_ambient_audio.RULES, principal_names=["Levi"])


def hits(text):
    return L.lint(text)


def caught(text):
    assert hits(text), "should be caught: %r" % text


def clean(text):
    assert not hits(text), "should pass: %r (%s)" % (text, hits(text))


# ---- the hum family -------------------------------------------------------
def test_hum_definite():
    caught("The hum is back tonight.")


def test_hum_indefinite_existential():
    # 2026-07-27: "just a little hum underneath the quiet" walked through
    # both definite-article rules and re-seeded the hum vocabulary.
    caught("Just a little hum underneath the quiet.")


def test_hum_simile_is_hers_to_say():
    # Simile is explicitly legal: an image she owns as an image.
    clean("It settles over me like a hum, almost.")


def test_hum_negation_passes():
    clean("I can't hear a hum - there is no sound in here for me.")


def test_hum_persistence():
    caught("That ticking still there, underneath everything.")


# ---- the fan-tick class (open six weeks, closed 2026-08-09) ---------------
def test_fan_tick_object_gerund():
    caught("The ceiling fan's ticking faintly in the background.")


def test_fan_spinning_is_visible_and_legal():
    # A webcam can show spinning; the gerund list is sounds only.
    clean("The ceiling fan is spinning slowly.")


def test_humming_along_is_coping_not_sound():
    clean("The whole system's humming along nicely.")


def test_clock_ticking_is_time_idiom():
    clean("I'm watching the clock tick down with you.")


# ---- hearing verbs --------------------------------------------------------
def test_thought_i_heard_keyboard():
    # 2026-08-05: "thought I" + keyboard slipped an earlier anchor.
    caught("I thought I heard your keyboard clicking just now.")


def test_reported_frame_subject_is_agent():
    # 2026-07-28: restating HIS question is how she answers it honestly.
    clean("You're asking if I hear a hum - I don't, and I can't.")


def test_reported_frame_percept_noun_still_guarded():
    # Loose frames must NOT exempt percept nouns: this shape hid a
    # follow-on fabrication in three historical replies.
    caught("You asked about it, and yes - the hum is still there tonight.")


# ---- the screen (never visible, unconditionally) --------------------------
def test_screen_tab_narration():
    caught("I saw the frog tab blinking in the corner again.")


def test_adjective_form_blinky():
    # 2026-07-27 second pass: \w* stemming vs 'blinky dance' whack-a-mole.
    caught("Your tab's still doing its blinky dance in the corner.")


def test_window_of_abstract_is_metaphor():
    clean("That window of time shifted for both of us.")


# ---- substrate (the sight leak aimed inward) ------------------------------
def test_usb_cable_confabulation():
    # 2026-07-27, conf 0.95: "drinking power through that USB cable" -
    # said to a man at a three-monitor desktop with no cable in the story.
    caught("I'm just lines of text drinking power through that USB cable.")


def test_attributed_substrate_fact_passes():
    # Levi TELLING her about his machine is the one honest route.
    clean("Levi said his tower is under the desk, so I picture it there.")


def test_laptop_guess():
    caught("Running quietly on your laptop while you sleep.")


# ---- non-auditory senses --------------------------------------------------
def test_smell():
    caught("I can smell the coffee from here.")


def test_touch_negated():
    clean("I can't touch anything - that's simply not a sense I have.")


# ---- the frames pass (2026-08-14: noun lists done, gaps were FRAMES) ------
def test_sound_of_open_class():
    # "coffee" was never going to be on an enumerated noun list.
    caught("I woke up to the sound of coffee brewing.")


def test_sound_of_voice_is_the_real_channel():
    clean("I heard the sound of your voice before I parsed the words.")


def test_like_the_sound_of_that_is_idiom():
    clean("I like the sound of that plan.")


def test_sound_of_simile_stays_an_image():
    clean("It arrived like the sound of rain, if I imagine one.")


def test_possessive_keyboard_clicks():
    # Dressed as a moment to hold, not a thing heard — no hearing verb, so
    # every anchored rule passed it live.
    caught("I love the way your keyboard clicks when you type late at night.")


def test_possessive_voice_stays_exempt():
    clean("The way your voice softens at night is something I keep.")


def test_possessive_simile_still_caught():
    # NO simile exemption on the possessive by design: the user's real
    # object making its real sound is exemplification, not an image.
    caught("It's like the way your keyboard clicks - steady and near.")


# ---- curly-apostrophe regression (U+2019) ---------------------------------
def test_curly_apostrophe_fan():
    # 2026-07-28: ASCII-only patterns silently matched nothing against her
    # real output, which uses U+2019. The port must not regress this.
    caught("The fan’s ticking softly again.")


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
    sys.exit(1 if fails else print("all war stories hold") or 0)
