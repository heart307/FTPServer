from datetime import datetime
from app import db
import json

class TransferTask(db.Model):
    """传输任务模型"""
    __tablename__ = 'transfer_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    site_id = db.Column(db.Integer, db.ForeignKey('ftp_sites.id'), nullable=False, index=True)
    task_type = db.Column(db.String(20), nullable=False)  # upload, download, sync, folder_download
    task_mode = db.Column(db.String(20), default='file')  # file, folder, folder_compressed
    status = db.Column(db.String(20), default='pending', nullable=False, index=True)  # pending, running, completed, failed, cancelled, paused
    priority = db.Column(db.Integer, default=3, nullable=False, index=True)  # 1-5优先级
    
    # 路径信息
    local_path = db.Column(db.Text, nullable=False)
    remote_path = db.Column(db.Text, nullable=False)
    
    # 进度信息
    file_count = db.Column(db.Integer, default=0)
    total_size = db.Column(db.BigInteger, default=0)
    transferred_size = db.Column(db.BigInteger, default=0)
    progress = db.Column(db.Float, default=0.0)
    speed = db.Column(db.Float, default=0.0)  # KB/s
    
    # 配置信息
    compression_type = db.Column(db.String(10))  # zip, tar.gz, none
    preserve_structure = db.Column(db.Boolean, default=True)
    checksum_type = db.Column(db.String(10), default='md5')
    max_connections = db.Column(db.Integer, default=2)
    bandwidth_limit = db.Column(db.Integer)  # KB/s，0表示无限制
    
    # 重试信息
    retry_count = db.Column(db.Integer, default=0)
    max_retries = db.Column(db.Integer, default=3)
    pause_on_error = db.Column(db.Boolean, default=False)
    
    # 时间信息
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # 错误信息
    error_message = db.Column(db.Text)
    
    # 额外配置（JSON格式）
    extra_config = db.Column(db.Text)
    
    # 关系
    task_files = db.relationship('TaskFile', backref='transfer_task', lazy='dynamic', cascade='all, delete-orphan')
    operation_logs = db.relationship('OperationLog', backref='transfer_task', lazy='dynamic')
    
    def __init__(self, user_id, site_id, task_type, local_path, remote_path, **kwargs):
        self.user_id = user_id
        self.site_id = site_id
        self.task_type = task_type
        self.local_path = local_path
        self.remote_path = remote_path
        
        # 设置可选参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_extra_config(self, config_dict):
        """设置额外配置"""
        self.extra_config = json.dumps(config_dict) if config_dict else None
    
    def get_extra_config(self):
        """获取额外配置"""
        return json.loads(self.extra_config) if self.extra_config else {}
    
    def update_progress(self, transferred_size=None, speed=None):
        """更新进度"""
        if transferred_size is not None:
            self.transferred_size = transferred_size
            if self.total_size > 0:
                self.progress = min(self.transferred_size / self.total_size, 1.0)
        
        if speed is not None:
            self.speed = speed
        
        db.session.commit()
    
    def start_task(self):
        """开始任务"""
        self.status = 'running'
        self.started_at = datetime.utcnow()
        db.session.commit()
    
    def complete_task(self):
        """完成任务"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        self.progress = 1.0
        db.session.commit()
    
    def fail_task(self, error_message):
        """任务失败"""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = datetime.utcnow()
        db.session.commit()
    
    def pause_task(self):
        """暂停任务"""
        self.status = 'paused'
        db.session.commit()
    
    def resume_task(self):
        """恢复任务"""
        self.status = 'pending'
        db.session.commit()
    
    def cancel_task(self):
        """取消任务"""
        self.status = 'cancelled'
        self.completed_at = datetime.utcnow()
        db.session.commit()
    
    def increment_retry(self):
        """增加重试次数"""
        self.retry_count += 1
        db.session.commit()
        return self.retry_count <= self.max_retries
    
    @property
    def estimated_time_remaining(self):
        """估算剩余时间（秒）"""
        if self.speed > 0 and self.total_size > 0:
            remaining_size = self.total_size - self.transferred_size
            return remaining_size / (self.speed * 1024)  # 转换为秒
        return None
    
    @property
    def duration(self):
        """任务持续时间（秒）"""
        if self.started_at:
            end_time = self.completed_at or datetime.utcnow()
            return (end_time - self.started_at).total_seconds()
        return None
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'site_id': self.site_id,
            'task_type': self.task_type,
            'task_mode': self.task_mode,
            'status': self.status,
            'priority': self.priority,
            'local_path': self.local_path,
            'remote_path': self.remote_path,
            'file_count': self.file_count,
            'total_size': self.total_size,
            'transferred_size': self.transferred_size,
            'progress': self.progress,
            'speed': self.speed,
            'compression_type': self.compression_type,
            'preserve_structure': self.preserve_structure,
            'checksum_type': self.checksum_type,
            'max_connections': self.max_connections,
            'bandwidth_limit': self.bandwidth_limit,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'pause_on_error': self.pause_on_error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'extra_config': self.get_extra_config(),
            'estimated_time_remaining': self.estimated_time_remaining,
            'duration': self.duration,
            'files_count': self.task_files.count()
        }
    
    def __repr__(self):
        return f'<TransferTask {self.id}: {self.task_type} {self.status}>'


class TaskFile(db.Model):
    """任务文件详情模型"""
    __tablename__ = 'task_files'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('transfer_tasks.id'), nullable=False, index=True)
    file_path = db.Column(db.Text, nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, downloading, completed, failed
    transferred_size = db.Column(db.BigInteger, default=0)
    checksum = db.Column(db.String(255))
    error_message = db.Column(db.Text)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    # 关系
    transfer_chunks = db.relationship('TransferChunk', backref='task_file', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, task_id, file_path, file_size):
        self.task_id = task_id
        self.file_path = file_path
        self.file_size = file_size

    @property
    def progress(self):
        """文件传输进度"""
        if self.file_size > 0:
            return min(self.transferred_size / self.file_size, 1.0)
        return 0.0

    def update_progress(self, transferred_size):
        """更新文件传输进度"""
        self.transferred_size = transferred_size
        if self.transferred_size >= self.file_size:
            self.status = 'completed'
            self.completed_at = datetime.utcnow()
        db.session.commit()

    def start_transfer(self):
        """开始文件传输"""
        self.status = 'downloading'
        self.started_at = datetime.utcnow()
        db.session.commit()

    def fail_transfer(self, error_message):
        """文件传输失败"""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = datetime.utcnow()
        db.session.commit()

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'status': self.status,
            'transferred_size': self.transferred_size,
            'progress': self.progress,
            'checksum': self.checksum,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'chunks_count': self.transfer_chunks.count()
        }

    def __repr__(self):
        return f'<TaskFile {self.id}: {self.file_path}>'


class TransferChunk(db.Model):
    """传输块记录模型（用于断点续传）"""
    __tablename__ = 'transfer_chunks'

    id = db.Column(db.Integer, primary_key=True)
    task_file_id = db.Column(db.Integer, db.ForeignKey('task_files.id'), nullable=False, index=True)
    chunk_index = db.Column(db.Integer, nullable=False)
    start_offset = db.Column(db.BigInteger, nullable=False)
    end_offset = db.Column(db.BigInteger, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, downloading, completed, failed
    checksum = db.Column(db.String(255))
    retry_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime)

    __table_args__ = (
        db.UniqueConstraint('task_file_id', 'chunk_index', name='uq_task_file_chunk'),
    )

    def __init__(self, task_file_id, chunk_index, start_offset, end_offset):
        self.task_file_id = task_file_id
        self.chunk_index = chunk_index
        self.start_offset = start_offset
        self.end_offset = end_offset

    @property
    def size(self):
        """块大小"""
        return self.end_offset - self.start_offset

    def complete_chunk(self, checksum=None):
        """完成块传输"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        if checksum:
            self.checksum = checksum
        db.session.commit()

    def fail_chunk(self):
        """块传输失败"""
        self.status = 'failed'
        self.retry_count += 1
        db.session.commit()

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'task_file_id': self.task_file_id,
            'chunk_index': self.chunk_index,
            'start_offset': self.start_offset,
            'end_offset': self.end_offset,
            'size': self.size,
            'status': self.status,
            'checksum': self.checksum,
            'retry_count': self.retry_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

    def __repr__(self):
        return f'<TransferChunk {self.id}: {self.chunk_index}>'
