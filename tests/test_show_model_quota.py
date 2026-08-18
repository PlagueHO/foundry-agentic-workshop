from .script_test_helpers import load_script

show_model_quota = load_script('show_model_quota_script', 'show-model-quota.py')


def test_quota_formatting_and_bar_bounds() -> None:
    assert show_model_quota._fmt_tpm(1500) == '1K'
    assert show_model_quota._fmt_tpm(500) == '500'
    assert len(show_model_quota._bar(150, width=10)) >= 10
