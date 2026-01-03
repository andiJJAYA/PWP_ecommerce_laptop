from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    no_hp = db.Column(db.String(20), nullable=True)
    umur = db.Column(db.Integer, nullable=True)
    alamat = db.Column(db.Text, nullable=True)
    role = db.Column(db.Enum('user', 'admin'), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    nama_laptop = db.Column(db.String(150), nullable=False)
    spesifikasi_singkat = db.Column(db.Text, nullable=False)
    deskripsi_lengkap = db.Column(db.Text)
    harga = db.Column(db.Integer, nullable=False)
    gambar = db.Column(db.String(255))
    status = db.Column(db.Enum('aktif', 'nonaktif'), default='aktif')

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    produk_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    produk = db.relationship('Product', backref='orders')
    nama_penerima = db.Column(db.String(100), nullable=False)
    alamat_lengkap = db.Column(db.Text, nullable=False)
    no_hp = db.Column(db.String(20), nullable=False)
    bank_pilihan = db.Column(db.String(50), nullable=False)
    harga_saat_beli = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Consultation(db.Model):
    __tablename__ = 'consultations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    nama_wa = db.Column(db.String(50), nullable=False) # Sesuaikan dengan DB
    kategori_kebutuhan = db.Column(db.String(50), nullable=False)
    pesan_user = db.Column(db.Text, nullable=False) # Sesuaikan dengan DB
    balasan_admin = db.Column(db.Text)
    status = db.Column(db.Enum('pending', 'replied'), default='pending')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())