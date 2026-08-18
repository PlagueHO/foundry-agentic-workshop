from .script_test_helpers import load_script

check_model_quota = load_script('check_model_quota_script', 'check-model-quota.py')


def test_is_truthy_and_required_environment_validation() -> None:
    assert check_model_quota._is_truthy('true') is True
    assert check_model_quota._is_truthy('false') is False
    assert check_model_quota._validate_required_env({
        'AZURE_LOCATION': '',
        'AZURE_ENV_NAME': '',
    })
    assert check_model_quota._validate_required_env({
        'AZURE_LOCATION': 'eastus',
        'AZURE_ENV_NAME': 'workshop',
    }) == []


def test_quota_name_and_region_helpers() -> None:
    assert check_model_quota._quota_name('GlobalStandard', 'gpt-4o') == (
        'OpenAI.GlobalStandard.gpt-4o'
    )
    assert check_model_quota._data_zone_for_region('eastus')
    assert check_model_quota._deployment_scope('GlobalStandard', 'eastus')
