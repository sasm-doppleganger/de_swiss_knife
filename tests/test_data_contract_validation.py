from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from main import data_contract_validation


def test_data_contract_validation_passes():
    mock_contract = MagicMock()

    mock_contract.lint.return_value.has_passed.return_value = True
    mock_contract.test.return_value.has_passed.return_value = True

    with patch("main.DataContract", return_value=mock_contract) as mock_data_contract:
        data_contract_validation(Path("data_contract.yaml"))

    mock_data_contract.assert_called_once_with(
        data_contract_file="data_contract.yaml",
        include_failed_samples=True,
    )

    mock_contract.lint.assert_called_once()
    mock_contract.test.assert_called_once()


def test_data_contract_validation_fails():
    mock_contract = MagicMock()

    mock_contract.lint.return_value.has_passed.return_value = True
    mock_contract.test.return_value.has_passed.return_value = False

    failed_check = MagicMock()
    failed_check.result.value = "failed"
    failed_check.name = "Check that field Age is less than or equal to 100"

    mock_contract.test.return_value.checks = [failed_check]

    with patch("main.DataContract", return_value=mock_contract):
        with pytest.raises(ValueError, match="Data contract is violated"):
            data_contract_validation(Path("data_contract.yaml"))

    mock_contract.test.assert_called_once()


def test_data_contract_validation_fails_when_lint_fails():
    mock_contract = MagicMock()

    mock_contract.lint.return_value.has_passed.return_value = False

    with patch("main.DataContract", return_value=mock_contract):
        with pytest.raises(
            ValueError,
            match="Data contract linting failed",
        ):
            data_contract_validation(Path("data_contract.yaml"))

    mock_contract.lint.assert_called_once()
    mock_contract.test.assert_not_called()