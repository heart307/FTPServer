from datetime import datetime
from app import db
from cryptography.fernet import Fernet
import os
import base64

class FtpSite(db.Model):
    """FTP站点模型"""
    __tablename__ = 'ftp_sites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    host = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, default=21, nullable=False)
    username = db.Column(db.String(100))
    password_encrypted = db.Column(db.Text)  # 加密存储的密码
    protocol = db.Column(db.String(10), default='FTP', nullable=False)  # FTP, FTPS, SFTP
    passive_mode = db.Column(db.Boolean, default=True, nullable=False)
    encoding = db.Column(db.String(20), default='utf-8', nullable=False)
    timeout = db.Column(db.Integer, default=30, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_connected_at = db.Column(db.DateTime)
    connection_count = db.Column(db.Integer, default=0, nullable=False)
    
    # 关系
    transfer_tasks = db.relationship('TransferTask', backref='ftp_site', lazy='dynamic', cascade='all, delete-orphan')
    folder_monitors = db.relationship('FolderMonitor', backref='ftp_site', lazy='dynamic', cascade='all, delete-orphan')
    operation_logs = db.relationship('OperationLog', backref='ftp_site', lazy='dynamic')
    
    def __init__(self, user_id, name, host, port=21, username=None, password=None, protocol='FTP'):
        self.user_id = user_id
        self.name = name
        self.host = host
        self.port = port
        self.username = username
        self.protocol = protocol
        if password:
            self.set_password(password)
    
    @property
    def encryption_key(self):
        """获取加密密钥"""
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            # 生成一个新的密钥（生产环境中应该使用固定的密钥）
            key = Fernet.generate_key()
            os.environ['ENCRYPTION_KEY'] = base64.urlsafe_b64encode(key).decode()
        else:
            key = base64.urlsafe_b64decode(key.encode())
        return key
    
    def set_password(self, password):
        """设置加密密码"""
        if password:
            f = Fernet(self.encryption_key)
            self.password_encrypted = f.encrypt(password.encode()).decode()
        else:
            self.password_encrypted = None
    
    def get_password(self):
        """获取解密密码"""
        if self.password_encrypted:
            f = Fernet(self.encryption_key)
            return f.decrypt(self.password_encrypted.encode()).decode()
        return None
    
    def update_connection_stats(self):
        """更新连接统计"""
        self.last_connected_at = datetime.utcnow()
        self.connection_count += 1
        db.session.commit()
    
    def test_connection(self):
        """测试FTP连接"""
        from app.core.ftp_client import FtpClient
        try:
            client = FtpClient(self)
            result = client.test_connection()
            if result['success']:
                self.update_connection_stats()
            return result
        except Exception as e:
            return {
                'success': False,
                'message': f'连接测试失败: {str(e)}'
            }
    
    def to_dict(self, include_password=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'protocol': self.protocol,
            'passive_mode': self.passive_mode,
            'encoding': self.encoding,
            'timeout': self.timeout,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_connected_at': self.last_connected_at.isoformat() if self.last_connected_at else None,
            'connection_count': self.connection_count,
            'active_tasks_count': self.transfer_tasks.filter_by(status='running').count(),
            'total_tasks_count': self.transfer_tasks.count()
        }
        
        if include_password:
            data['password'] = self.get_password()
        
        return data
    
    def __repr__(self):
        return f'<FtpSite {self.name}@{self.host}:{self.port}>'
