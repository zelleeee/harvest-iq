import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename
from app import db

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_image(file, subfolder='products'):
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
        os.makedirs(upload_path, exist_ok=True)
        file.save(os.path.join(upload_path, filename))
        return f"{subfolder}/{filename}"
    return None

def seed_categories():
    from app.models.category import Category
    categories = [
        {'name': 'Vegetables', 'name_tl': 'Gulay', 'icon': '🥦'},
        {'name': 'Fruits', 'name_tl': 'Prutas', 'icon': '🍎'},
        {'name': 'Rice & Grains', 'name_tl': 'Bigas at Butil', 'icon': '🌾'},
        {'name': 'Herbs & Spices', 'name_tl': 'Halamang Gamot', 'icon': '🌿'},
        {'name': 'Livestock', 'name_tl': 'Hayop', 'icon': '🐄'},
        {'name': 'Poultry & Eggs', 'name_tl': 'Manok at Itlog', 'icon': '🥚'},
        {'name': 'Fish & Seafood', 'name_tl': 'Isda at Pagkain-dagat', 'icon': '🐟'},
        {'name': 'Organic', 'name_tl': 'Organiko', 'icon': '🌱'},
        {'name': 'Root Crops', 'name_tl': 'Ugat na Pananim', 'icon': '🥕'},
        {'name': 'Flowers & Plants', 'name_tl': 'Bulaklak at Halaman', 'icon': '🌸'},
    ]
    for cat_data in categories:
        if not Category.query.filter_by(name=cat_data['name']).first():
            cat = Category(**cat_data)
            db.session.add(cat)
    db.session.commit()

def format_price(amount):
    return f"₱{amount:,.2f}"

def get_status_badge(status):
    badges = {
        'pending': 'warning',
        'confirmed': 'info',
        'processing': 'primary',
        'shipped': 'secondary',
        'delivered': 'success',
        'cancelled': 'danger',
        'refunded': 'dark',
    }
    return badges.get(status, 'light')