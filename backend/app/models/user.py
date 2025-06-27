from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(45))
    
    # 关系
    ftp_sites = db.relationship('FtpSite', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    transfer_tasks = db.relationship('TransferTask', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    folder_monitors = db.relationship('FolderMonitor', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    operation_logs = db.relationship('OperationLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self, ip_address=None):
        """更新最后登录时间"""
        self.last_login_at = datetime.utcnow()
        if ip_address:
            self.last_login_ip = ip_address
        db.session.commit()
    
    def to_dict(self, include_sensitive=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'last_login_ip': self.last_login_ip
        }
        
        if include_sensitive:
            data.update({
                'ftp_sites_count': self.ftp_sites.count(),
                'active_tasks_count': self.transfer_tasks.filter_by(status='running').count(),
                'total_tasks_count': self.transfer_tasks.count()
            })
        
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'
