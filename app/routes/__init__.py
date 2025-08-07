# routes/__init__.py

from flask import Blueprint

# This function will be called in your main app to register all route blueprints
def register_routes(app):
    from .auth_routes import auth_bp
    from .dashboard_routes import dashboard_bp
    from .chat_routes import chat_bp
    from .skill_routes import skill_bp
    from .request_routes import request_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(skill_bp)
    app.register_blueprint(request_bp)
