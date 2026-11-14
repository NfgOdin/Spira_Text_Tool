"""
core.task_worker - Thread-Safe Background Worker & Event Queue Subsystem.
Coordinates long-running operations off the main thread with progress reporting and cancellation.
"""

import threading
import queue
import time
from dataclasses import dataclass
from typing import Callable, Any, Optional

@dataclass
class TaskProgress:
    current: int
    total: int
    message: str
    stage: str = "running" # 'running', 'complete', 'cancelled', 'error'
    result: Any = None
    error: Optional[str] = None
    elapsed_sec: float = 0.0

class TaskWorker:
    def __init__(self, target_fn: Callable[['TaskWorker'], Any], name: str = "BackgroundTask"):
        self.target_fn = target_fn
        self.name = name
        self.queue: queue.Queue[TaskProgress] = queue.Queue()
        self._cancel_flag = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._start_time = 0.0

    def start(self):
        """Starts the worker thread."""
        self._cancel_flag.clear()
        self._start_time = time.time()
        self._thread = threading.Thread(target=self._run, name=self.name, daemon=True)
        self._thread.start()

    def cancel(self):
        """Signals the background task to cancel."""
        self._cancel_flag.set()

    def is_cancelled(self) -> bool:
        """Returns True if cancellation was requested."""
        return self._cancel_flag.is_set()

    def post_progress(self, current: int, total: int, message: str):
        """Called from inside the worker function to notify caller of progress."""
        elapsed = time.time() - self._start_time
        self.queue.put(TaskProgress(
            current=current,
            total=total,
            message=message,
            stage="running",
            elapsed_sec=round(elapsed, 1)
        ))

    def _run(self):
        try:
            res = self.target_fn(self)
            elapsed = time.time() - self._start_time
            if self.is_cancelled():
                self.queue.put(TaskProgress(current=100, total=100, message="Operation cancelled.", stage="cancelled", elapsed_sec=round(elapsed, 1)))
            else:
                self.queue.put(TaskProgress(current=100, total=100, message="Operation complete.", stage="complete", result=res, elapsed_sec=round(elapsed, 1)))
        except Exception as e:
            elapsed = time.time() - self._start_time
            self.queue.put(TaskProgress(current=0, total=100, message=f"Operation failed: {e}", stage="error", error=str(e), elapsed_sec=round(elapsed, 1)))
