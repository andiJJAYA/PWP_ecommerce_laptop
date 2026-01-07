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

# ENDPOINT UNTUK USER ==========
@api_bp.route('/orders', methods=['POST'])
@login_required
def create_order_api():
    """Endpoint bagi User untuk membuat pesanan baru"""
    data = request.json
    if not data or 'product_id' not in data:
        return jsonify({"error": "Data produk tidak lengkap"}), 400
    
    product = Product.query.get_or_404(data.get('product_id'))
    new_order = Order(
        user_id=current_user.id,
        produk_id=product.id,
        nama_penerima=data.get('nama_penerima'),
        no_hp=data.get('no_hp'),
        alamat_lengkap=data.get('alamat_lengkap'),
        bank_pilihan=data.get('bank_pilihan'),
        harga_saat_beli=product.harga,
        status='pending'
    )
    
    try:
        db.session.add(new_order)
        db.session.commit()
        return jsonify({"status": "success", "message": "Pesanan berhasil dibuat", "order_id": new_order.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/consultations', methods=['POST'])
@login_required
def create_consultation_api():
    """Endpoint bagi User untuk mengirim pesan konsultasi"""
    data = request.json
    if not data or 'pesan_user' not in data:
        return jsonify({"error": "Pesan tidak boleh kosong"}), 400

    new_consul = Consultation(
        user_id=current_user.id,
        nama_wa=data.get('nama_wa', current_user.username),
        kategori_kebutuhan=data.get('kategori', 'Umum'),
        pesan_user=data.get('pesan_user'),
        status='pending'
    )
    
    db.session.add(new_consul)
    db.session.commit()
    return jsonify({"status": "success", "message": "Konsultasi terkirim", "id": new_consul.id}), 201

# ENDPOINT TAMBAHAN UNTUK ADMIN ===============
@api_bp.route('/consultations/<int:id>/reply', methods=['PATCH'])
@login_required
def reply_consultation_api(id):
    """Endpoint bagi Admin untuk membalas konsultasi"""
    if current_user.role != 'admin':
        return jsonify({"error": "Forbidden"}), 403

    consul = Consultation.query.get_or_404(id)
    data = request.json
    
    if not data or 'balasan_admin' not in data:
        return jsonify({"error": "Balasan tidak boleh kosong"}), 400

    consul.balasan_admin = data.get('balasan_admin')
    consul.status = 'replied'
    db.session.commit()
    return jsonify({"status": "success", "message": "Balasan terkirim"}), 200

@api_bp.route('/consultations/<int:id>', methods=['DELETE'])
@login_required
def delete_consultation_api(id):
    """Endpoint bagi Admin untuk menghapus konsultasi"""
    if current_user.role != 'admin':
        return jsonify({"error": "Forbidden"}), 403

    consult = Consultation.query.get_or_404(id)
    try:
        db.session.delete(consult)
        db.session.commit()
        return jsonify({"status": "success", "message": "Konsultasi berhasil dihapus"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500