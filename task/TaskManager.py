import threading
import queue
from typing import Callable


class TaskManager:
    """同步任务串行执行器（空闲时零资源占用）"""

    # 单例模式确保全局唯一执行器
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """初始化执行器状态"""
        max_qsize = 1000
        self._task_queue = queue.Queue(maxsize=max_qsize)  # 同步任务队列
        self._worker_thread = None  # 工作线程
        self._shutdown_event = threading.Event()  # 关闭事件

    async def add_task(self, func: Callable, *args, **kwargs) -> int:
        """
        异步添加同步任务到队列
        :return: 当前队列大小
        """
        # 将任务添加到队列
        self._task_queue.put((func, args, kwargs))

        # 按需启动工作线程
        self._start_worker()

        return self._task_queue.qsize()

    def _start_worker(self):
        """按需启动工作线程"""
        if (self._worker_thread is None or
                not self._worker_thread.is_alive() or
                self._worker_thread == threading.current_thread()):
            self._shutdown_event.clear()
            self._worker_thread = threading.Thread(
                target=self._task_processor,
                daemon=True
            )
            self._worker_thread.start()

    def _task_processor(self):
        """任务处理器（优化空闲资源）"""
        while True:
            # 获取任务（无限期等待）
            task_item = self._task_queue.get()

            # 检查关闭信号（None 是关闭标记）
            if task_item == (None, None, None) or self._shutdown_event.is_set():
                self._task_queue.task_done()
                break

            func, args, kwargs = task_item

            try:
                # 直接执行任务
                func(*args, **kwargs)
            except Exception as e:
                self._handle_task_error(e)
            finally:
                self._task_queue.task_done()

            # 检查是否需要退出
            if self._shutdown_event.is_set():
                break

    def shutdown(self, wait: bool = True):
        """关闭执行器"""
        self._shutdown_event.set()

        # 放入空任务唤醒工作线程
        if not self._task_queue.empty():
            self._task_queue.put((None, None, None))

        # 等待工作线程退出
        if wait and self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=5.0)

    def _handle_task_error(self, error: Exception):
        """处理任务错误"""
        # 错误处理逻辑
        print(f"任务执行失败: {str(error)}")

    @property
    def queue_size(self) -> int:
        """获取当前队列大小"""
        return self._task_queue.qsize()

    @property
    def is_worker_alive(self) -> bool:
        """工作线程是否运行中"""
        return self._worker_thread and self._worker_thread.is_alive()