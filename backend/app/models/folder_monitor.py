from datetime import datetime
from app import db
import json

class FolderMonitor(db.Model):
    """文件夹监控任务模型"""
    __tablename__ = 'folder_monitors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    site_id = db.Column(db.Integer, db.ForeignKey('ftp_sites.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    remote_path = db.Column(db.Text, nullable=False)
    local_path = db.Column(db.Text, nullable=False)
    scan_interval = db.Column(db.Integer, default=300, nullable=False)  # 扫描间隔（秒）
    sync_mode = db.Column(db.String(20), default='incremental', nullable=False)  # incremental, full
    conflict_resolution = db.Column(db.String(20), default='rename', nullable=False)  # overwrite, rename, skip
    filters = db.Column(db.Text)  # JSON格式的过滤规则
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_scan_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 统计信息
    total_files_scanned = db.Column(db.Integer, default=0)
    total_files_downloaded = db.Column(db.Integer, default=0)
    total_bytes_downloaded = db.Column(db.BigInteger, default=0)
    last_error_message = db.Column(db.Text)
    
    # 关系
    file_snapshots = db.relationship('FileSnapshot', backref='folder_monitor', lazy='dynamic', cascade='all, delete-orphan')
    operation_logs = db.relationship('OperationLog', backref='folder_monitor', lazy='dynamic')
    
    def __init__(self, user_id, site_id, name, remote_path, local_path, **kwargs):
        self.user_id = user_id
        self.site_id = site_id
        self.name = name
        self.remote_path = remote_path
        self.local_path = local_path
        
        # 设置可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_filters(self, filters_dict):
        """设置过滤规则"""
        self.filters = json.dumps(filters_dict) if filters_dict else None
    
    def get_filters(self):
        """获取过滤规则"""
        return json.loads(self.filters) if self.filters else {}
    
    def update_scan_stats(self, files_scanned=0, files_downloaded=0, bytes_downloaded=0):
        """更新扫描统计"""
        self.last_scan_at = datetime.utcnow()
        self.total_files_scanned += files_scanned
        self.total_files_downloaded += files_downloaded
        self.total_bytes_downloaded += bytes_downloaded
        db.session.commit()
    
    def set_error(self, error_message):
        """设置错误信息"""
        self.last_error_message = error_message
        db.session.commit()
    
    def clear_error(self):
        """清除错误信息"""
        self.last_error_message = None
        db.session.commit()
    
    def start_monitor(self):
        """启动监控"""
        self.is_active = True
        self.clear_error()
        db.session.commit()
    
    def stop_monitor(self):
        """停止监控"""
        self.is_active = False
        db.session.commit()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'site_id': self.site_id,
            'name': self.name,
            'remote_path': self.remote_path,
            'local_path': self.local_path,
            'scan_interval': self.scan_interval,
            'sync_mode': self.sync_mode,
            'conflict_resolution': self.conflict_resolution,
            'filters': self.get_filters(),
            'is_active': self.is_active,
            'last_scan_at': self.last_scan_at.isoformat() if self.last_scan_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_files_scanned': self.total_files_scanned,
            'total_files_downloaded': self.total_files_downloaded,
            'total_bytes_downloaded': self.total_bytes_downloaded,
            'last_error_message': self.last_error_message,
            'snapshots_count': self.file_snapshots.count()
        }
    
    def __repr__(self):
        return f'<FolderMonitor {self.id}: {self.name}>'


class FileSnapshot(db.Model):
    """文件快照模型（用于增量检测）"""
    __tablename__ = 'file_snapshots'
    
    id = db.Column(db.Integer, primary_key=True)
    monitor_id = db.Column(db.Integer, db.ForeignKey('folder_monitors.id'), nullable=False, index=True)
    file_path = db.Column(db.Text, nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    modified_time = db.Column(db.DateTime, nullable=False)
    checksum = db.Column(db.String(255))
    status = db.Column(db.String(20), default='synced', nullable=False)  # synced, pending, downloading, failed
    last_sync_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('monitor_id', 'file_path', name='uq_monitor_file_path'),
    )
    
    def __init__(self, monitor_id, file_path, file_size, modified_time, checksum=None):
        self.monitor_id = monitor_id
        self.file_path = file_path
        self.file_size = file_size
        self.modified_time = modified_time
        self.checksum = checksum
    
    def mark_pending(self):
        """标记为待下载"""
        self.status = 'pending'
        db.session.commit()
    
    def mark_downloading(self):
        """标记为下载中"""
        self.status = 'downloading'
        db.session.commit()
    
    def mark_synced(self):
        """标记为已同步"""
        self.status = 'synced'
        self.last_sync_at = datetime.utcnow()
        db.session.commit()
    
    def mark_failed(self):
        """标记为失败"""
        self.status = 'failed'
        db.session.commit()
    
    def update_file_info(self, file_size, modified_time, checksum=None):
        """更新文件信息"""
        self.file_size = file_size
        self.modified_time = modified_time
        if checksum:
            self.checksum = checksum
        self.status = 'pending'  # 文件有变化，需要重新同步
        db.session.commit()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'monitor_id': self.monitor_id,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'modified_time': self.modified_time.isoformat() if self.modified_time else None,
            'checksum': self.checksum,
            'status': self.status,
            'last_sync_at': self.last_sync_at.isoformat() if self.last_sync_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<FileSnapshot {self.id}: {self.file_path}>'
