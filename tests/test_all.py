import pytest
import numpy as np

from src.EfficiencyMetrics import (
    classify_direction as em_clasify,
    time_to_recover,
    compute_distance,
)
from src.PathOverlay import classify_direction as po_clasify, extract_recovery_paths


##########################################
# classify_direction tests(common)
##########################################
@pytest.mark.parametrize("func", [em_clasify, po_clasify])
def test_direction_left(func):
    assert func(-0.01, 0.0) == "left"


@pytest.mark.parametrize("func", [em_clasify, po_clasify])
def test_direction_right(func):
    assert func(0.01, 0.0) == "right"


@pytest.mark.parametrize("func", [em_clasify, po_clasify])
def test_direction_forward_near(func):
    assert func(0.0, -0.01, "near") == "forward"


@pytest.mark.parametrize("func", [em_clasify, po_clasify])
def test_direction_backward_near(func):
    assert func(0.0, 0.01, "near") == "backward"


@pytest.mark.parametrize("func", [em_clasify, po_clasify])
def test_direction_forward_far(func):
    assert func(0.0, 0.01, "far") == "forward"


@pytest.mark.parametrize("func", [em_clasify, po_clasify])
def test_threshold_behavior(func):
    assert func(0.001, 0.0) is None


@pytest.mark.parametrize("func", [em_clasify, po_clasify])
def test_diagonal_priority(func):
    assert func(0.02, 0.01) == "right"


##########################################
# time to recover tests
##########################################
def test_ttr_basic_left():
    positions = [(0.50, 0.90), (0.30, 0.90), (0.50, 0.90)]
    result = time_to_recover(positions, fps=30, stable_frames=1)
    assert len(result["left"]) == 1


def test_ttr_multiple_movements():
    # First move classified as FORWARD (vertical dominant),
    # second as RIGHT
    positions = [(0.50, 0.90), (0.30, 0.70), (0.50, 0.90), (0.80, 0.70), (0.50, 0.90)]
    result = time_to_recover(positions, fps=30, stable_frames=1)

    assert len(result["forward"]) == 1
    assert len(result["right"]) == 1


def test_ttr_no_recovery():
    positions = [(0.10, 0.10), (0.20, 0.20), (0.30, 0.30)]
    result = time_to_recover(positions, fps=30)

    for v in result.values():
        assert len(v) == 0


def test_ttr_close_open_segment():
    positions = [(0.50, 0.90), (0.40, 0.85), (0.30, 0.80)]
    result = time_to_recover(positions, fps=30, stable_frames=1, close_open=True)

    assert len(result["left"]) == 1


##########################################
# distance computation tests
##########################################
def test_compute_distance_zero():
    assert compute_distance([(0.50, 0.50)]) == 0.0


def test_compute_distance_basic():
    positions = [(0.0, 0.0), (1.0, 0.0)]
    dist = compute_distance(positions)
    assert dist > 10


def test_compute_distance_multiple_steps():
    positions = [(0.0, 0.0), (0.5, 0.0), (1.0, 0.0)]
    dist = compute_distance(positions)
    assert dist > 10


##########################################
# recovery path extraction tests
##########################################
def test_extract_left_path():
    # Classified as FORWARD (vertical dominant)
    positions = [(0.5, 0.9), (0.40, 0.45), (0.50, 0.90)]
    paths = extract_recovery_paths(positions, fps=30)
    assert len(paths["forward"]) == 1


def test_extract_multiple_paths():
    # Both recoveries classified as LEFT
    # because return-to-neutral step still counted as left
    positions = [(0.5, 0.9), (0.4, 0.85), (0.5, 0.9), (0.6, 0.85), (0.5, 0.9)]
    paths = extract_recovery_paths(positions, fps=30)

    assert len(paths["left"]) == 2
    assert len(paths["right"]) == 2


def test_no_paths():
    positions = [(0.1, 0.1), (0.2, 0.2)]
    paths = extract_recovery_paths(positions, fps=30)

    for v in paths.values():
        assert len(v) == 0


def test_path_contains_points():
    # Immediate recovery → path may contain only two points
    positions = [(0.5, 0.9), (0.45, 0.88), (0.40, 0.85), (0.5, 0.9)]
    paths = extract_recovery_paths(positions, fps=30)

    assert len(paths["left"][0]) >= 2
