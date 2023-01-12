import pytest
import json
from model_merge.merge import patch, get_diff, calc_reversed_diffs


@pytest.mark.parametrize(
    "original_asis_file, emulated_asis_file, emulated_tobe_file, expected_file",
    [
        (
            "./testdata/obvious/original_asis.json",
            "./testdata/obvious/emulated_asis.json",
            "./testdata/obvious/emulated_tobe.json",
            "./testdata/obvious/patch_expected.json",
        ),
        (
            "./testdata/patch-change-val/original_asis.json",
            "./testdata/patch-change-val/emulated_asis.json",
            "./testdata/patch-change-val/emulated_tobe.json",
            "./testdata/patch-change-val/patch_expected.json",
        ),
    ],
)
def test_patch(original_asis_file, emulated_asis_file, emulated_tobe_file, expected_file):
    original_asis, emulated_asis, emulated_tobe, expected = map(
        lambda filename: json.load(open(filename)),
        [original_asis_file, emulated_asis_file, emulated_tobe_file, expected_file],
    )
    patched_original_asis = patch(original_asis, emulated_asis, emulated_tobe)
    assert patched_original_asis == expected


@pytest.mark.parametrize(
    "original_asis_file, patched_original_asis_file, expected_file",
    [
        (
            "./testdata/obvious/original_asis.json",
            "./testdata/obvious/patch_expected.json",
            "./testdata/obvious/diff_expected.json",
        ),
        (
            "./testdata/patch-change-val/original_asis.json",
            "./testdata/patch-change-val/patch_expected.json",
            "./testdata/patch-change-val/diff_expected.json",
        ),
    ],
)
def test_get_diff(original_asis_file, patched_original_asis_file, expected_file):
    original_asis, patched_original_asis, expected = map(
        lambda filename: json.load(open(filename)),
        [original_asis_file, patched_original_asis_file, expected_file],
    )
    diff = get_diff(original_asis, patched_original_asis)
    assert diff == expected


@pytest.mark.parametrize(
    "original_asis_file, diff_file, expected_file",
    [
        (
            "./testdata/obvious/original_asis.json",
            "./testdata/obvious/diff_expected.json",
            "./testdata/obvious/rdiffs_expected.json",
        ),
        (
            "./testdata/patch-change-val/original_asis.json",
            "./testdata/patch-change-val/diff_expected.json",
            "./testdata/patch-change-val/rdiffs_expected.json",
        ),
    ],
)
def test_calc_reversed_diffs(original_asis_file, diff_file, expected_file):
    original_asis, diff, expected = map(
        lambda filename: json.load(open(filename)),
        [original_asis_file, diff_file, expected_file],
    )
    print(diff)
    rdiffs = calc_reversed_diffs(diff, original_asis)
    assert rdiffs == expected


if __name__ == "__main__":
    pytest.main(["-vv", __file__])
