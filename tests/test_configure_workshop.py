from .script_test_helpers import load_script

configure_workshop = load_script('configure_workshop_script', 'configure-workshop.py')


def test_display_width_handles_combining_characters() -> None:
    assert configure_workshop._display_width('abc') == 3
    assert configure_workshop._display_width('e\u0301') == 1


def test_callout_helpers_create_bordered_lines() -> None:
    line = configure_workshop._callout_line('Hello', left='[', right=']')
    assert line.startswith('[ Hello')
    assert line.endswith(']')
    assert configure_workshop._callout_border('[', ']').startswith('[')
