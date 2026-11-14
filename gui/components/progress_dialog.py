"""
gui.components.progress_dialog - Modal/Floating Background Task Progress Dialog.
Displays thread progress, elapsed time, status message, and Cancel button.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from core.task_worker import TaskWorker, TaskProgress

class TaskProgressDialog:
    def __init__(self, parent, title: str, worker: TaskWorker, on_complete: Optional[Callable[[TaskProgress], None]] = None):
        self.parent = parent
        self.worker = worker
        self.on_complete = on_complete
        
        # Parent root reference
        root = parent.winfo_toplevel() if hasattr(parent, 'winfo_toplevel') else parent
        self.dialog = tk.Toplevel(root)
        self.dialog.title(title)
        self.dialog.geometry("460x170")
        self.dialog.resizable(False, False)
        self.dialog.transient(root)
        self.dialog.grab_set()
        
        # Colors
        self.bg_color = getattr(parent, 'bg_color', "#0e1117")
        self.text_color = getattr(parent, 'text_color', "#f3f4f6")
        self.accent_color = getattr(parent, 'accent_color', "#3b82f6")
        self.card_color = getattr(parent, 'card_color', "#161922")
        self.dialog.configure(bg=self.bg_color)
        
        # Center dialog
        self.dialog.update_idletasks()
        rx = root.winfo_x()
        ry = root.winfo_y()
        rw = root.winfo_width()
        rh = root.winfo_height()
        dx = rx + max(0, (rw - 460) // 2)
        dy = ry + max(0, (rh - 170) // 2)
        self.dialog.geometry(f"+{dx}+{dy}")
        
        frame = tk.Frame(self.dialog, bg=self.bg_color, padx=18, pady=16)
        frame.pack(fill="both", expand=True)
        
        self.lbl_title = tk.Label(frame, text=title, font=("Segoe UI", 11, "bold"), fg=self.accent_color, bg=self.bg_color)
        self.lbl_title.pack(anchor="w", pady=(0, 4))
        
        self.lbl_msg = tk.Label(frame, text="Starting background task...", font=("Segoe UI", 9), fg=self.text_color, bg=self.bg_color, anchor="w")
        self.lbl_msg.pack(fill="x", pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(frame, mode="determinate", maximum=100)
        self.progress_bar.pack(fill="x", pady=(0, 10))
        
        btn_bar = tk.Frame(frame, bg=self.bg_color)
        btn_bar.pack(fill="x")
        
        self.lbl_time = tk.Label(btn_bar, text="Elapsed: 0.0s", font=("Segoe UI", 8), fg="#9ca3af", bg=self.bg_color)
        self.lbl_time.pack(side="left")
        
        self.btn_cancel = tk.Button(btn_bar, text="Cancel", command=self.cancel_task,
                                    bg=self.card_color, fg=self.text_color, font=("Segoe UI", 9), relief="flat", padx=14, pady=2)
        self.btn_cancel.pack(side="right")
        
        # Start worker and polling
        self.worker.start()
        self.dialog.after(50, self.poll_queue)

    def cancel_task(self):
        self.worker.cancel()
        self.btn_cancel.config(text="Cancelling...", state="disabled")
        self.lbl_msg.config(text="Cancelling task, please wait...")

    def poll_queue(self):
        try:
            while not self.worker.queue.empty():
                prog: TaskProgress = self.worker.queue.get_nowait()
                if prog.total > 0:
                    pct = int((prog.current / prog.total) * 100)
                    self.progress_bar["value"] = pct
                self.lbl_msg.config(text=prog.message[:65])
                self.lbl_time.config(text=f"Elapsed: {prog.elapsed_sec:.1f}s")
                
                if prog.stage in ("complete", "error", "cancelled"):
                    self.dialog.destroy()
                    if self.on_complete:
                        self.on_complete(prog)
                    return
        except Exception:
            pass
            
        if self.dialog.winfo_exists():
            self.dialog.after(50, self.poll_queue)
