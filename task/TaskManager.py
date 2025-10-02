import threading
import queue
from typing import Callable, Union
from concurrent.futures import ThreadPoolExecutor, Future


class TaskManager:
    """同步任务并行执行器（使用线程池）"""

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
        self._shutdown_event = threading.Event()  # 关闭事件
        self._executor = None  # 线程池执行器
        self._max_workers = 2  # 最大线程数
        self._worker_thread = None  # 任务分发线程

    async def add_task(self, func: Callable, *args, **kwargs) -> Union[int, str]:
        """
        异步添加同步任务到队列
        :return: 成功时返回当前队列大小，队列满时返回错误信息
        """
        # 检查队列是否已满
        if self._task_queue.full():
            return "队列已满，无法添加新任务"

        # 检查是否已关闭
        if self._shutdown_event.is_set():
            return "执行器已关闭，无法添加新任务"

        # 将任务添加到队列
        self._task_queue.put((func, args, kwargs))

        # 按需启动工作线程
        self._start_worker()

        return self._task_queue.qsize()

    def _start_worker(self):
        """按需启动任务分发线程"""
        if (self._worker_thread is None or
                not self._worker_thread.is_alive() or
                self._worker_thread == threading.current_thread()):

            self._shutdown_event.clear()

            # 创建线程池（如果尚未创建）
            if self._executor is None:
                self._executor = ThreadPoolExecutor(
                    max_workers=self._max_workers,
                    thread_name_prefix="TaskWorker"
                )

            # 启动任务分发线程
            self._worker_thread = threading.Thread(
                target=self._task_dispatcher,
                daemon=True,
                name="TaskDispatcher"
            )
            self._worker_thread.start()

    def _task_dispatcher(self):
        """任务分发器（从队列取任务并提交到线程池）"""
        while not self._shutdown_event.is_set() or not self._task_queue.empty():
            try:
                # 带超时的获取，避免永久阻塞
                task_item = self._task_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            # 检查关闭信号
            if task_item == (None, None, None):
                self._task_queue.task_done()
                break

            func, args, kwargs = task_item

            # 提交任务到线程池
            future = self._executor.submit(self._execute_task, func, args, kwargs)
            # 添加回调处理异常
            future.add_done_callback(self._handle_task_result)

    def _execute_task(self, func: Callable, args: tuple, kwargs: dict):
        """实际执行任务的包装函数"""
        try:
            func(*args, **kwargs)
        except Exception as e:
            return e
        return None

    def _handle_task_result(self, future: Future):
        """处理任务完成结果"""
        self._task_queue.task_done()
        exception = future.exception()
        if exception:
            self._handle_task_error(exception)

    def shutdown(self, wait: bool = True):
        """关闭执行器"""
        self._shutdown_event.set()

        # 放入空任务唤醒分发线程
        if not self._task_queue.empty():
            self._task_queue.put((None, None, None))

        # 等待分发线程退出
        if wait and self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=5.0)

        # 关闭线程池
        if self._executor:
            self._executor.shutdown(wait=wait)

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