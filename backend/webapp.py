from .app import app


def run(q):
    """Start the Flask web application."""
    # The queue is unused but kept for a consistent interface
    app.run(host="0.0.0.0", port=5000, debug=False)
