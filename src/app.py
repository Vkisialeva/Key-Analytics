from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics
try:
    from src.EfficiencyMetrics import time_to_recover, compute_distance
except ModuleNotFoundError:
    from EfficiencyMetrics import time_to_recover, compute_distance
app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Home route
@app.route("/")
def home():
    return "API is running!"

# Metrics route
@app.route("/metrics")
def metrics():
    player_positions = [
        (0.50, 0.90),
        (0.48, 0.88),
        (0.46, 0.86),
        (0.42, 0.82),
        (0.50, 0.90),
    ]

    fps = 30

    ttr = time_to_recover(player_positions, fps)
    distance = compute_distance(player_positions)

    return jsonify({
        "time_to_recover": ttr,
        "distance": distance
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)