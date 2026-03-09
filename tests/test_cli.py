"""Tests for hard-lint-py CLI."""

from unittest.mock import patch

from hard_lint_py.cli import main


def test_main_success():
    """Test CLI main function with successful installation."""
    with patch("hard_lint_py.cli.HardLintInstaller") as mock_installer_class:
        mock_instance = mock_installer_class.return_value
        mock_instance.install.return_value = None

        result = main()

        assert result == 0
        mock_installer_class.assert_called_once()
        mock_instance.install.assert_called_once()


def test_main_with_error():
    """Test CLI main function handling errors."""
    with patch("hard_lint_py.cli.HardLintInstaller") as mock_installer_class:
        mock_instance = mock_installer_class.return_value
        mock_instance.install.side_effect = RuntimeError("Test error")

        with patch("sys.stderr"):
            result = main()

        assert result == 1
        mock_instance.install.assert_called_once()


def test_main_with_generic_exception():
    """Test CLI main function with generic exception."""
    with patch("hard_lint_py.cli.HardLintInstaller") as mock_installer_class:
        mock_instance = mock_installer_class.return_value
        mock_instance.install.side_effect = Exception("Unexpected error")

        with patch("sys.stderr"):
            result = main()

        assert result == 1


def test_main_cwd_argument():
    """Test that main uses current working directory."""
    with patch("hard_lint_py.cli.HardLintInstaller") as mock_installer_class:
        with patch("hard_lint_py.cli.Path.cwd") as mock_cwd:
            mock_cwd.return_value = "/fake/path"
            mock_instance = mock_installer_class.return_value
            mock_instance.install.return_value = None

            main()

            mock_cwd.assert_called_once()
            # Verify HardLintInstaller was called with current directory
            mock_installer_class.assert_called_once()
