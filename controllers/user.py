from flask import Blueprint, render_template, redirect, request, flash, url_for, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import User, Product, Order, Consultation

user_bp = Blueprint('user', __name__)

@user_bp.route('/')
def home():
    products = Product.query.filter_by(status='aktif').all()
    return render_template('user/index.html', products=products)

@user_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    results = Product.query.filter(
        Product.status == 'aktif',
        Product.nama_laptop.ilike(f"%{q}%")
    ).limit(6).all()

    data = [{
        'id': p.id,
        'nama': p.nama_laptop,
        'harga': p.harga,
        'gambar': p.gambar
    } for p in results]

    return jsonify(data)

@user_bp.route('/akun')
@login_required
def akun():
    if current_user.role != 'user':
        return redirect(url_for('user.home'))
    
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.id.desc()).all()
    notifications = Consultation.query.filter_by(user_id=current_user.id).all()
    
    return render_template('user/akun.html', orders=user_orders, notifications=notifications)

@user_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    if current_user.role != 'user':
        return redirect(url_for('user.home'))

    current_user.no_hp = request.form.get('no_hp')
    current_user.umur = request.form.get('umur')
    current_user.alamat = request.form.get('alamat')

    try:
        db.session.commit()
        flash('Profil berhasil diperbarui!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Terjadi kesalahan saat memperbarui profil.', 'danger')

    return redirect(url_for('user.akun'))

@user_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    try:
        p_id = request.form.get('produk_id')
        produk = Product.query.get(p_id)
        if not produk:
            return jsonify({'status': 'error', 'message': 'Produk tidak ditemukan'}), 404

        new_order = Order(
            user_id=current_user.id,
            produk_id=p_id,
            nama_penerima=request.form.get('nama_penerima'),
            no_hp=request.form.get('no_hp'),
            alamat_lengkap=request.form.get('alamat_lengkap'),
            bank_pilihan=request.form.get('bank_pilihan'),
            harga_saat_beli=produk.harga,
            status='pending'
        )

        db.session.add(new_order)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Pesanan berhasil dibuat!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@user_bp.route('/submit_consultation', methods=['POST'])
@login_required
def submit_consultation():
    try:
        nama = request.form.get('nama_user')
        wa = request.form.get('wa_user')
        if not all([nama, wa, request.form.get('kategori'), request.form.get('pesan')]):
            return jsonify({'status': 'error', 'message': 'Semua field harus diisi'}), 400

        new_consul = Consultation(
            user_id=current_user.id,
            nama_wa=f"{nama} - {wa}",
            kategori_kebutuhan=request.form.get('kategori'),
            pesan_user=request.form.get('pesan'),
            status='pending'
        )
        db.session.add(new_consul)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    