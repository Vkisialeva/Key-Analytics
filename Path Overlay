import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 1. DIRECTION CLASSIFICATION
# ============================================================

def classify_direction(du, dv, player_side="near", threshold=0.002):
    """Classify movement direction."""
    
    # Horizontal
    if abs(du) > abs(dv):
        if du > threshold:  return "right"
        if du < -threshold: return "left"

    # Vertical (depends on player side)
    if player_side == "near":
        if dv < -threshold: return "forward"
        if dv >  threshold: return "backward"
    else:
        if dv >  threshold: return "forward"
        if dv < -threshold: return "backward"

    return None


# ============================================================
# 2. RECOVERY PATH EXTRACTION
# ============================================================

def extract_recovery_paths(player_positions, fps, player_side="near"):
    """
    Returns a dict:
    {
        "left":    [path1, path2, ...],
        "right":   [...],
        "forward": [...],
        "backward":[...]
    }
    where each path is a list of (u,v) points showing the route
    from movement start → recovery.
    """
    positions = np.array(player_positions)
    
    # Neutral zone
    neutral_u = (0.35, 0.65)
    neutral_v = (0.75, 1.00) if player_side == "near" else (0.00, 0.25)

    def is_neutral(u, v):
        return neutral_u[0] <= u <= neutral_u[1] and neutral_v[0] <= v <= neutral_v[1]

    recovery_paths = {
        "left": [], "right": [], "forward": [], "backward": []
    }

    last_dir = None
    movement_start_idx = None
    path_points = []

    for i in range(1, len(positions)):
        u1,v1 = positions[i - 1]
        u2,v2 = positions[i]

        du = u2 - u1
        dv = v2 - v1

        direction = classify_direction(du, dv, player_side)

        # Movement starts
        if direction and last_dir is None:
            last_dir = direction
            movement_start_idx = i
            path_points = [positions[i-1].tolist()]

        # If in movement, record the path
        if last_dir:
            path_points.append([u2, v2])

        # Recovered
        if last_dir and is_neutral(u2, v2):
            recovery_paths[last_dir].append(path_points.copy())
            last_dir = None
            movement_start_idx = None
            path_points = []

    return recovery_paths


# ============================================================
# 3. DRAW PATH OVERLAY VISUALIZATION
# ============================================================

def plot_recovery_paths(recovery_paths, player_side="near"):
    """Plot the recovery paths for all directions."""
    
    fig, ax = plt.subplots(figsize=(5,10))

    # Court outline (simple visualization)
    ax.add_patch(plt.Rectangle((0,0), 1,1,
                               fill=True, alpha=0.2, edgecolor="black", facecolor="lightblue"))

    # Neutral zone
    if player_side == "near":
        nz = plt.Rectangle((0.35, 0.75), 0.30, 0.25,
                           fill=True, alpha=0.2, color="green")
    else:
        nz = plt.Rectangle((0.35, 0.00), 0.30, 0.25,
                           fill=True, alpha=0.2, color="green")

    ax.add_patch(nz)

    # Colors for each direction
    colors = {
        "left": "red",
        "right": "blue",
        "forward": "purple",
        "backward": "orange"
    }

    # Plot each recovery path
    for direction, paths in recovery_paths.items():
        for path in paths:
            path = np.array(path)
            ax.plot(path[:,0], path[:,1], color=colors[direction], alpha=0.7, linewidth=2)

    # Labels
    ax.set_title("Recovery Path Overlay")
    ax.set_xlim(0,1)
    ax.set_ylim(1,0)  # tennis court orientation
    ax.set_aspect("equal")
    ax.axis("off")
    plt.show()


# ============================================================
# 4. EXAMPLE USAGE
# ============================================================

# Example normalized tracking data (replace with your actual tracker output)
player_positions = [
    (0.50,0.90), (0.45,0.88), (0.40,0.85), (0.38,0.82), (0.50,0.90),
    (0.50,0.90), (0.55,0.92), (0.60,0.94), (0.62,0.96), (0.50,0.90)
]
fps = 30
player_side = "near"

# Compute recovery paths
recovery_paths = extract_recovery_paths(player_positions, fps, player_side)

# Visualize them
plot_recovery_paths(recovery_paths, player_side)
