import threading
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict
from .priority_queue import TaskPriority

@dataclass
class SystemResources:
    """系统资源定义"""
    max_ftp_connections: int = 20      # 最大FTP连接数
    max_bandwidth_kbps: int = 10240    # 最大带宽 KB/s (10MB/s)
    max_concurrent_tasks: int = 10     # 最大并发任务数
    max_disk_io_mbps: int = 100        # 最大磁盘I/O MB/s
    max_memory_mb: int = 1024          # 最大内存使用 MB

@dataclass 
class ResourceAllocation:
    """资源分配配置"""
    priority: int
    ftp_connections: int = 0
    bandwidth_kbps: int = 0
    concurrent_tasks: int = 0
    disk_io_mbps: int = 0
    memory_mb: int = 0
    
    def to_dict(self):
        return {
            "ftp_connections": self.ftp_connections,
            "bandwidth_kbps": self.bandwidth_kbps,
            "concurrent_tasks": self.concurrent_tasks,
            "disk_io_mbps": self.disk_io_mbps,
            "memory_mb": self.memory_mb
        }

class ResourceManager:
    """系统资源管理器"""
    
    def __init__(self, system_resources: SystemResources = None):
        self.system_resources = system_resources or SystemResources()
        self.lock = threading.RLock()
        
        # 资源分配策略配置
        self.allocation_strategy = {
            TaskPriority.CRITICAL: {
                "ftp_connections_percent": 40,    # 40%的连接
                "bandwidth_percent": 50,          # 50%的带宽
                "concurrent_tasks_percent": 50,   # 50%的并发任务
                "disk_io_percent": 40,           # 40%的磁盘I/O
                "memory_percent": 40             # 40%的内存
            },
            TaskPriority.HIGH: {
                "ftp_connections_percent": 30,
                "bandwidth_percent": 30,
                "concurrent_tasks_percent": 30,
                "disk_io_percent": 30,
                "memory_percent": 30
            },
            TaskPriority.NORMAL: {
                "ftp_connections_percent": 20,
                "bandwidth_percent": 15,
                "concurrent_tasks_percent": 15,
                "disk_io_percent": 20,
                "memory_percent": 20
            },
            TaskPriority.LOW: {
                "ftp_connections_percent": 8,
                "bandwidth_percent": 4,
                "concurrent_tasks_percent": 4,
                "disk_io_percent": 8,
                "memory_percent": 8
            },
            TaskPriority.BACKGROUND: {
                "ftp_connections_percent": 2,
                "bandwidth_percent": 1,
                "concurrent_tasks_percent": 1,
                "disk_io_percent": 2,
                "memory_percent": 2
            }
        }
        
        # 当前资源使用情况
        self.current_usage = {
            priority: ResourceAllocation(priority) 
            for priority in [1, 2, 3, 4, 5]
        }
        
        # 活跃任务追踪
        self.active_tasks = defaultdict(list)  # priority -> [task_ids]
        self.task_allocations = {}  # task_id -> ResourceAllocation
        
    def calculate_max_allocation(self, priority: int) -> ResourceAllocation:
        """计算指定优先级的最大资源分配"""
        strategy = self.allocation_strategy[priority]
        
        return ResourceAllocation(
            priority=priority,
            ftp_connections=int(self.system_resources.max_ftp_connections * 
                              strategy["ftp_connections_percent"] / 100),
            bandwidth_kbps=int(self.system_resources.max_bandwidth_kbps * 
                             strategy["bandwidth_percent"] / 100),
            concurrent_tasks=int(self.system_resources.max_concurrent_tasks * 
                               strategy["concurrent_tasks_percent"] / 100),
            disk_io_mbps=int(self.system_resources.max_disk_io_mbps * 
                           strategy["disk_io_percent"] / 100),
            memory_mb=int(self.system_resources.max_memory_mb * 
                        strategy["memory_percent"] / 100)
        )
    
    def can_allocate_resources(self, priority: int, required: ResourceAllocation) -> bool:
        """检查是否可以分配指定资源"""
        with self.lock:
            max_allocation = self.calculate_max_allocation(priority)
            current = self.current_usage[priority]
            
            return (
                current.ftp_connections + required.ftp_connections <= max_allocation.ftp_connections and
                current.bandwidth_kbps + required.bandwidth_kbps <= max_allocation.bandwidth_kbps and
                current.concurrent_tasks + required.concurrent_tasks <= max_allocation.concurrent_tasks and
                current.disk_io_mbps + required.disk_io_mbps <= max_allocation.disk_io_mbps and
                current.memory_mb + required.memory_mb <= max_allocation.memory_mb
            )
    
    def allocate_resources(self, task_id: str, priority: int, required: ResourceAllocation) -> bool:
        """分配资源给任务"""
        with self.lock:
            if not self.can_allocate_resources(priority, required):
                return False
            
            # 分配资源
            current = self.current_usage[priority]
            current.ftp_connections += required.ftp_connections
            current.bandwidth_kbps += required.bandwidth_kbps
            current.concurrent_tasks += required.concurrent_tasks
            current.disk_io_mbps += required.disk_io_mbps
            current.memory_mb += required.memory_mb
            
            # 记录任务分配
            self.active_tasks[priority].append(task_id)
            self.task_allocations[task_id] = required
            return True
    
    def release_resources(self, task_id: str, priority: int, allocated: ResourceAllocation = None):
        """释放任务资源"""
        with self.lock:
            # 如果没有提供分配信息，从记录中获取
            if allocated is None:
                allocated = self.task_allocations.get(task_id)
                if allocated is None:
                    return  # 没有找到分配记录
            
            current = self.current_usage[priority]
            current.ftp_connections = max(0, current.ftp_connections - allocated.ftp_connections)
            current.bandwidth_kbps = max(0, current.bandwidth_kbps - allocated.bandwidth_kbps)
            current.concurrent_tasks = max(0, current.concurrent_tasks - allocated.concurrent_tasks)
            current.disk_io_mbps = max(0, current.disk_io_mbps - allocated.disk_io_mbps)
            current.memory_mb = max(0, current.memory_mb - allocated.memory_mb)
            
            # 移除任务记录
            if task_id in self.active_tasks[priority]:
                self.active_tasks[priority].remove(task_id)
            if task_id in self.task_allocations:
                del self.task_allocations[task_id]
    
    def get_available_resources(self, priority: int) -> ResourceAllocation:
        """获取指定优先级的可用资源"""
        with self.lock:
            max_allocation = self.calculate_max_allocation(priority)
            current = self.current_usage[priority]
            
            return ResourceAllocation(
                priority=priority,
                ftp_connections=max_allocation.ftp_connections - current.ftp_connections,
                bandwidth_kbps=max_allocation.bandwidth_kbps - current.bandwidth_kbps,
                concurrent_tasks=max_allocation.concurrent_tasks - current.concurrent_tasks,
                disk_io_mbps=max_allocation.disk_io_mbps - current.disk_io_mbps,
                memory_mb=max_allocation.memory_mb - current.memory_mb
            )
    
    def get_resource_status(self) -> Dict:
        """获取资源使用状态"""
        with self.lock:
            status = {}
            for priority in [1, 2, 3, 4, 5]:
                max_alloc = self.calculate_max_allocation(priority)
                current = self.current_usage[priority]
                
                status[priority] = {
                    "priority_name": TaskPriority.get_priority_name(priority),
                    "max_allocation": max_alloc.to_dict(),
                    "current_usage": current.to_dict(),
                    "usage_percentage": {
                        "ftp_connections": (current.ftp_connections / max(max_alloc.ftp_connections, 1)) * 100,
                        "bandwidth": (current.bandwidth_kbps / max(max_alloc.bandwidth_kbps, 1)) * 100,
                        "concurrent_tasks": (current.concurrent_tasks / max(max_alloc.concurrent_tasks, 1)) * 100,
                        "disk_io": (current.disk_io_mbps / max(max_alloc.disk_io_mbps, 1)) * 100,
                        "memory": (current.memory_mb / max(max_alloc.memory_mb, 1)) * 100
                    },
                    "active_tasks": len(self.active_tasks[priority]),
                    "available_resources": self.get_available_resources(priority).to_dict()
                }
            
            return status
    
    def update_allocation_strategy(self, new_strategy: Dict):
        """更新资源分配策略"""
        with self.lock:
            self.allocation_strategy.update(new_strategy)
    
    def update_system_resources(self, new_resources: SystemResources):
        """更新系统资源配置"""
        with self.lock:
            self.system_resources = new_resources
    
    def get_task_allocation(self, task_id: str) -> ResourceAllocation:
        """获取任务的资源分配"""
        with self.lock:
            return self.task_allocations.get(task_id)
    
    def get_total_usage(self) -> Dict:
        """获取总体资源使用情况"""
        with self.lock:
            total_usage = ResourceAllocation(0)
            for priority_usage in self.current_usage.values():
                total_usage.ftp_connections += priority_usage.ftp_connections
                total_usage.bandwidth_kbps += priority_usage.bandwidth_kbps
                total_usage.concurrent_tasks += priority_usage.concurrent_tasks
                total_usage.disk_io_mbps += priority_usage.disk_io_mbps
                total_usage.memory_mb += priority_usage.memory_mb
            
            return {
                "total_usage": total_usage.to_dict(),
                "system_resources": {
                    "max_ftp_connections": self.system_resources.max_ftp_connections,
                    "max_bandwidth_kbps": self.system_resources.max_bandwidth_kbps,
                    "max_concurrent_tasks": self.system_resources.max_concurrent_tasks,
                    "max_disk_io_mbps": self.system_resources.max_disk_io_mbps,
                    "max_memory_mb": self.system_resources.max_memory_mb
                },
                "usage_percentage": {
                    "ftp_connections": (total_usage.ftp_connections / max(self.system_resources.max_ftp_connections, 1)) * 100,
                    "bandwidth": (total_usage.bandwidth_kbps / max(self.system_resources.max_bandwidth_kbps, 1)) * 100,
                    "concurrent_tasks": (total_usage.concurrent_tasks / max(self.system_resources.max_concurrent_tasks, 1)) * 100,
                    "disk_io": (total_usage.disk_io_mbps / max(self.system_resources.max_disk_io_mbps, 1)) * 100,
                    "memory": (total_usage.memory_mb / max(self.system_resources.max_memory_mb, 1)) * 100
                }
            }
