import heapq
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import IntEnum

class TaskPriority(IntEnum):
    """任务优先级枚举"""
    CRITICAL = 1    # 关键任务 - 不间断执行，最高资源分配
    HIGH = 2        # 高优先级 - 优先调度，高资源分配  
    NORMAL = 3      # 普通优先级 - 正常调度，标准资源分配
    LOW = 4         # 低优先级 - 可被抢占，低资源分配
    BACKGROUND = 5  # 后台任务 - 空闲时执行，最低资源分配

    @classmethod
    def get_priority_name(cls, priority):
        names = {1: "关键", 2: "高", 3: "普通", 4: "低", 5: "后台"}
        return names.get(priority, "未知")
    
    @classmethod
    def get_priority_color(cls, priority):
        colors = {1: "red", 2: "orange", 3: "blue", 4: "green", 5: "gray"}
        return colors.get(priority, "default")

@dataclass
class TaskItem:
    """任务项数据结构"""
    task_id: str
    priority: int
    created_at: float = field(default_factory=time.time)
    estimated_duration: int = 0  # 预估执行时间（秒）
    resource_requirements: Dict = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    
    def __lt__(self, other):
        # 优先级数字越小，优先级越高
        if self.priority != other.priority:
            return self.priority < other.priority
        # 同优先级按创建时间排序（FIFO）
        return self.created_at < other.created_at

class PriorityTaskQueue:
    """多级优先级任务队列"""
    
    def __init__(self):
        self.queues = {
            TaskPriority.CRITICAL: [],
            TaskPriority.HIGH: [],
            TaskPriority.NORMAL: [],
            TaskPriority.LOW: [],
            TaskPriority.BACKGROUND: []
        }
        self.lock = threading.RLock()
        self.task_index = {}  # task_id -> TaskItem 映射
        self.queue_stats = defaultdict(int)  # 队列统计信息
        
    def put(self, task_item: TaskItem):
        """添加任务到队列"""
        with self.lock:
            heapq.heappush(self.queues[task_item.priority], task_item)
            self.task_index[task_item.task_id] = task_item
            self.queue_stats[task_item.priority] += 1
            
    def get(self, priority_filter: List[int] = None) -> Optional[TaskItem]:
        """从队列中获取任务"""
        with self.lock:
            # 如果指定了优先级过滤器，只从这些队列中获取
            priorities = priority_filter or [1, 2, 3, 4, 5]
            
            for priority in priorities:
                if self.queues[priority]:
                    task_item = heapq.heappop(self.queues[priority])
                    # 检查是否是已删除的任务
                    if task_item.task_id.startswith("DELETED_"):
                        continue
                    
                    if task_item.task_id in self.task_index:
                        del self.task_index[task_item.task_id]
                        self.queue_stats[priority] -= 1
                        return task_item
            return None
    
    def remove(self, task_id: str) -> bool:
        """从队列中移除指定任务"""
        with self.lock:
            if task_id not in self.task_index:
                return False
                
            task_item = self.task_index[task_id]
            
            # 标记为已删除（延迟删除）
            task_item.task_id = f"DELETED_{task_id}"
            del self.task_index[task_id]
            self.queue_stats[task_item.priority] -= 1
            return True
    
    def update_priority(self, task_id: str, new_priority: int) -> bool:
        """更新任务优先级"""
        with self.lock:
            if task_id not in self.task_index:
                return False
                
            # 移除旧任务
            old_task = self.task_index[task_id]
            old_priority = old_task.priority
            self.remove(task_id)
            
            # 添加新优先级任务
            old_task.priority = new_priority
            old_task.task_id = task_id  # 恢复原始ID
            self.put(old_task)
            return True
    
    def peek(self, priority: int = None) -> Optional[TaskItem]:
        """查看队列顶部任务但不移除"""
        with self.lock:
            if priority is not None:
                if self.queues[priority]:
                    return self.queues[priority][0]
            else:
                for p in [1, 2, 3, 4, 5]:
                    if self.queues[p]:
                        return self.queues[p][0]
            return None
    
    def size(self, priority: int = None) -> int:
        """获取队列大小"""
        with self.lock:
            if priority is not None:
                return self.queue_stats[priority]
            return sum(self.queue_stats.values())
    
    def is_empty(self, priority: int = None) -> bool:
        """检查队列是否为空"""
        return self.size(priority) == 0
    
    def get_queue_status(self) -> Dict:
        """获取队列状态"""
        with self.lock:
            total_tasks = sum(self.queue_stats.values())
            return {
                "queue_lengths": dict(self.queue_stats),
                "total_tasks": total_tasks,
                "priority_distribution": {
                    priority: {
                        "count": count,
                        "percentage": count / max(total_tasks, 1) * 100
                    }
                    for priority, count in self.queue_stats.items()
                }
            }
    
    def get_waiting_tasks(self, priority: int = None) -> List[TaskItem]:
        """获取等待中的任务列表"""
        with self.lock:
            if priority is not None:
                return [task for task in self.queues[priority] 
                       if not task.task_id.startswith("DELETED_")]
            
            all_tasks = []
            for p in [1, 2, 3, 4, 5]:
                all_tasks.extend([task for task in self.queues[p] 
                                if not task.task_id.startswith("DELETED_")])
            return sorted(all_tasks)
    
    def clear(self, priority: int = None):
        """清空队列"""
        with self.lock:
            if priority is not None:
                self.queues[priority].clear()
                self.queue_stats[priority] = 0
                # 清理task_index中对应的任务
                to_remove = [task_id for task_id, task in self.task_index.items() 
                           if task.priority == priority]
                for task_id in to_remove:
                    del self.task_index[task_id]
            else:
                for p in [1, 2, 3, 4, 5]:
                    self.queues[p].clear()
                    self.queue_stats[p] = 0
                self.task_index.clear()
    
    def cleanup_deleted_tasks(self):
        """清理已标记删除的任务"""
        with self.lock:
            for priority in [1, 2, 3, 4, 5]:
                # 重建队列，过滤掉已删除的任务
                valid_tasks = [task for task in self.queues[priority] 
                             if not task.task_id.startswith("DELETED_")]
                self.queues[priority] = valid_tasks
                heapq.heapify(self.queues[priority])
                self.queue_stats[priority] = len(valid_tasks)
    
    def __len__(self):
        return self.size()
    
    def __bool__(self):
        return not self.is_empty()
