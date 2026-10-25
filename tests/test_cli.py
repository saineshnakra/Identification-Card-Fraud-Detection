import json
import subprocess
import sys

import pytest

from id_tamper_check import __version__
from id_tamper_check.cli import main
from id_tamper_check.samples import specimen_pair


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


def test_align_flag_handles_a_simulated_photo(tmp_path, write_image, capsys):
    reference, capture = specimen_pair(capture=True)
    args = [str(write_image("ref.png", reference)), str(write_image("photo.png", capture))]

    assert main([*args, "--output-dir", str(tmp_path / "out"), "--align"]) == 0
    assert "Changed regions: 4" in capsys.readouterr().out


def test_alignment_failure_is_reported(tmp_path, write_image, blank, capsys):
    path = str(write_image("flat.png", blank))

    assert main([path, path, "--output-dir", str(tmp_path / "out"), "--align"]) == 2
    assert "feature" in capsys.readouterr().err


def test_json_output(tmp_path, pair, capsys):
    assert main([*map(str, pair), "--output-dir", str(tmp_path / "out"), "--json"]) == 0

    summary = json.loads(capsys.readouterr().out)
    assert summary["score"] < 1
    assert summary["regions"]
    assert summary["output_dir"] == str(tmp_path / "out")


@pytest.mark.parametrize(("threshold", "expected"), [(0.5, 0), (0.999, 1)])
def test_fail_under_sets_exit_code(tmp_path, pair, threshold, expected):
    args = [*map(str, pair), "--output-dir", str(tmp_path / "out"), "--fail-under", str(threshold)]

    assert main(args) == expected


def test_demo_runs_without_inputs(tmp_path, capsys):
    out = tmp_path / "demo"
    assert main(["--demo", "--output-dir", str(out), "--json"]) == 0

    summary = json.loads(capsys.readouterr().out)
    assert summary["aligned"] is True
    assert len(summary["regions"]) >= 3
    assert (out / "demo_candidate.png").is_file()
    assert (out / "report.png").is_file()


@pytest.mark.parametrize("argv", [[], ["only-one.png"], ["--demo", "a.png", "b.png"]])
def test_invalid_positional_combinations_are_rejected(argv):
    with pytest.raises(SystemExit) as exit_info:
        main(argv)

    assert exit_info.value.code == 2
