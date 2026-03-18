"""
run.py
Entry point for the Resume Keyword Analyzer Flask application.

Usage:
    python run.py

API endpoints:
    GET  /api/health   — health check
    POST /api/upload   — upload resume + JD files
    POST /api/analyse  — analyse text directly (JSON)
    POST /api/report   — get detailed text report (JSON)
"""

from flask import Flask
from app.routes import api


def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload size
    app.register_blueprint(api, url_prefix='/api')

    @app.errorhandler(413)
    def too_large(e):
        from flask import jsonify
        return jsonify({"error": "File too large. Maximum size is 5MB."}), 413

    @app.errorhandler(404)
    def not_found(e):
        from flask import jsonify
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        from flask import jsonify
        return jsonify({"error": "Method not allowed"}), 405

    return app


if __name__ == '__main__':
    app = create_app()
    print("Resume Keyword Analyzer running at http://localhost:5000")
    print("Endpoints:")
    print("  GET  /api/health")
    print("  POST /api/upload   (multipart/form-data: resume, jd)")
    print("  POST /api/analyse  (JSON: resume_text, jd_text)")
    print("  POST /api/report   (JSON: resume_text, jd_text)")
    app.run(debug=True, port=5000)
