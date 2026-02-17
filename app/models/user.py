from app import db, login_manager, bcrypt
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='buyer')  # 'farmer' or 'buyer'
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    region = db.Column(db.String(100))
    profile_image = db.Column(db.String(255), default='default_profile.jpg')
    bio = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    products = db.relationship('Product', backref='farmer', lazy=True, foreign_keys='Product.farmer_id')
    orders_as_buyer = db.relationship('Order', backref='buyer', lazy=True, foreign_keys='Order.buyer_id')
    reviews = db.relationship('Review', backref='reviewer', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_farmer(self):
        return self.role == 'farmer'

    @property
    def average_rating(self):
        if not self.products:
            return 0
        ratings = []
        for product in self.products:
            for review in product.reviews:
                ratings.append(review.rating)
        return round(sum(ratings) / len(ratings), 1) if ratings else 0

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
    