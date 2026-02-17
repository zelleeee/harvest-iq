from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.product import Product
from app.models.order import Order
from app.utils.helpers import save_image
from app.utils.constants import PH_REGIONS, PRODUCT_UNITS

users_bp = Blueprint('users', __name__)

@users_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_farmer:
        products = Product.query.filter_by(farmer_id=current_user.id).order_by(Product.created_at.desc()).all()
        farmer_product_ids = [p.id for p in products]
        from app.models.order import OrderItem
        order_ids = db.session.query(OrderItem.order_id)\
                              .filter(OrderItem.product_id.in_(farmer_product_ids)).distinct().all()
        recent_orders = Order.query.filter(Order.id.in_([o[0] for o in order_ids]))\
                                   .order_by(Order.created_at.desc()).limit(5).all()
        total_revenue = sum(
            item.subtotal for order in Order.query.filter(Order.id.in_([o[0] for o in order_ids])).all()
            for item in order.items if item.product.farmer_id == current_user.id
        )
        return render_template('dashboard/farmer.html', products=products,
                               recent_orders=recent_orders, total_revenue=total_revenue,
                               units=PRODUCT_UNITS)
    else:
        orders = Order.query.filter_by(buyer_id=current_user.id)\
                            .order_by(Order.created_at.desc()).limit(5).all()
        return render_template('dashboard/buyer.html', orders=orders)

@users_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name', '').strip()
        current_user.phone = request.form.get('phone', '').strip()
        current_user.address = request.form.get('address', '').strip()
        current_user.region = request.form.get('region', '')
        current_user.bio = request.form.get('bio', '').strip()

        image_file = request.files.get('profile_image')
        if image_file and image_file.filename:
            path = save_image(image_file, subfolder='profiles')
            if path:
                current_user.profile_image = path

        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('users.profile'))
    return render_template('users/profile.html', regions=PH_REGIONS)

@users_bp.route('/farmer/<int:farmer_id>')
def farmer_store(farmer_id):
    from app.models.user import User
    farmer = User.query.filter_by(id=farmer_id, role='farmer', is_active=True).first_or_404()
    products = Product.query.filter_by(farmer_id=farmer_id, is_available=True).all()
    return render_template('users/farmer_store.html', farmer=farmer, products=products)
