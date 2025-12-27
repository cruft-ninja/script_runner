#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bash Script Runner GUI - Modern Themed with Sun Valley ttk (sv-ttk)

Features:
- Beautiful modern dark/light theming using sv-ttk (Sun Valley style)
- Automatic perfect theming for all ttk widgets
- Scratchpad mode with plain text editing
- Themed sudo password dialog (mostly ttk)
- Tooltips, filtering, logging, etc.

Note: Requires `sv-ttk` package: pip install sv-ttk
"""

import json
import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk
from tkfilebrowser import asksaveasfilename
import sv_ttk  # Modern Sun Valley theme
from typing import List, Dict, Optional

# Constants
CONFIG_FILE = "scripts.json"
BUTTONS_PER_ROW = 5
GRID_PAD = 10
LOG_LINES = 15
DEFAULT_MAX_CONCURRENT = 5
DEFAULT_DARK_MODE = True
TOOLTIP_BG = "#ffffc0"
TOOLTIP_FG = "#000000"
TOOLTIP_FONT = ("Helvetica", 11)
LOG_FONT = ("Consolas", 12)
LABEL_FONT = ("Helvetica", 12)


class ToolTip:
    """Theme-aware tooltip class."""

    def __init__(self, widget: tk.Widget, text: str):
        self.widget = widget
        self.text = text
        self.tip: Optional[tk.Toplevel] = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        if self.tip or not self.text:
            return
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 1
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        tk.Label(
            self.tip,
            text=self.text,
            justify="left",
            background=TOOLTIP_BG,
            foreground=TOOLTIP_FG,
            relief="solid",
            borderwidth=1,
            font=TOOLTIP_FONT,
            padx=8,
            pady=4,
            wraplength=300,
        ).pack()

    def hide(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


class ScriptRunnerApp:
    """Main application class for the Bash Script Runner GUI."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Bash Script Runner")

        self.dark_mode = DEFAULT_DARK_MODE
        sv_ttk.set_theme("dark" if self.dark_mode else "light")

        self.scripts: List[Dict] = self.load_scripts()
        self.path_to_label = {s["path"]: s["label"] for s in self.scripts}
        self.running_scripts: Dict[str, bool] = {}
        self.script_frames: Dict[str, ttk.Frame] = {}
        self.script_texts: Dict[str, tk.Text] = {}
        self.all_texts: List[tk.Text] = []
        self.buttons: List[tuple[ttk.Button, str, List[str], str]] = []

        self.max_concurrent_var = tk.IntVar(value=DEFAULT_MAX_CONCURRENT)

        self.setup_ui()

    def load_scripts(self) -> List[Dict]:
        """Load scripts from JSON config file."""
        if not os.path.exists(CONFIG_FILE):
            raise FileNotFoundError(f"Config file {CONFIG_FILE} not found.")
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def setup_ui(self):
        """Set up the main UI components."""
        self.setup_log_notebook()
        self.setup_controls_frame()
        self.setup_filter_frame()
        self.setup_button_grid()
        self.apply_filters()

        self.root.update_idletasks()
        self.root.geometry(f"{max(self.root.winfo_width(), 900)}x{self.root.winfo_reqheight()}")
        self.search_entry.focus_set()

    def setup_log_notebook(self):
        """Set up the log notebook with console and scratchpad."""
        self.log_notebook = ttk.Notebook(self.root)
        self.log_notebook.pack(fill="both", expand=True, padx=15, pady=15)
        self.log_notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        self.log_notebook.bind("<B1-Motion>", self.reorder_tab)

        # Main log
        main_log_frame = ttk.Frame(self.log_notebook)
        self.main_log_text = tk.Text(
            main_log_frame, height=LOG_LINES, font=LOG_FONT, wrap="word", undo=True, state="disabled"
        )
        self.main_log_text.pack(side="left", fill="both", expand=True)
        main_scrollbar = ttk.Scrollbar(
            main_log_frame, orient="vertical", command=self.main_log_text.yview
        )
        main_scrollbar.pack(side="right", fill="y")
        self.main_log_text.config(yscrollcommand=main_scrollbar.set)
        self.log_notebook.add(main_log_frame, text="Console")

        # Scratchpad
        scratch_frame = ttk.Frame(self.log_notebook)
        self.scratch_text = tk.Text(
            scratch_frame, height=LOG_LINES, font=LOG_FONT, wrap="word", undo=True, state="normal"
        )
        self.scratch_text.pack(side="left", fill="both", expand=True)
        scratch_scrollbar = ttk.Scrollbar(
            scratch_frame, orient="vertical", command=self.scratch_text.yview
        )
        scratch_scrollbar.pack(side="right", fill="y")
        self.scratch_text.config(yscrollcommand=scratch_scrollbar.set)
        self.log_notebook.add(scratch_frame, text="Scratchpad")

        self.all_texts = [self.main_log_text, self.scratch_text]

    def setup_controls_frame(self):
        """Set up the controls frame with buttons and settings."""
        self.controls_frame = ttk.Frame(self.root)
        self.controls_frame.pack(pady=(0, 10))

        save_btn = ttk.Button(self.controls_frame, text="Save Current Tab", command=self.save_current_tab)
        save_btn.pack(side="left", padx=10)
        ToolTip(save_btn, "Save current tab content to a file")

        self.close_btn = ttk.Button(
            self.controls_frame, text="Close Current Tab", command=self.close_current_tab
        )
        self.close_btn.pack(side="left", padx=10)
        ToolTip(self.close_btn, "Close the current script tab (if not running)")

        clear_tabs_btn = ttk.Button(
            self.controls_frame, text="Clear Tabs", command=self.close_finished_tabs
        )
        clear_tabs_btn.pack(side="left", padx=10)
        ToolTip(clear_tabs_btn, "Close all script tabs that have finished running")

        ttk.Label(self.controls_frame, text="Max Concurrent:").pack(side="left", padx=10)
        max_concurrent_spin = ttk.Spinbox(
            self.controls_frame,
            from_=1,
            to=20,
            textvariable=self.max_concurrent_var,
            width=5,
        )
        max_concurrent_spin.pack(side="left", padx=10)
        ToolTip(max_concurrent_spin, "Set the maximum number of concurrent script executions (1-20)")

        dark_btn = ttk.Button(
            self.controls_frame,
            text="Disable Dark Mode" if self.dark_mode else "Enable Dark Mode",
            command=self.toggle_dark_mode,
        )
        dark_btn.pack(side="right", padx=10)
        ToolTip(dark_btn, "Switch between light and dark theme")

    def setup_filter_frame(self):
        """Set up the filter frame for search and tags."""
        self.filter_frame = ttk.Frame(self.root)
        self.filter_frame.pack(pady=10, padx=50, fill="x")

        ttk.Label(self.filter_frame, text="Search:", font=LABEL_FONT).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            self.filter_frame, textvariable=self.search_var, font=LABEL_FONT, width=40
        )
        self.search_entry.pack(side="left", padx=10, fill="x", expand=True)

        clear_search_btn = ttk.Button(
            self.filter_frame, text="✖", command=lambda: self.search_var.set(""), width=3
        )
        clear_search_btn.pack(side="left")

        ttk.Label(self.filter_frame, text="Tag:", font=LABEL_FONT).pack(side="left", padx=(20, 0))

        all_tags = sorted({t for s in self.scripts for t in s["tags"]})
        self.tag_var = tk.StringVar(value="All Tags")
        tag_menu = ttk.OptionMenu(
            self.filter_frame, self.tag_var, "All Tags", "All Tags", *all_tags
        )
        tag_menu.pack(side="left", padx=10, fill="x", expand=True)

        self.search_var.trace("w", self.apply_filters)
        self.tag_var.trace("w", self.apply_filters)

    def setup_button_grid(self):
        """Set up the button grid for scripts."""
        self.btn_frame = ttk.Frame(self.root)
        self.btn_frame.pack(pady=10)

        for i in range(BUTTONS_PER_ROW):
            self.btn_frame.grid_columnconfigure(i, weight=1)

        for script in self.scripts:
            label = script["label"]
            path = script["path"]
            needs_sudo = script["needs_sudo"]
            tags = script["tags"]
            tip = script["description"]

            btn = ttk.Button(
                self.btn_frame,
                text=label,
                width=18,
                command=lambda p=path, ns=needs_sudo: self.run_script(p, ns),
            )
            ToolTip(btn, tip)
            self.buttons.append((btn, label.lower(), [t.lower() for t in tags], path))

    def apply_filters(self, *args):
        """Apply search and tag filters to buttons."""
        term = self.search_var.get().lower()
        tag = self.tag_var.get().lower() if self.tag_var.get() != "All Tags" else None
        visible = []
        for btn, name, btags, _ in self.buttons:
            match = (not term or term in name) and (tag is None or tag in btags)
            if match:
                visible.append(btn)
            else:
                btn.grid_remove()
        for i, btn in enumerate(visible):
            btn.grid(
                row=i // BUTTONS_PER_ROW,
                column=i % BUTTONS_PER_ROW,
                padx=GRID_PAD,
                pady=GRID_PAD,
                sticky="ew",
            )
        self.root.update_idletasks()
        self.root.geometry(f"{self.root.winfo_width()}x{self.root.winfo_reqheight()}")

    def toggle_dark_mode(self):
        """Toggle between dark and light themes."""
        self.dark_mode = not self.dark_mode
        sv_ttk.set_theme("dark" if self.dark_mode else "light")

    def log(self, msg: str, target: tk.Text = None):
        """Log a message to the specified text widget."""
        if target is None:
            target = self.main_log_text

        def _write():
            was_disabled = target.cget("state") == "disabled"
            if was_disabled:
                target.config(state="normal")
            target.insert("end", msg + "\n")
            if was_disabled:
                target.config(state="disabled")
            target.see("end")

        self.root.after(0, _write)

    def clear_current_tab(self):
        """Clear the content of the current tab."""
        current_tab = self.log_notebook.select()
        if not current_tab:
            return
        frame = self.root.nametowidget(current_tab)
        text_widget = next(
            (c for c in frame.winfo_children() if isinstance(c, tk.Text)), None
        )
        if text_widget is None:
            return
        was_disabled = text_widget.cget("state") == "disabled"
        if was_disabled:
            text_widget.config(state="normal")
        text_widget.delete(1.0, "end")
        if was_disabled:
            text_widget.config(state="disabled")

    def save_current_tab(self):
        """Save the content of the current tab to a file."""
        current_tab = self.log_notebook.select()
        if not current_tab:
            return
        frame = self.root.nametowidget(current_tab)
        text_widget = next(
            (c for c in frame.winfo_children() if isinstance(c, tk.Text)), None
        )
        if text_widget is None:
            return
        content = text_widget.get(1.0, "end").strip()
        if not content:
            self.log("[INFO] Current tab is empty — nothing to save.")
            return
        file_path = asksaveasfilename(
            parent=self.root,
            title="Save Tab Content",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="tab_content.txt",
        )
        if not file_path:
            self.log("[INFO] Save cancelled.")
            return
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.log(f"[INFO] Tab saved to: {file_path}")
        except Exception as e:
            self.log(f"[ERROR] Failed to save: {e}")

    def close_current_tab(self):
        """Close the current script tab if not running."""
        current_tab = self.log_notebook.select()
        if not current_tab:
            return
        tab_text = self.log_notebook.tab(current_tab, "text")
        if tab_text in ["Console", "Scratchpad"]:
            self.log("[INFO] Cannot close permanent tabs.")
            return
        frame = self.root.nametowidget(current_tab)
        path = next((p for p, f in self.script_frames.items() if f == frame), None)
        if not path or (path in self.running_scripts and self.running_scripts[path]):
            self.log("[WARN] Cannot close tab while script is running or invalid tab.")
            return
        self.log_notebook.forget(current_tab)
        frame.destroy()
        del self.script_frames[path]
        text = self.script_texts.pop(path)
        self.all_texts.remove(text)
        self.log_notebook.select(self.log_notebook.nametowidget(".!notebook.!frame"))
        self.log(f"[INFO] Closed tab: {tab_text}")

    def close_finished_tabs(self):
        """Close all finished script tabs."""
        to_close = []
        for path, frame in list(self.script_frames.items()):
            text = self.script_texts[path]
            content = text.get(1.0, "end").rstrip()
            if content.endswith("#" * 50) and not (
                path in self.running_scripts and self.running_scripts[path]
            ):
                to_close.append((path, frame, text))
        for path, frame, text in to_close:
            tab_text = self.log_notebook.tab(frame, "text")
            self.log_notebook.forget(frame)
            frame.destroy()
            del self.script_frames[path]
            del self.script_texts[path]
            self.all_texts.remove(text)
            self.log(f"[INFO] Closed finished tab: {tab_text}")
        self.log_notebook.select(self.log_notebook.nametowidget(".!notebook.!frame"))

    def on_tab_change(self, event):
        """Handle tab change to enable/disable close button."""
        current_tab = self.log_notebook.select()
        if not current_tab:
            self.close_btn.config(state="disabled")
            return
        tab_text = self.log_notebook.tab(current_tab, "text")
        self.close_btn.config(
            state="normal" if tab_text not in ["Console", "Scratchpad"] else "disabled"
        )

    def reorder_tab(self, event):
        """Reorder tabs via drag-and-drop."""
        try:
            index = self.log_notebook.index(f"@{event.x},{event.y}")
            self.log_notebook.insert(index, child=self.log_notebook.select())
        except tk.TclError:
            pass

    def ask_password(self) -> Optional[str]:
        """Prompt for sudo password in a themed dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Sudo Password")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.geometry(
            f"400x180+{self.root.winfo_rootx()+200}+{self.root.winfo_rooty()+150}"
        )

        ttk.Label(dialog, text="Enter your sudo password:", font=LABEL_FONT).pack(pady=20)

        pw_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=pw_var, show="*", width=30, font=LABEL_FONT)
        entry.pack(pady=5, padx=40, fill="x")
        entry.focus()

        show_var = tk.BooleanVar()

        def toggle_show():
            entry.config(show="" if show_var.get() else "*")

        ttk.Checkbutton(dialog, text="Show password", variable=show_var, command=toggle_show).pack(
            pady=5
        )

        result = [None]

        def ok():
            result[0] = pw_var.get()
            dialog.destroy()

        def cancel():
            dialog.destroy()

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="OK", command=ok).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Cancel", command=cancel).pack(side="right", padx=10)

        self.root.wait_window(dialog)
        return result[0]

    def set_button_state(self, path: str, state: str):
        """Set the state of a script button."""
        for btn_data in self.buttons:
            btn, _, _, btn_path = btn_data
            if btn_path == path:
                btn.config(state=state)
                break

    def run_script(self, path: str, needs_sudo: bool):
        """Run a bash script in a separate thread."""
        if len(self.running_scripts) >= self.max_concurrent_var.get():
            self.log("[WARN] Maximum concurrent scripts reached. Please wait.")
            return
        if path in self.running_scripts and self.running_scripts[path]:
            self.log("[WARN] This script is already running. Please wait.")
            return
        self.running_scripts[path] = True
        self.set_button_state(path, "disabled")

        if path == "Clear Log":
            self.clear_current_tab()
            self.running_scripts.pop(path, None)
            self.set_button_state(path, "normal")
            return

        full_path = os.path.join(os.path.dirname(__file__), path)
        if not os.path.exists(full_path):
            self.log(f"[ERROR] Script not found: {full_path}")
            self.running_scripts.pop(path, None)
            self.set_button_state(path, "normal")
            return

        if path not in self.script_texts:
            frame = ttk.Frame(self.log_notebook)
            text = tk.Text(
                frame, height=LOG_LINES, font=LOG_FONT, wrap="word", undo=True, state="disabled"
            )
            sb = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
            text.config(yscrollcommand=sb.set)
            text.pack(side="left", fill="both", expand=True)
            sb.pack(side="right", fill="y")
            label = self.path_to_label.get(path, os.path.basename(path))
            self.log_notebook.add(frame, text=label)
            self.script_frames[path] = frame
            self.script_texts[path] = text
            self.all_texts.append(text)

        target = self.script_texts[path]
        frame = self.script_frames[path]
        self.log_notebook.select(frame)

        self.log("\n" + "#" * 50, target=target)
        self.log(f"[INFO] Running: {full_path}", target=target)

        password = None
        if needs_sudo:
            try:
                subprocess.check_call(
                    ["sudo", "-n", "true"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                sudo_cached = True
            except subprocess.CalledProcessError:
                sudo_cached = False
            if not sudo_cached:
                password = self.ask_password()
                if password is None:
                    self.log("[WARN] Aborted by user.")
                    self.running_scripts.pop(path, None)
                    self.set_button_state(path, "normal")
                    return

        if needs_sudo:
            cmd = (
                ["sudo", "-S" if password else "", "bash", full_path]
                if password or not sudo_cached
                else ["sudo", "bash", full_path]
            )
            cmd = [c for c in cmd if c]  # Remove empty strings
        else:
            cmd = ["bash", full_path]

        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE if password else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(full_path or "."),
            )
            if password:
                proc.stdin.write(password + "\n")  # type: ignore
                proc.stdin.close()  # type: ignore

            def read_stream(stream, prefix: str, tgt: tk.Text):
                for line in iter(stream.readline, ""):
                    self.log(f"[{prefix}] {line.rstrip()}", target=tgt)

            threading.Thread(
                target=read_stream, args=(proc.stdout, "OUT", target), daemon=True  # type: ignore
            ).start()
            threading.Thread(
                target=read_stream, args=(proc.stderr, "ERR", target), daemon=True  # type: ignore
            ).start()

            def done(tgt: tk.Text, pth: str):
                proc.wait()
                status = "DONE" if proc.returncode == 0 else f"FAIL ({proc.returncode})"
                self.log(f"[{status}] {os.path.basename(pth)}", target=tgt)
                self.log("#" * 50, target=tgt)
                self.running_scripts.pop(pth, None)
                self.set_button_state(pth, "normal")

            threading.Thread(target=done, args=(target, path), daemon=True).start()

        except Exception as e:
            self.log(f"[ERROR] {e}")
            self.running_scripts.pop(path, None)
            self.set_button_state(path, "normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = ScriptRunnerApp(root)
    root.mainloop()