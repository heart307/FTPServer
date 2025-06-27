from datetime import datetime
from app import db
import json

class SystemConfig(db.Model):
    """系统配置模型"""
    __tablename__ = 'system_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    config_type = db.Column(db.String(20), default='string')  # string, int, float, bool, json
    is_public = db.Column(db.Boolean, default=False)  # 是否可以公开访问
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, key, value, description=None, config_type='string', is_public=False):
        self.key = key
        self.set_value(value)
        self.description = description
        self.config_type = config_type
        self.is_public = is_public
    
    def set_value(self, value):
        """设置配置值"""
        if self.config_type == 'json':
            self.value = json.dumps(value) if value is not None else None
        elif self.config_type == 'bool':
            self.value = str(bool(value)) if value is not None else None
        else:
            self.value = str(value) if value is not None else None
    
    def get_value(self):
        """获取配置值"""
        if self.value is None:
            return None
        
        if self.config_type == 'int':
            return int(self.value)
        elif self.config_type == 'float':
            return float(self.value)
        elif self.config_type == 'bool':
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.config_type == 'json':
            return json.loads(self.value)
        else:
            return self.value
    
    @classmethod
    def get_config(cls, key, default=None):
        """获取配置值"""
        config = cls.query.filter_by(key=key).first()
        return config.get_value() if config else default
    
    @classmethod
    def set_config(cls, key, value, description=None, config_type='string', is_public=False):
        """设置配置值"""
        config = cls.query.filter_by(key=key).first()
        if config:
            config.set_value(value)
            if description:
                config.description = description
            config.config_type = config_type
            config.is_public = is_public
        else:
            config = cls(key, value, description, config_type, is_public)
            db.session.add(config)
        
        db.session.commit()
        return config
    
    @classmethod
    def get_public_configs(cls):
        """获取所有公开配置"""
        configs = cls.query.filter_by(is_public=True).all()
        return {config.key: config.get_value() for config in configs}
    
    @classmethod
    def init_default_configs(cls):
        """初始化默认配置"""
        default_configs = [
            # 任务调度配置
            ('scheduler.max_concurrent_tasks', 10, '最大并发任务数', 'int', True),
            ('scheduler.max_ftp_connections', 20, '最大FTP连接数', 'int', True),
            ('scheduler.default_bandwidth_limit', 10240, '默认带宽限制(KB/s)', 'int', True),
            ('scheduler.time_slice_seconds', 30, '时间片长度(秒)', 'int', False),
            ('scheduler.preemption_enabled', True, '是否启用抢占', 'bool', False),
            ('scheduler.starvation_threshold', 300, '饥饿阈值(秒)', 'int', False),
            
            # 文件传输配置
            ('transfer.chunk_size', 8192, '传输块大小(字节)', 'int', False),
            ('transfer.max_retries', 3, '最大重试次数', 'int', True),
            ('transfer.timeout', 30, '传输超时时间(秒)', 'int', True),
            ('transfer.verify_checksum', True, '是否验证校验和', 'bool', True),
            
            # 文件夹监控配置
            ('monitor.default_scan_interval', 300, '默认扫描间隔(秒)', 'int', True),
            ('monitor.max_monitors_per_user', 10, '每用户最大监控数', 'int', True),
            
            # 系统配置
            ('system.max_upload_size', 1073741824, '最大上传文件大小(字节)', 'int', True),
            ('system.log_retention_days', 30, '日志保留天数', 'int', False),
            ('system.enable_registration', True, '是否允许用户注册', 'bool', True),
            
            # 安全配置
            ('security.jwt_expires_hours', 24, 'JWT过期时间(小时)', 'int', False),
            ('security.max_login_attempts', 5, '最大登录尝试次数', 'int', False),
            ('security.lockout_duration', 300, '锁定持续时间(秒)', 'int', False),
        ]
        
        for key, value, description, config_type, is_public in default_configs:
            if not cls.query.filter_by(key=key).first():
                cls.set_config(key, value, description, config_type, is_public)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.get_value(),
            'description': self.description,
            'config_type': self.config_type,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<SystemConfig {self.key}: {self.value}>'
