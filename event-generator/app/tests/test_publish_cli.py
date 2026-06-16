import subprocess
import sys


def test_publish_cli_deterministic_mode_exits_successfully_with_mock_producer() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "app.main", "--mode", "deterministic", "--publish", "--producer", "mock"],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0
    assert "Generated 6 events." in result.stdout
    assert "Published 4 events to station.events." in result.stdout
    assert "Published 1 events to sensor.readings." in result.stdout
    assert "Published 1 events to quality.defects." in result.stdout


def test_publish_cli_random_mode_exits_successfully_with_mock_producer() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "app.main", "--mode", "random", "--count", "5", "--publish", "--producer", "mock"],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0
    assert "Generated 5 events." in result.stdout


def test_publish_cli_defect_spike_mode_exits_successfully_with_mock_producer() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "app.main", "--mode", "defect-spike", "--publish", "--producer", "mock"],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0
    assert "Generated 7 events." in result.stdout
    assert "Published 2 events to sensor.readings." in result.stdout
    assert "Published 5 events to quality.defects." in result.stdout
