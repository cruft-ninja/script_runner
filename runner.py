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

import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk
from tkfilebrowser import asksaveasfilename
import sv_ttk  # Modern Sun Valley theme

# ======================================================================
# CONFIGURATION SECTION
# ======================================================================
scripts = [
    (
        "Clear Log", False, "Clear Log", ["utility", "log"],
        "Clear all output from the log window"
    ),
    (
        "Image Import", False, "/home/ninja/apps/script_runner/bash/images_from_cam",
        ["media", "import"], "Import photos from connected camera"
    ),
    (
        "Keyboard Toggle", False, "/home/ninja/apps/script_runner/bash/toggle_onboard",
        ["hardware", "keyboard"], "Toggle the on-screen keyboard visibility"
    ),
    (
        "Docker Watchtower", False, "/home/ninja/apps/script_runner/bash/update_docker_images",
        ["docker", "update"], "Automatically update all Docker containers"
    ),
    (
        "Docker Prune", False, "/home/ninja/apps/script_runner/bash/docker_image_prune",
        ["docker", "cleanup"], "Remove unused Docker images"
    ),
    (
        "Ollama Update", True, "/home/ninja/apps/script_runner/bash/ollama_update",
        ["ai", "ollama", "update"], "Update Ollama to the latest version"
    ),
    (
        "Ollama Models Update", False,
        "/home/ninja/apps/script_runner/bash/ollama_model_update",
        ["ai", "ollama", "models", "update"],
        "Pull latest versions of installed Ollama models"
    ),
    (
        "System Update", True, "/home/ninja/apps/script_runner/bash/update_system",
        ["system", "update"], "Full system package update and upgrade"
    ),
    (
        "Clear System Logs", True, "/home/ninja/apps/script_runner/bash/purge_logs",
        ["system", "log", "cleanup"], "Safely clear old system logs"
    ),
    (
        "System Monitor", False, "/home/ninja/apps/script_runner/bash/system_monitor",
        ["system", "monitoring"], "Open system monitor"
    ),
    (
        "Open WebUI", False, "/home/ninja/apps/script_runner/bash/openwebui",
        ["ai", "ollama"], "Launch Ollama Web UI in Chromium browser"
    ),
    (
        "Gmail", False, "/home/ninja/apps/script_runner/bash/gmail",
        ["web", "gmail"], "Open Gmail in Chromium browser"
    ),
    (
        "Grok", False, "/home/ninja/apps/script_runner/bash/grok",
        ["web", "ai"], "Open Grok AI chat"
    ),
    (
        "Edit Source", False, "/home/ninja/apps/script_runner/bash/edit_source",
        ["utility", "edit"],
        "Open this script runner source code for editing"
    ),
]

path_to_label = {s[2]: s[0] for s in scripts}

BUTTONS_PER_ROW = 5
GRID_PAD = 10
LOG_LINES = 15

running_scripts = {}  # path -> True if running

# ======================================================================
# MAIN WINDOW & THEMING SETUP
# ======================================================================
root = tk.Tk()  # Standard Tk root for sv-ttk compatibility
root.title("Bash Script Runner")

dark_mode = True  # Start in dark mode
sv_ttk.set_theme("dark" if dark_mode else "light")

max_concurrent_var = tk.IntVar(value=5)

# ======================================================================
# TOOLTIP CLASS (now theme-aware where possible)
# ======================================================================
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
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
        # Use softer colors that work better in both themes
        tk.Label(self.tip, text=self.text, justify="left",
                 background="#ffffc0", foreground="#000000",  # Slightly darker yellow
                 relief="solid", borderwidth=1, font=("Helvetica", 11),
                 padx=8, pady=4, wraplength=300).pack()

    def hide(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None

# ======================================================================
# LOG / SCRATCHPAD AREA
# ======================================================================
log_notebook = ttk.Notebook(root)
log_notebook.pack(fill="both", expand=True, padx=15, pady=15)

main_log_frame = ttk.Frame(log_notebook)
main_log_text = tk.Text(main_log_frame, height=LOG_LINES,
                        font=("Consolas", 12), wrap="word", undo=True,
                        state="disabled")
main_log_text.pack(side="left", fill="both", expand=True)
main_scrollbar = ttk.Scrollbar(main_log_frame, orient="vertical",
                               command=main_log_text.yview)
main_scrollbar.pack(side="right", fill="y")
main_log_text.config(yscrollcommand=main_scrollbar.set)
log_notebook.add(main_log_frame, text="Console")

scratch_frame = ttk.Frame(log_notebook)
scratch_text = tk.Text(scratch_frame, height=LOG_LINES,
                       font=("Consolas", 12), wrap="word", undo=True,
                       state="normal")
scratch_text.pack(side="left", fill="both", expand=True)
scratch_scrollbar = ttk.Scrollbar(scratch_frame, orient="vertical",
                                  command=scratch_text.yview)
scratch_scrollbar.pack(side="right", fill="y")
scratch_text.config(yscrollcommand=scratch_scrollbar.set)
log_notebook.add(scratch_frame, text="Scratchpad")

all_texts = [main_log_text, scratch_text]
script_frames = {}
script_texts = {}

# ======================================================================
# CONTROL BUTTONS
# ======================================================================
controls_frame = ttk.Frame(root)
controls_frame.pack(pady=(0, 10))

def save_current_tab():
    current_tab = log_notebook.select()
    if not current_tab:
        return
    frame = root.nametowidget(current_tab)
    text_widget = next((c for c in frame.winfo_children() if isinstance(c, tk.Text)), None)
    if text_widget is None:
        return
    content = text_widget.get(1.0, "end").strip()
    if not content:
        log("[INFO] Current tab is empty — nothing to save.")
        return
    file_path = asksaveasfilename(
        parent=root,
        title="Save Tab Content",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        initialfile="tab_content.txt"
    )
    if not file_path:
        log("[INFO] Save cancelled.")
        return
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        log(f"[INFO] Tab saved to: {file_path}")
    except Exception as e:
        log(f"[ERROR] Failed to save: {e}")

save_btn = ttk.Button(controls_frame, text="Save Current Tab", command=save_current_tab)
save_btn.pack(side="left", padx=10)
ToolTip(save_btn, "Save current tab content to a file")

def close_current_tab():
    current_tab = log_notebook.select()
    if not current_tab:
        return
    tab_text = log_notebook.tab(current_tab, "text")
    if tab_text in ["Console", "Scratchpad"]:
        log("[INFO] Cannot close permanent tabs.")
        return
    frame = root.nametowidget(current_tab)
    path = next((p for p, f in script_frames.items() if f == frame), None)
    if not path or (path in running_scripts and running_scripts[path]):
        log("[WARN] Cannot close tab while script is running or invalid tab.")
        return
    log_notebook.forget(current_tab)
    frame.destroy()
    del script_frames[path]
    text = script_texts.pop(path)
    all_texts.remove(text)
    log_notebook.select(main_log_frame)
    log(f"[INFO] Closed tab: {tab_text}")

close_btn = ttk.Button(controls_frame, text="Close Current Tab", command=close_current_tab)
close_btn.pack(side="left", padx=10)
ToolTip(close_btn, "Close the current script tab (if not running)")

def close_finished_tabs():
    to_close = []
    for path, frame in list(script_frames.items()):
        text = script_texts[path]
        content = text.get(1.0, "end").rstrip()
        if content.endswith("#" * 50) and not (path in running_scripts and running_scripts[path]):
            to_close.append((path, frame, text))
    for path, frame, text in to_close:
        tab_text = log_notebook.tab(frame, "text")
        log_notebook.forget(frame)
        frame.destroy()
        del script_frames[path]
        del script_texts[path]
        all_texts.remove(text)
        log(f"[INFO] Closed finished tab: {tab_text}")
    log_notebook.select(main_log_frame)

clear_tabs_btn = ttk.Button(controls_frame, text="Clear Tabs", command=close_finished_tabs)
clear_tabs_btn.pack(side="left", padx=10)
ToolTip(clear_tabs_btn, "Close all script tabs that have finished running")

ttk.Label(controls_frame, text="Max Concurrent:").pack(side="left", padx=10)
max_concurrent_spin = ttk.Spinbox(controls_frame, from_=1, to=20,
                                  textvariable=max_concurrent_var, width=5)
max_concurrent_spin.pack(side="left", padx=10)
ToolTip(max_concurrent_spin, "Set the maximum number of concurrent script executions (1-20)")

def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    sv_ttk.set_theme("dark" if dark_mode else "light")
    dark_btn.config(text="Disable Dark Mode" if dark_mode else "Enable Dark Mode")

dark_btn = ttk.Button(controls_frame, text="Disable Dark Mode", command=toggle_dark_mode)
dark_btn.pack(side="right", padx=10)
ToolTip(dark_btn, "Switch between light and dark theme")

# ======================================================================
# LOGGING & CLEAR
# ======================================================================
def log(msg, target=main_log_text):
    def _write():
        was_disabled = target.cget("state") == "disabled"
        if was_disabled:
            target.config(state="normal")
        target.insert("end", msg + "\n")
        if was_disabled:
            target.config(state="disabled")
        target.see("end")
    root.after(0, _write)

def clear_current_tab():
    current_tab = log_notebook.select()
    if not current_tab:
        return
    frame = root.nametowidget(current_tab)
    text_widget = next((c for c in frame.winfo_children() if isinstance(c, tk.Text)), None)
    if text_widget is None:
        return
    was_disabled = text_widget.cget("state") == "disabled"
    if was_disabled:
        text_widget.config(state="normal")
    text_widget.delete(1.0, "end")
    if was_disabled:
        text_widget.config(state="disabled")

# ======================================================================
# SUDO PASSWORD DIALOG
# ======================================================================
def ask_password():
    dialog = tk.Toplevel(root)
    dialog.title("Sudo Password")
    dialog.transient(root)
    dialog.grab_set()
    dialog.geometry(f"400x180+{root.winfo_rootx()+200}+{root.winfo_rooty()+150}")

    ttk.Label(dialog, text="Enter your sudo password:", font=("Helvetica", 12)).pack(pady=20)

    pw_var = tk.StringVar()
    entry = ttk.Entry(dialog, textvariable=pw_var, show="*", width=30, font=("Helvetica", 12))
    entry.pack(pady=5, padx=40, fill="x")
    entry.focus()

    show_var = tk.BooleanVar()
    def toggle_show():
        entry.config(show="" if show_var.get() else "*")
    ttk.Checkbutton(dialog, text="Show password", variable=show_var, command=toggle_show).pack(pady=5)

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

    root.wait_window(dialog)
    return result[0]

# ======================================================================
# SCRIPT EXECUTION
# ======================================================================
def set_button_state(path, state):
    for btn_data in buttons:
        btn, _, _, btn_path = btn_data
        if btn_path == path:
            btn.config(state=state)
            break

def run_script(path, needs_sudo):
    if len(running_scripts) >= max_concurrent_var.get():
        log("[WARN] Maximum concurrent scripts reached. Please wait.")
        return
    if path in running_scripts and running_scripts[path]:
        log("[WARN] This script is already running. Please wait.")
        return
    running_scripts[path] = True
    set_button_state(path, "disabled")

    if path == "Clear Log":
        clear_current_tab()
        running_scripts.pop(path, None)
        set_button_state(path, "normal")
        return
    if not os.path.exists(path):
        log(f"[ERROR] Script not found: {path}")
        running_scripts.pop(path, None)
        set_button_state(path, "normal")
        return

    if path not in script_texts:
        frame = ttk.Frame(log_notebook)
        text = tk.Text(frame, height=LOG_LINES, font=("Consolas", 12),
                       wrap="word", undo=True, state="disabled")
        sb = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        text.config(yscrollcommand=sb.set)
        text.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        label = path_to_label.get(path, os.path.basename(path))
        log_notebook.add(frame, text=label)
        script_frames[path] = frame
        script_texts[path] = text
        all_texts.append(text)

    target = script_texts[path]
    frame = script_frames[path]
    log_notebook.select(frame)

    log("\n" + "#" * 50, target=target)
    log(f"[INFO] Running: {path}", target=target)

    password = None
    if needs_sudo:
        try:
            subprocess.check_call(['sudo', '-n', 'true'],
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)
            sudo_cached = True
        except subprocess.CalledProcessError:
            sudo_cached = False
        if not sudo_cached:
            password = ask_password()
            if password is None:
                log("[WARN] Aborted by user.")
                running_scripts.pop(path, None)
                set_button_state(path, "normal")
                return

    if needs_sudo:
        cmd = ["sudo", "-S" if password else "", "bash", path] if password or not sudo_cached else ["sudo", "bash", path]
        cmd = [c for c in cmd if c]  # Remove empty strings
    else:
        cmd = ["bash", path]

    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE if password else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(path or ".")
        )
        if password:
            proc.stdin.write(password + "\n")
            proc.stdin.close()

        def read_stream(stream, prefix, tgt):
            for line in stream:
                log(f"[{prefix}] {line.rstrip()}", target=tgt)
        threading.Thread(target=read_stream, args=(proc.stdout, "OUT", target), daemon=True).start()
        threading.Thread(target=read_stream, args=(proc.stderr, "ERR", target), daemon=True).start()

        def done(tgt, pth):
            proc.wait()
            status = "DONE" if proc.returncode == 0 else f"FAIL ({proc.returncode})"
            log(f"[{status}] {os.path.basename(pth)}", target=tgt)
            log("#" * 50, target=tgt)
            running_scripts.pop(pth, None)
            set_button_state(pth, "normal")
        threading.Thread(target=done, args=(target, path), daemon=True).start()

    except Exception as e:
        log(f"[ERROR] {e}")
        running_scripts.pop(path, None)
        set_button_state(path, "normal")

# ======================================================================
# FILTERING CONTROLS
# ======================================================================
filter_frame = ttk.Frame(root)
filter_frame.pack(pady=10, padx=50, fill="x")

ttk.Label(filter_frame, text="Search:", font=("Helvetica", 12)).pack(side="left")
search_var = tk.StringVar()
search_entry = ttk.Entry(filter_frame, textvariable=search_var, font=("Helvetica", 12), width=40)
search_entry.pack(side="left", padx=10, fill="x", expand=True)

clear_search_btn = ttk.Button(filter_frame, text="✖",
                              command=lambda: search_var.set(""), width=3)
clear_search_btn.pack(side="left")

ttk.Label(filter_frame, text="Tag:", font=("Helvetica", 12)).pack(side="left", padx=(20, 0))

all_tags = sorted({t for s in scripts for t in s[3]})
tag_var = tk.StringVar(value="All Tags")
tag_menu = ttk.OptionMenu(filter_frame, tag_var, "All Tags", "All Tags", *all_tags)
tag_menu.pack(side="left", padx=10, fill="x", expand=True)

# ======================================================================
# BUTTON GRID
# ======================================================================
btn_frame = ttk.Frame(root)
btn_frame.pack(pady=10)

for i in range(BUTTONS_PER_ROW):
    btn_frame.grid_columnconfigure(i, weight=1)

buttons = []

for i, (label, needs_sudo, path, tags, tip) in enumerate(scripts):
    btn = ttk.Button(
        btn_frame,
        text=label,
        width=18,
        command=lambda p=path, ns=needs_sudo: run_script(p, ns)
    )
    btn.grid(row=i//BUTTONS_PER_ROW, column=i % BUTTONS_PER_ROW,
             padx=GRID_PAD, pady=GRID_PAD, sticky="ew")
    ToolTip(btn, tip)
    buttons.append((btn, label.lower(), [t.lower() for t in tags], path))

# ======================================================================
# DYNAMIC FILTERING
# ======================================================================
def apply_filters(*_):
    term = search_var.get().lower()
    tag = tag_var.get().lower() if tag_var.get() != "All Tags" else None
    visible = []
    for btn, name, btags, _ in buttons:
        match = (not term or term in name) and (tag is None or tag in btags)
        if match:
            visible.append(btn)
        else:
            btn.grid_remove()
    for i, btn in enumerate(visible):
        btn.grid(row=i//BUTTONS_PER_ROW, column=i % BUTTONS_PER_ROW,
                 padx=GRID_PAD, pady=GRID_PAD, sticky="ew")
    root.update_idletasks()
    root.geometry(f"{root.winfo_width()}x{root.winfo_reqheight()}")

search_var.trace("w", apply_filters)
tag_var.trace("w", apply_filters)
apply_filters()

# ======================================================================
# TAB CHANGE HANDLER
# ======================================================================
def on_tab_change(event):
    current_tab = log_notebook.select()
    if not current_tab:
        close_btn.config(state="disabled")
        return
    tab_text = log_notebook.tab(current_tab, "text")
    close_btn.config(state="normal" if tab_text not in ["Console", "Scratchpad"] else "disabled")

log_notebook.bind("<<NotebookTabChanged>>", on_tab_change)
on_tab_change(None)

# ======================================================================
# TAB REORDERING
# ======================================================================
def reorder_tab(event):
    try:
        index = log_notebook.index(f"@{event.x},{event.y}")
        log_notebook.insert(index, child=log_notebook.select())
    except tk.TclError:
        pass

log_notebook.bind("<B1-Motion>", reorder_tab)

# ======================================================================
# FINAL SETUP
# ======================================================================
root.update_idletasks()
root.geometry(f"{max(root.winfo_width(), 900)}x{root.winfo_reqheight()}")
search_entry.focus_set()

root.mainloop()