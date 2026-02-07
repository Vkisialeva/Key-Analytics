import numpy as np

# ============================================================
# 1. CLASSIFY MOVEMENT DIRECTION
# ============================================================

def classify_direction(du, dv, player_side="near", threshold=0.002):
    """
    Determine if movement is left, right, forward, or backward
    based on Δu and Δv values and player side.
    """
    # Horizontal movement
    if abs(du) > abs(dv):
        if du > threshold:  return "right"
        if du < -threshold: return "left"

    # Vertical movement (depends on near/far orientation)
    else:
        if player_side == "near":
            if dv < -threshold: return "forward"
            if dv >  threshold: return "backward"
        else:  # far side player sees court flipped
            if dv >  threshold: return "forward"
            if dv < -threshold: return "backward"

    return None


# ============================================================
# 2. TIME TO RECOVER (MAIN METRIC) - IMPROVED
# ============================================================

def time_to_recover(player_positions, fps, player_side="near",
                    threshold=0.002, stable_frames=3, close_open=False):
    """
    Compute Time-to-Recover (TTR) for:
      - left
      - right
      - forward
      - backward

    Improvements:
      - Movement starts only when player LEAVES neutral
      - Direction is debounced via stable_frames
      - Recovery only counted after exiting neutral
      - Optionally closes an open segment at end (close_open=True)
    """
    positions = np.asarray(player_positions, dtype=float)
    if len(positions) < 2:
        return {"left": [], "right": [], "forward": [], "backward": []}

    # Neutral zone definition
    neutral_u = (0.35, 0.65)
    neutral_v = (0.75, 1.00) if player_side == "near" else (0.00, 0.25)

    def is_neutral(u, v):
        return neutral_u[0] <= u <= neutral_u[1] and neutral_v[0] <= v <= neutral_v[1]

    # Storage
    ttr_data = {"left": [], "right": [], "forward": [], "backward": []}

    # State
    active_dir = None
    start_idx = None
    has_exited_neutral = False

    # Direction debounce state
    last_dir = None
    run_len = 0

    prev_neutral = is_neutral(*positions[0])

    for i in range(1, len(positions)):
        u1, v1 = positions[i - 1]
        u2, v2 = positions[i]
        du, dv = (u2 - u1), (v2 - v1)

        curr_neutral = is_neutral(u2, v2)

        direction = classify_direction(du, dv, player_side=player_side, threshold=threshold)

        # Debounce direction
        if direction is not None and direction == last_dir:
            run_len += 1
        else:
            last_dir = direction
            run_len = 1 if direction is not None else 0

        confirmed_dir = last_dir if run_len >= stable_frames else None

        # Start movement: must transition from neutral -> non-neutral
        if active_dir is None:
            if prev_neutral and (not curr_neutral) and confirmed_dir:
                active_dir = confirmed_dir
                start_idx = i
                has_exited_neutral = True

        else:
            if not curr_neutral:
                has_exited_neutral = True

            # End movement: return to neutral after having exited
            if curr_neutral and has_exited_neutral:
                ttr = (i - start_idx) / float(fps)
                ttr_data[active_dir].append(ttr)

                # reset
                active_dir = None
                start_idx = None
                has_exited_neutral = False
                last_dir = None
                run_len = 0

        prev_neutral = curr_neutral

    # Optionally close an open movement at end-of-clip
    if close_open and active_dir is not None and start_idx is not None:
        ttr = (len(positions) - 1 - start_idx) / float(fps)
        ttr_data[active_dir].append(ttr)

    return ttr_data


# ============================================================
# 3. DISTANCE COVERED
# ============================================================

COURT_WIDTH_M  = 10.97   # singles sideline width
COURT_LENGTH_M = 23.78   # baseline to baseline

def compute_distance(player_positions):
    """
    Calculate total real distance run by the player (in meters).
    Uses normalized coordinates mapped to real court dimensions.
    """
    positions = np.asarray(player_positions, dtype=float)
    if len(positions) < 2:
        return 0.0

    diffs = positions[1:] - positions[:-1]
    dx = diffs[:, 0] * COURT_WIDTH_M
    dy = diffs[:, 1] * COURT_LENGTH_M
    return float(np.sqrt(dx * dx + dy * dy).sum())


# ============================================================
# 4. EXAMPLE USAGE
# ============================================================

fps = 30
player_side = "near"
player_positions = [
    (0.50, 0.90),
    (0.48, 0.88),
    (0.46, 0.86),
    (0.42, 0.82),
    (0.50, 0.90),   # back to neutral
    (0.60, 0.85),   # new right movement
    (0.65, 0.83),
    (0.50, 0.90)    # back to neutral
]

ttr_results = time_to_recover(player_positions, fps, player_side,
                              threshold=0.002, stable_frames=1)  # stable_frames=1 for tiny demo
distance_m  = compute_distance(player_positions)

print("TIME TO RECOVER:")
for direction, times in ttr_results.items():
    print(f"  {direction}: {np.mean(times) if times else 0:.2f} sec")

print(f"\nDISTANCE COVERED: {distance_m:.2f} meters")
