from datetime import datetime
from app import db

class OperationLog(db.Model):
    """操作日志模型"""
    __tablename__ = 'operation_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    site_id = db.Column(db.Integer, db.ForeignKey('ftp_sites.id'), index=True)
    task_id = db.Column(db.Integer, db.ForeignKey('transfer_tasks.id'), index=True)
    monitor_id = db.Column(db.Integer, db.ForeignKey('folder_monitors.id'), index=True)
    
    # 操作信息
    operation = db.Column(db.String(50), nullable=False, index=True)  # connect, disconnect, upload, download, delete, etc.
    target_path = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, index=True)  # success, failed, warning
    message = db.Column(db.Text)
    
    # 请求信息
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    # 时间信息
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # 额外数据（JSON格式）
    extra_data = db.Column(db.Text)
    
    def __init__(self, user_id, operation, status, message=None, **kwargs):
        self.user_id = user_id
        self.operation = operation
        self.status = status
        self.message = message
        
        # 设置可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def log_operation(cls, user_id, operation, status, message=None, **kwargs):
        """记录操作日志"""
        log = cls(
            user_id=user_id,
            operation=operation,
            status=status,
            message=message,
            **kwargs
        )
        db.session.add(log)
        db.session.commit()
        return log
    
    @classmethod
    def log_success(cls, user_id, operation, message=None, **kwargs):
        """记录成功操作"""
        return cls.log_operation(user_id, operation, 'success', message, **kwargs)
    
    @classmethod
    def log_failure(cls, user_id, operation, message=None, **kwargs):
        """记录失败操作"""
        return cls.log_operation(user_id, operation, 'failed', message, **kwargs)
    
    @classmethod
    def log_warning(cls, user_id, operation, message=None, **kwargs):
        """记录警告操作"""
        return cls.log_operation(user_id, operation, 'warning', message, **kwargs)
    
    @classmethod
    def cleanup_old_logs(cls, days=30):
        """清理旧日志"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        old_logs = cls.query.filter(cls.created_at < cutoff_date)
        count = old_logs.count()
        old_logs.delete()
        db.session.commit()
        return count
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'site_id': self.site_id,
            'task_id': self.task_id,
            'monitor_id': self.monitor_id,
            'operation': self.operation,
            'target_path': self.target_path,
            'status': self.status,
            'message': self.message,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'extra_data': self.extra_data
        }
    
    def __repr__(self):
        return f'<OperationLog {self.id}: {self.operation} {self.status}>'
