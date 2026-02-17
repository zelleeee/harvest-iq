from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from config.development import DevelopmentConfig
from app.locales import get_locale

# 1. Initialize extensions globally
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()

def create_app(config=DevelopmentConfig):
    # 2. Create the app instance
    app = Flask(__name__)
    app.config.from_object(config)

    # 3. Bind extensions to the app instance
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # 4. MOVED: Context Processor now lives inside the function
    @app.context_processor
    def inject_locale():
        from flask import session
        lang = session.get('lang', 'en')
        return {'t': get_locale(lang), 'lang': lang}

    # 5. Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.products import products_bp
    from app.routes.orders import orders_bp
    from app.routes.users import users_bp
    from app.routes.search import search_bp
    from app.routes.cart import cart_bp
    from app.routes.payment import payment_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(search_bp, url_prefix='/search')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(payment_bp, url_prefix='/payment')

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    # 6. Database and Seeding
    with app.app_context():
        db.create_all()
        from app.utils.helpers import seed_categories
        seed_categories()

    return app