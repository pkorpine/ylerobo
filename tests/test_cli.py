from click.testing import CliRunner
from ylerobo.cli import cli


def test_flow():
    runner = CliRunner()
    # Re-create database
    result = runner.invoke(cli, ["init", "--force"])
    assert result.exit_code == 0
    result = runner.invoke(cli, ["init"])
    assert result.exit_code == 1

    # Add series
    result = runner.invoke(cli, ["add", "https://areena.yle.fi/1-50754744"])
    assert result.exit_code == 0
    result = runner.invoke(cli, ["add", "https://areena.yle.fi/1-50754744"])
    assert result.exit_code == 1

    # List series
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0

    # Remove series
    runner = CliRunner()
    result = runner.invoke(cli, ["remove", "https://areena.yle.fi/1-50754744"])
    assert result.exit_code == 0
    result = runner.invoke(cli, ["remove", "https://areena.yle.fi/1-50754744"])
    assert result.exit_code == 1
