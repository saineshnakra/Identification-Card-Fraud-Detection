import subprocess
import sys

import pytest

from id_tamper_check import __version__
from id_tamper_check.cli import main


@pytest.fixture
def pair(write_image, blank, edited):
    return write_image("reference.png", blank), write_image("candidate.png", edited)


def test_cli_writes_outputs_and_summary(tmp_path, pair, capsys):
    out = tmp_path / "out"
    assert main([*map(str, pair), "--output-dir", str(out)]) == 0

    stdout = capsys.readouterr().out
    assert "SSIM score:" in stdout
    assert (out / "report.png").is_file()


def test_missing_input_is_reported_without_traceback(tmp_path, capsys):
    code = main([str(tmp_path / "nope.png"), str(tmp_path / "nope.png"), "--output-dir", str(tmp_path)])

    assert code == 2
    assert "Image not found" in capsys.readouterr().err


def test_version_flag(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])

    assert exit_info.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_module_entry_point_propagates_exit_code(tmp_path):
    completed = subprocess.run(
        [sys.executable, "-m", "id_tamper_check", str(tmp_path / "a.png"), str(tmp_path / "b.png")],
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 2
    assert "Traceback" not in completed.stderr
