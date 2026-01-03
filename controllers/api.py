from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from extensions import db
from models import User, Product, Order, Consultation

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/products/<int:id>', methods=['GET']) # Cukup /products/<id>
def get_product_detail_api(id):
    p = Product.query.get_or_404(id)
    return jsonify({
        "id": p.id,
        "nama": p.nama_laptop,
        "harga": p.harga,
        "status": p.status,
        "gambar": p.gambar,
        "spesifikasi": p.spesifikasi_singkat,
        "deskripsi": p.deskripsi_lengkap
    }), 200

@api_bp.route('/products', methods=['GET']) # Cukup /products
def api_get_products():
    products = Product.query.all()
    return jsonify([
        {
            "id": p.id,
            "nama": p.nama_laptop,
            "harga": p.harga,
            "status": p.status
        } for p in products
    ])

@api_bp.route('/products', methods=['POST']) # Cukup /products
@login_required
def create_product_api():
    if current_user.role != 'admin':
        return jsonify({"error": "Forbidden"}), 403
    
    data = request.json
    new_product = Product(
        nama_laptop=data.get('nama_laptop'),
        spesifikasi_singkat=data.get('spesifikasi_singkat'),
        harga=data.get('harga')
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"status": "created", "id": new_product.id}), 201

@api_bp.route('/products/<int:id>', methods=['PUT'])
@login_required
def update_product_api(id):
    if current_user.role != 'admin':
        return jsonify({"error": "Forbidden"}), 403

    product = Product.query.get_or_404(id)
    data = request.json

    if not data:
        return jsonify({"error": "No data provided"}), 400

    product.nama_laptop = data.get('nama_laptop', product.nama_laptop)
    product.harga = data.get('harga', product.harga)
    product.spesifikasi_singkat = data.get('spesifikasi_singkat', product.spesifikasi_singkat)
    
    try:
        db.session.commit()
        return jsonify({"status": "updated", "id": product.id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/products/<int:id>', methods=['DELETE'])
@login_required
def delete_product_api(id):
    if current_user.role != 'admin':
        return jsonify({"error": "Forbidden"}), 403

    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"status": "deleted"}), 200

@api_bp.route('/orders/<int:id>/status', methods=['PATCH'])
@login_required
def update_order_status_api(id):
    if current_user.role != 'admin':
        return jsonify({"error": "Forbidden"}), 403

    order = Order.query.get_or_404(id)
    data = request.json
    order.status = data.get('status', order.status)
    db.session.commit()

    return jsonify({
        "status": "success",
        "order_id": order.id,
        "new_status": order.status
    }), 200

@api_bp.route('/consultations', methods=['GET'])
@login_required
def get_consultations_api():
    if current_user.role != 'admin':
        return jsonify({"error": "Forbidden"}), 403

    consultations = Consultation.query.all()
    return jsonify([{
        "id": c.id,
        "user_id": c.user_id,
        "status": c.status
    } for c in consultations])