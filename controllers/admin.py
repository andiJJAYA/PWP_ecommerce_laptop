import os
from flask import Blueprint, jsonify, render_template, redirect, request, flash, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import User, Product, Order, Consultation

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@admin_bp.route('/')
@login_required
def dashboard(): 
    if current_user.role != 'admin':
        return redirect(url_for('user.home'))
    
    products = Product.query.all()
    orders = Order.query.order_by(Order.created_at.desc()).all()
    consultations = Consultation.query.order_by(Consultation.id.desc()).all()
    
    stats = {
        'total_user': User.query.filter_by(role='user').count(),
        'total_produk': Product.query.count(),
        'total_pesanan': Order.query.filter_by(status='pending').count(),
        'total_konsultasi': Consultation.query.filter_by(status='pending').count()
    }
    
    return render_template('admin/dashboard.html', 
                           all_products=products, 
                           all_orders=orders, 
                           all_consuls=consultations,
                           **stats)

@admin_bp.route('/product/add', methods=['POST'])
@login_required
def add_product():
    if current_user.role != 'admin': return redirect(url_for('user.home'))
    
    file = request.files.get('gambar')
    filename = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Gunakan current_app.config
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

    new_product = Product(
        nama_laptop=request.form.get('nama_laptop'),
        spesifikasi_singkat=request.form.get('spesifikasi_singkat'),
        deskripsi_lengkap=request.form.get('deskripsi_lengkap'),
        harga=request.form.get('harga'),
        gambar=filename,
        status='aktif'
    )
    db.session.add(new_product)
    db.session.commit()
    flash('Produk berhasil ditambahkan!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/product/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    if current_user.role != 'admin':
        return redirect(url_for('user.home'))
    
    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        product.nama_laptop = request.form.get('nama_laptop')
        product.spesifikasi_singkat = request.form.get('spesifikasi_singkat')
        product.deskripsi_lengkap = request.form.get('deskripsi_lengkap')
        product.harga = request.form.get('harga')
        product.status = request.form.get('status')

        file = request.files.get('gambar')
        if file and allowed_file(file.filename):
            if product.gambar:
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.gambar)
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            product.gambar = filename

        try:
            db.session.commit()
            flash('Produk berhasil diperbarui!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal memperbarui produk: {str(e)}', 'danger')
            
        return redirect(url_for('admin.dashboard'))

    return jsonify({
        'id': product.id,
        'nama': product.nama_laptop,
        'spesifikasi': product.spesifikasi_singkat,
        'deskripsi': product.deskripsi_lengkap,
        'harga': product.harga,
        'status': product.status,
        'gambar': product.gambar
    })

@admin_bp.route('/product/delete/<int:id>')
@login_required
def delete_product(id):
    if current_user.role != 'admin': return redirect(url_for('user.home'))
    
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Produk berhasil dihapus!', 'danger')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/order/update/<int:id>/<string:action>')
@login_required
def update_order_status(id, action):
    if current_user.role != 'admin': return redirect(url_for('user.home'))
        
    order = Order.query.get_or_404(id)
    if action == 'confirm':
        order.status = 'confirmed'
        flash(f'Pesanan #{id} dikonfirmasi!', 'success')
    elif action == 'cancel':
        order.status = 'canceled'
        flash(f'Pesanan #{id} dibatalkan!', 'warning')
        
    db.session.commit()
    return redirect(url_for('admin.dashboard') + '#manage-orders')

@admin_bp.route('/consultation/reply/<int:id>', methods=['POST'])
@login_required
def reply_consultation(id):
    if current_user.role != 'admin': return redirect(url_for('user.home'))
        
    consult = Consultation.query.get_or_404(id)
    balasan = request.form.get('balasan_admin')
    
    if balasan:
        consult.balasan_admin = balasan
        consult.status = 'replied'
        db.session.commit()
        flash(f'Balasan untuk ID #{id} terkirim!', 'success')
    
    return redirect(url_for('admin.dashboard') + '#manage-consultations')

@admin_bp.route('/consultation/delete/<int:id>')
@login_required
def delete_consultation(id):
    if current_user.role != 'admin': return redirect(url_for('user.home'))
    
    consult = Consultation.query.get_or_404(id)
    db.session.delete(consult)
    db.session.commit()
    flash('Konsultasi dihapus!', 'warning')
    return redirect(url_for('admin.dashboard') + '#manage-consultations')