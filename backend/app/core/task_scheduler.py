import asyncio
import time
import threading
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
from .priority_queue import PriorityTaskQueue, TaskItem, TaskPriority
from .resource_manager import ResourceManager, ResourceAllocation

class SchedulingPolicy(Enum):
    """调度策略枚举"""
    PRIORITY_PREEMPTIVE = "priority_preemptive"    # 抢占式优先级调度
    ROUND_ROBIN = "round_robin"                    # 时间片轮转
    FAIR_SHARE = "fair_share"                      # 公平共享
    ADAPTIVE = "adaptive"                          # 自适应调度

@dataclass
class TaskExecution:
    """任务执行状态"""
    task_item: TaskItem
    allocated_resources: ResourceAllocation
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    preempted_at: Optional[float] = None
    progress: float = 0.0
    status: str = "running"  # running, completed, failed, preempted
    error: Optional[str] = None
    is_preempted: bool = False

class TaskScheduler:
    """动态任务调度器"""
    
    def __init__(self, resource_manager: ResourceManager, task_queue: PriorityTaskQueue):
        self.resource_manager = resource_manager
        self.task_queue = task_queue
        self.running_tasks = {}  # task_id -> TaskExecution
        self.scheduling_policy = SchedulingPolicy.PRIORITY_PREEMPTIVE
        self.is_running = False
        self.scheduler_thread = None
        
        # 调度配置
        self.config = {
            "time_slice_seconds": 30,           # 时间片长度
            "preemption_enabled": True,         # 是否启用抢占
            "starvation_threshold": 300,        # 饥饿阈值（秒）
            "load_balance_interval": 60,        # 负载均衡间隔
            "max_preemptions_per_minute": 5,    # 每分钟最大抢占次数
            "scheduler_interval": 1             # 调度器运行间隔（秒）
        }
        
        # 统计信息
        self.stats = {
            "total_scheduled": 0,
            "total_completed": 0,
            "total_preempted": 0,
            "total_failed": 0,
            "average_wait_time": 0,
            "average_execution_time": 0,
            "last_schedule_time": None
        }
        
        # 饥饿检测
        self.starvation_tracker = {}  # task_id -> first_queued_time
        
        # 抢占限制
        self.preemption_history = []  # 记录最近的抢占时间
        
    def start(self):
        """启动调度器"""
        if not self.is_running:
            self.is_running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
    
    def stop(self):
        """停止调度器"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
    
    def _scheduler_loop(self):
        """调度器主循环"""
        while self.is_running:
            try:
                # 1. 检查并处理饥饿任务
                self._handle_starvation()
                
                # 2. 根据调度策略调度新任务
                if self.scheduling_policy == SchedulingPolicy.PRIORITY_PREEMPTIVE:
                    self._priority_preemptive_schedule()
                elif self.scheduling_policy == SchedulingPolicy.ROUND_ROBIN:
                    self._round_robin_schedule()
                elif self.scheduling_policy == SchedulingPolicy.FAIR_SHARE:
                    self._fair_share_schedule()
                elif self.scheduling_policy == SchedulingPolicy.ADAPTIVE:
                    self._adaptive_schedule()
                
                # 3. 检查任务完成情况
                self._check_completed_tasks()
                
                # 4. 清理过期的抢占记录
                self._cleanup_preemption_history()
                
                # 5. 更新统计信息
                self.stats["last_schedule_time"] = time.time()
                
                time.sleep(self.config["scheduler_interval"])
                
            except Exception as e:
                print(f"调度器错误: {e}")
                time.sleep(5)
    
    def _priority_preemptive_schedule(self):
        """抢占式优先级调度"""
        # 获取下一个高优先级任务
        next_task = self.task_queue.get([TaskPriority.CRITICAL, TaskPriority.HIGH])
        if not next_task:
            # 没有高优先级任务，尝试普通优先级
            next_task = self.task_queue.get([TaskPriority.NORMAL])
            if not next_task:
                # 没有普通优先级任务，尝试低优先级
                next_task = self.task_queue.get([TaskPriority.LOW, TaskPriority.BACKGROUND])
        
        if next_task:
            # 检查是否需要抢占
            if (next_task.priority <= TaskPriority.HIGH and 
                self.config["preemption_enabled"] and 
                self._can_preempt()):
                self._try_preemption(next_task)
            else:
                self._try_start_task(next_task)
    
    def _try_preemption(self, high_priority_task: TaskItem):
        """尝试抢占低优先级任务"""
        # 查找可以被抢占的任务
        preemptable_tasks = [
            (task_id, execution) for task_id, execution in self.running_tasks.items()
            if execution.task_item.priority > high_priority_task.priority
        ]
        
        if preemptable_tasks:
            # 选择优先级最低的任务进行抢占
            task_to_preempt = max(preemptable_tasks, key=lambda x: x[1].task_item.priority)
            task_id, execution = task_to_preempt
            
            # 执行抢占
            self._preempt_task(task_id)
            
            # 启动高优先级任务
            self._try_start_task(high_priority_task)
            
            self.stats["total_preempted"] += 1
            self._record_preemption()
    
    def _try_start_task(self, task_item: TaskItem):
        """尝试启动任务"""
        # 计算所需资源
        required_resources = self._calculate_required_resources(task_item)
        
        # 检查资源是否可用
        if self.resource_manager.can_allocate_resources(task_item.priority, required_resources):
            # 分配资源并启动任务
            if self.resource_manager.allocate_resources(
                task_item.task_id, task_item.priority, required_resources
            ):
                execution = TaskExecution(task_item, required_resources)
                execution.started_at = time.time()
                self.running_tasks[task_item.task_id] = execution
                
                # 启动任务执行（这里应该调用实际的任务执行函数）
                self._start_task_execution(execution)
                
                self.stats["total_scheduled"] += 1
                
                # 移除饥饿追踪
                if task_item.task_id in self.starvation_tracker:
                    del self.starvation_tracker[task_item.task_id]
        else:
            # 资源不足，重新放回队列
            self.task_queue.put(task_item)
            
            # 添加到饥饿追踪
            if task_item.task_id not in self.starvation_tracker:
                self.starvation_tracker[task_item.task_id] = time.time()
    
    def _handle_starvation(self):
        """处理饥饿任务"""
        current_time = time.time()
        starved_tasks = []
        
        for task_id, queued_time in self.starvation_tracker.items():
            if current_time - queued_time > self.config["starvation_threshold"]:
                starved_tasks.append(task_id)
        
        # 为饥饿任务临时提升优先级
        for task_id in starved_tasks:
            if self.task_queue.update_priority(task_id, TaskPriority.HIGH):
                print(f"任务 {task_id} 因饥饿被提升为高优先级")
    
    def _preempt_task(self, task_id: str):
        """抢占任务"""
        if task_id in self.running_tasks:
            execution = self.running_tasks[task_id]
            
            # 暂停任务
            execution.is_preempted = True
            execution.preempted_at = time.time()
            execution.status = "preempted"
            
            # 释放资源
            self.resource_manager.release_resources(
                task_id, execution.task_item.priority, execution.allocated_resources
            )
            
            # 将任务重新放回队列
            self.task_queue.put(execution.task_item)
            
            # 从运行任务中移除
            del self.running_tasks[task_id]
            
            print(f"任务 {task_id} 被抢占")
    
    def _calculate_required_resources(self, task_item: TaskItem) -> ResourceAllocation:
        """计算任务所需资源"""
        # 根据任务类型和优先级计算资源需求
        base_resources = ResourceAllocation(
            priority=task_item.priority,
            ftp_connections=1,
            bandwidth_kbps=1024,  # 1MB/s
            concurrent_tasks=1,
            disk_io_mbps=10,
            memory_mb=64
        )
        
        # 根据优先级调整资源分配
        if task_item.priority == TaskPriority.CRITICAL:
            base_resources.ftp_connections = 2
            base_resources.bandwidth_kbps = 2048
            base_resources.memory_mb = 128
        elif task_item.priority == TaskPriority.BACKGROUND:
            base_resources.bandwidth_kbps = 256
            base_resources.memory_mb = 32
        
        # 考虑任务的资源需求
        if task_item.resource_requirements:
            for key, value in task_item.resource_requirements.items():
                if hasattr(base_resources, key):
                    setattr(base_resources, key, value)
        
        return base_resources
    
    def _start_task_execution(self, execution: TaskExecution):
        """启动任务执行"""
        # 这里应该调用实际的任务执行逻辑
        # 例如：启动Celery任务或直接执行
        pass
    
    def _check_completed_tasks(self):
        """检查已完成的任务"""
        completed_tasks = []
        for task_id, execution in self.running_tasks.items():
            if execution.status in ['completed', 'failed']:
                completed_tasks.append(task_id)
        
        for task_id in completed_tasks:
            execution = self.running_tasks[task_id]
            self.resource_manager.release_resources(
                task_id, execution.task_item.priority, execution.allocated_resources
            )
            del self.running_tasks[task_id]
            
            if execution.status == 'completed':
                self.stats["total_completed"] += 1
            else:
                self.stats["total_failed"] += 1
    
    def _can_preempt(self) -> bool:
        """检查是否可以执行抢占"""
        current_time = time.time()
        # 清理一分钟前的抢占记录
        self.preemption_history = [
            t for t in self.preemption_history 
            if current_time - t < 60
        ]
        
        return len(self.preemption_history) < self.config["max_preemptions_per_minute"]
    
    def _record_preemption(self):
        """记录抢占操作"""
        self.preemption_history.append(time.time())
    
    def _cleanup_preemption_history(self):
        """清理过期的抢占记录"""
        current_time = time.time()
        self.preemption_history = [
            t for t in self.preemption_history 
            if current_time - t < 60
        ]
    
    def _round_robin_schedule(self):
        """时间片轮转调度"""
        # 简化实现，实际应该更复杂
        next_task = self.task_queue.get()
        if next_task:
            self._try_start_task(next_task)
    
    def _fair_share_schedule(self):
        """公平共享调度"""
        # 简化实现
        next_task = self.task_queue.get()
        if next_task:
            self._try_start_task(next_task)
    
    def _adaptive_schedule(self):
        """自适应调度"""
        # 根据系统负载动态调整调度策略
        total_usage = self.resource_manager.get_total_usage()
        cpu_usage = total_usage["usage_percentage"]["concurrent_tasks"]
        
        if cpu_usage > 80:
            # 高负载时使用抢占式调度
            self._priority_preemptive_schedule()
        else:
            # 低负载时使用公平调度
            self._fair_share_schedule()
    
    def add_task(self, task_item: TaskItem):
        """添加任务到调度队列"""
        self.task_queue.put(task_item)
    
    def remove_task(self, task_id: str) -> bool:
        """移除任务"""
        # 先尝试从队列中移除
        if self.task_queue.remove(task_id):
            return True
        
        # 如果任务正在运行，则停止它
        if task_id in self.running_tasks:
            execution = self.running_tasks[task_id]
            execution.status = "cancelled"
            self.resource_manager.release_resources(
                task_id, execution.task_item.priority, execution.allocated_resources
            )
            del self.running_tasks[task_id]
            return True
        
        return False
    
    def get_scheduler_status(self) -> Dict:
        """获取调度器状态"""
        return {
            "is_running": self.is_running,
            "scheduling_policy": self.scheduling_policy.value,
            "config": self.config,
            "stats": self.stats,
            "queue_status": self.task_queue.get_queue_status(),
            "running_tasks_count": len(self.running_tasks),
            "starvation_tasks_count": len(self.starvation_tracker),
            "recent_preemptions": len(self.preemption_history)
        }
