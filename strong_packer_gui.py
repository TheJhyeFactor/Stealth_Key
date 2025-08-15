#!/usr/bin/env python3
"""
Enhanced Nuitka GUI Packer
A comprehensive GUI for compiling Python scripts to native executables using Nuitka.

Features:
- Cross-platform support (Windows, macOS, Linux)
- Intuitive GUI with improved layout and validation
- Real-time build progress with threaded execution
- Advanced configuration options
- Build profiles and settings persistence
- Comprehensive error handling and logging
- Output verification and testing capabilities

Requirements:
- Python 3.8+
- Nuitka installed (pip install nuitka or pipx install nuitka)
- Platform-specific build tools (Visual Studio on Windows, Xcode on macOS, gcc/clang on Linux)
"""

import os
import sys
import json
import threading
import subprocess
import shutil
import platform
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import queue
import webbrowser

# Constants
APP_TITLE = "Enhanced Nuitka GUI Packer"
APP_VERSION = "2.0"
DEFAULT_EXE_NAME = "app"
CONFIG_FILE = Path.home() / ".nuitka_gui_config.json"

# Platform detection
IS_WINDOWS = (os.name == "nt")
IS_MAC = (sys.platform == "darwin")
IS_LINUX = sys.platform.startswith("linux")

class BuildConfig:
    """Configuration class for build settings"""
    
    def __init__(self):
        self.script_path = ""
        self.output_dir = str(Path.cwd())
        self.exe_name = DEFAULT_EXE_NAME
        self.icon_file = ""
        self.data_files = []
        self.extra_args = ""
        
        # Build flags
        self.onefile = True
        self.standalone = True
        self.no_console = False
        self.lto = True
        self.follow_imports = True
        self.nofollow_imports = False
        self.assume_yes = True
        self.show_progress = True
        self.remove_output = True
        self.enable_plugins = []
        self.disable_plugins = []
        
        # Advanced options
        self.optimization_level = ""
        self.python_flag = ""
        self.include_packages = []
        self.exclude_packages = []
        self.include_modules = []
        self.exclude_modules = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for JSON serialization"""
        return {k: v for k, v in self.__dict__.items()}
    
    def from_dict(self, data: Dict[str, Any]):
        """Load config from dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

class NuitkaRunner:
    """Handles Nuitka compilation process"""
    
    @staticmethod
    def check_nuitka() -> tuple[bool, str]:
        """Check if Nuitka is available and return version info"""
        nuitka_path = shutil.which("nuitka")
        if not nuitka_path:
            return False, "Nuitka not found in PATH"
        
        try:
            result = subprocess.run(
                [nuitka_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                return True, f"Found: {version}"
            else:
                return False, "Nuitka version check failed"
        except Exception as e:
            return False, f"Error checking Nuitka: {e}"
    
    @staticmethod
    def build_command(config: BuildConfig) -> List[str]:
        """Build the Nuitka command from configuration"""
        script_path = Path(config.script_path).resolve()
        output_dir = Path(config.output_dir).resolve()
        
        cmd = ["nuitka", str(script_path)]
        
        # Output configuration
        cmd.extend([f"--output-dir={output_dir}"])
        
        exe_name = config.exe_name
        if IS_WINDOWS and not exe_name.lower().endswith(".exe"):
            exe_name += ".exe"
        cmd.extend([f"--output-filename={exe_name}"])
        
        # Core build flags
        if config.onefile:
            cmd.append("--onefile")
        if config.standalone:
            cmd.append("--standalone")
        if config.no_console and IS_WINDOWS:
            cmd.append("--windows-console-mode=disable")
        if config.lto:
            cmd.append("--lto=yes")
        if config.follow_imports:
            cmd.append("--follow-imports")
        if config.nofollow_imports:
            cmd.append("--nofollow-imports")
        if config.assume_yes:
            cmd.append("--assume-yes-for-downloads")
        if config.show_progress:
            cmd.append("--show-progress")
        if config.remove_output:
            cmd.append("--remove-output")
        
        # Icon configuration
        if config.icon_file and Path(config.icon_file).exists():
            icon_path = Path(config.icon_file).resolve()
            if IS_WINDOWS:
                cmd.extend(["--windows-icon-from-ico", str(icon_path)])
            elif IS_MAC:
                cmd.extend(["--macos-app-icon", str(icon_path)])
        
        # Data files
        for data_spec in config.data_files:
            if data_spec.strip():
                cmd.extend([f"--include-data-files={data_spec}"])
        
        # Packages and modules
        for pkg in config.include_packages:
            if pkg.strip():
                cmd.extend([f"--include-package={pkg}"])
        
        for pkg in config.exclude_packages:
            if pkg.strip():
                cmd.extend([f"--nofollow-import-to={pkg}"])
        
        for mod in config.include_modules:
            if mod.strip():
                cmd.extend([f"--include-module={mod}"])
        
        # Plugins
        for plugin in config.enable_plugins:
            if plugin.strip():
                cmd.extend([f"--enable-plugin={plugin}"])
        
        for plugin in config.disable_plugins:
            if plugin.strip():
                cmd.extend([f"--disable-plugin={plugin}"])
        
        # Optimization (Python flags)
        if config.optimization_level and config.optimization_level in ["-O", "-OO"]:
            cmd.extend([f"--python-flag={config.optimization_level}"])
        
        # Prefer clang if available
        if shutil.which("clang"):
            cmd.append("--clang")
        
        # Extra arguments
        if config.extra_args.strip():
            cmd.extend(config.extra_args.split())
        
        # Error handling mode
        cmd.append("--noinclude-default-mode=error")
        
        return cmd

class LogWidget:
    """Enhanced logging widget with threading support"""
    
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Build Log")
        self.text = tk.Text(
            self.frame,
            height=15,
            wrap="word",
            state="disabled",
            font=("Consolas", 9) if IS_WINDOWS else ("Monaco", 9)
        )
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        self.text.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side="right", fill="y", padx=(0, 8), pady=8)
        
        # Message queue for thread-safe logging
        self.log_queue = queue.Queue()
        self.frame.after(100, self.process_log_queue)
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
    
    def log(self, message: str, level: str = "INFO"):
        """Thread-safe logging method"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {level}: {message}"
        self.log_queue.put(formatted_msg)
    
    def process_log_queue(self):
        """Process queued log messages"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.text.configure(state="normal")
                self.text.insert("end", message + "\n")
                self.text.see("end")
                self.text.configure(state="disabled")
                self.text.update_idletasks()
        except queue.Empty:
            pass
        finally:
            self.frame.after(100, self.process_log_queue)
    
    def clear(self):
        """Clear the log"""
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")

class AdvancedOptionsDialog:
    """Dialog for advanced Nuitka options"""
    
    def __init__(self, parent, config: BuildConfig):
        self.result = None
        self.config = config.to_dict()  # Work with a copy
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Advanced Options")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self._build_ui()
    
    def _build_ui(self):
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Packages tab
        pkg_frame = ttk.Frame(notebook)
        notebook.add(pkg_frame, text="Packages & Modules")
        self._build_packages_tab(pkg_frame)
        
        # Plugins tab
        plugin_frame = ttk.Frame(notebook)
        notebook.add(plugin_frame, text="Plugins")
        self._build_plugins_tab(plugin_frame)
        
        # Optimization tab
        opt_frame = ttk.Frame(notebook)
        notebook.add(opt_frame, text="Optimization")
        self._build_optimization_tab(opt_frame)
        
        # Buttons
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ttk.Button(btn_frame, text="OK", command=self._ok_clicked).pack(side="right", padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=self._cancel_clicked).pack(side="right")
    
    def _build_packages_tab(self, parent):
        # Include packages
        ttk.Label(parent, text="Include Packages:").pack(anchor="w", padx=5, pady=(5, 0))
        self.include_pkg_text = tk.Text(parent, height=4)
        self.include_pkg_text.pack(fill="x", padx=5, pady=2)
        self.include_pkg_text.insert("1.0", "\n".join(self.config.get("include_packages", [])))
        
        # Exclude packages
        ttk.Label(parent, text="Exclude Packages:").pack(anchor="w", padx=5, pady=(10, 0))
        self.exclude_pkg_text = tk.Text(parent, height=4)
        self.exclude_pkg_text.pack(fill="x", padx=5, pady=2)
        self.exclude_pkg_text.insert("1.0", "\n".join(self.config.get("exclude_packages", [])))
        
        # Include modules
        ttk.Label(parent, text="Include Modules:").pack(anchor="w", padx=5, pady=(10, 0))
        self.include_mod_text = tk.Text(parent, height=4)
        self.include_mod_text.pack(fill="x", padx=5, pady=2)
        self.include_mod_text.insert("1.0", "\n".join(self.config.get("include_modules", [])))
    
    def _build_plugins_tab(self, parent):
        # Enable plugins
        ttk.Label(parent, text="Enable Plugins:").pack(anchor="w", padx=5, pady=(5, 0))
        self.enable_plugins_text = tk.Text(parent, height=6)
        self.enable_plugins_text.pack(fill="x", padx=5, pady=2)
        self.enable_plugins_text.insert("1.0", "\n".join(self.config.get("enable_plugins", [])))
        
        # Common plugins info
        info_text = ("Common plugins: tk-inter, qt-plugins, numpy, matplotlib, "
                    "multiprocessing, pkg-resources, pylint-warnings")
        ttk.Label(parent, text=info_text, wraplength=550).pack(anchor="w", padx=5, pady=2)
        
        # Disable plugins
        ttk.Label(parent, text="Disable Plugins:").pack(anchor="w", padx=5, pady=(10, 0))
        self.disable_plugins_text = tk.Text(parent, height=4)
        self.disable_plugins_text.pack(fill="x", padx=5, pady=2)
        self.disable_plugins_text.insert("1.0", "\n".join(self.config.get("disable_plugins", [])))
    
    def _build_optimization_tab(self, parent):
        # Optimization level
        ttk.Label(parent, text="Python Optimization:").pack(anchor="w", padx=5, pady=(5, 0))
        self.opt_var = tk.StringVar(value=self.config.get("optimization_level", ""))
        opt_frame = ttk.Frame(parent)
        opt_frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Radiobutton(opt_frame, text="None", variable=self.opt_var, value="").pack(side="left", padx=10)
        ttk.Radiobutton(opt_frame, text="-O (basic)", variable=self.opt_var, value="-O").pack(side="left", padx=10)
        ttk.Radiobutton(opt_frame, text="-OO (remove docstrings)", variable=self.opt_var, value="-OO").pack(side="left", padx=10)
        
        # Python flags
        ttk.Label(parent, text="Additional Python Flags:").pack(anchor="w", padx=5, pady=(10, 0))
        self.python_flags_var = tk.StringVar(value=self.config.get("python_flag", ""))
        ttk.Entry(parent, textvariable=self.python_flags_var).pack(fill="x", padx=5, pady=2)
        
        ttk.Label(parent, text="Examples: -O (optimize), -OO (remove docstrings), -B (no .pyc files)", font=("TkDefaultFont", 8)).pack(anchor="w", padx=5)
    
    def _ok_clicked(self):
        # Collect all settings
        self.config["include_packages"] = [
            line.strip() for line in self.include_pkg_text.get("1.0", "end").splitlines() 
            if line.strip()
        ]
        self.config["exclude_packages"] = [
            line.strip() for line in self.exclude_pkg_text.get("1.0", "end").splitlines() 
            if line.strip()
        ]
        self.config["include_modules"] = [
            line.strip() for line in self.include_mod_text.get("1.0", "end").splitlines() 
            if line.strip()
        ]
        self.config["enable_plugins"] = [
            line.strip() for line in self.enable_plugins_text.get("1.0", "end").splitlines() 
            if line.strip()
        ]
        self.config["disable_plugins"] = [
            line.strip() for line in self.disable_plugins_text.get("1.0", "end").splitlines() 
            if line.strip()
        ]
        self.config["optimization_level"] = self.opt_var.get()
        self.config["python_flag"] = self.python_flags_var.get()
        
        self.result = self.config
        self.dialog.destroy()
    
    def _cancel_clicked(self):
        self.dialog.destroy()

class MainApplication:
    """Main application class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_TITLE} v{APP_VERSION}")
        self.root.geometry("900x700")
        self.root.minsize(850, 650)
        
        # Configuration
        self.config = BuildConfig()
        self.load_config()
        
        # Variables
        self._init_variables()
        
        # Build UI
        self._build_ui()
        
        # Check Nuitka availability
        self._check_nuitka()
        
        # Build thread
        self.build_thread = None
        self.is_building = False
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _init_variables(self):
        """Initialize tkinter variables"""
        self.script_var = tk.StringVar(value=self.config.script_path)
        self.output_var = tk.StringVar(value=self.config.output_dir)
        self.exe_name_var = tk.StringVar(value=self.config.exe_name)
        self.icon_var = tk.StringVar(value=self.config.icon_file)
        self.extra_args_var = tk.StringVar(value=self.config.extra_args)
        
        # Flags
        self.onefile_var = tk.BooleanVar(value=self.config.onefile)
        self.standalone_var = tk.BooleanVar(value=self.config.standalone)
        self.no_console_var = tk.BooleanVar(value=self.config.no_console)
        self.lto_var = tk.BooleanVar(value=self.config.lto)
        self.follow_imports_var = tk.BooleanVar(value=self.config.follow_imports)
        self.nofollow_imports_var = tk.BooleanVar(value=self.config.nofollow_imports)
        self.show_progress_var = tk.BooleanVar(value=self.config.show_progress)
        self.remove_output_var = tk.BooleanVar(value=self.config.remove_output)
    
    def _build_ui(self):
        """Build the main user interface"""
        # Create main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Create notebook for organized layout
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True)
        
        # Basic settings tab
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="Basic Settings")
        self._build_basic_tab(basic_frame)
        
        # Advanced settings tab
        advanced_frame = ttk.Frame(notebook)
        notebook.add(advanced_frame, text="Build Options")
        self._build_advanced_tab(advanced_frame)
        
        # Build log tab
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="Build Log")
        self._build_log_tab(log_frame)
        
        # Status bar
        self._build_status_bar(main_frame)
    
    def _build_basic_tab(self, parent):
        """Build basic settings tab"""
        # Script selection
        script_frame = ttk.LabelFrame(parent, text="Python Script", padding="5")
        script_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Entry(script_frame, textvariable=self.script_var).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(script_frame, text="Browse...", command=self._browse_script).pack(side="right")
        
        # Output configuration
        output_frame = ttk.LabelFrame(parent, text="Output Configuration", padding="5")
        output_frame.pack(fill="x", pady=(0, 10))
        
        # Output directory
        ttk.Label(output_frame, text="Output Directory:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        dir_frame = ttk.Frame(output_frame)
        dir_frame.grid(row=0, column=1, columnspan=2, sticky="ew", padx=(10, 0), pady=(0, 5))
        ttk.Entry(dir_frame, textvariable=self.output_var).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(dir_frame, text="Browse...", command=self._browse_output).pack(side="right")
        
        # Executable name
        ttk.Label(output_frame, text="Executable Name:").grid(row=1, column=0, sticky="w")
        ttk.Entry(output_frame, textvariable=self.exe_name_var, width=25).grid(row=1, column=1, sticky="w", padx=(10, 0))
        
        output_frame.columnconfigure(1, weight=1)
        
        # Icon selection
        icon_frame = ttk.LabelFrame(parent, text="Application Icon (Optional)", padding="5")
        icon_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Entry(icon_frame, textvariable=self.icon_var).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(icon_frame, text="Browse...", command=self._browse_icon).pack(side="right")
        
        # Data files
        data_frame = ttk.LabelFrame(parent, text="Include Data Files", padding="5")
        data_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        ttk.Label(data_frame, text="One per line: source_pattern=destination_path").pack(anchor="w", pady=(0, 5))
        
        self.data_text = tk.Text(data_frame, height=6, wrap="none")
        data_scroll = ttk.Scrollbar(data_frame, orient="vertical", command=self.data_text.yview)
        self.data_text.configure(yscrollcommand=data_scroll.set)
        
        self.data_text.pack(side="left", fill="both", expand=True)
        data_scroll.pack(side="right", fill="y")
        
        # Load data files
        self.data_text.insert("1.0", "\n".join(self.config.data_files))
        
        # Build buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=(10, 0))
        
        self.build_btn = ttk.Button(button_frame, text="🔨 Build Executable", command=self._start_build)
        self.build_btn.pack(side="left", padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="⏹ Stop Build", command=self._stop_build, state="disabled")
        self.stop_btn.pack(side="left", padx=(0, 10))
        
        ttk.Button(button_frame, text="⚙ Advanced Options", command=self._show_advanced_options).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="💾 Save Profile", command=self._save_config).pack(side="left")
    
    def _build_advanced_tab(self, parent):
        """Build advanced settings tab"""
        # Core options
        core_frame = ttk.LabelFrame(parent, text="Core Build Options", padding="5")
        core_frame.pack(fill="x", pady=(0, 10))
        
        # First row
        row1 = ttk.Frame(core_frame)
        row1.pack(fill="x", pady=(0, 5))
        ttk.Checkbutton(row1, text="One File", variable=self.onefile_var).pack(side="left", padx=(0, 20))
        ttk.Checkbutton(row1, text="Standalone", variable=self.standalone_var).pack(side="left", padx=(0, 20))
        ttk.Checkbutton(row1, text="Hide Console (Windows)", variable=self.no_console_var).pack(side="left")
        
        # Second row
        row2 = ttk.Frame(core_frame)
        row2.pack(fill="x", pady=(0, 5))
        ttk.Checkbutton(row2, text="LTO Optimization", variable=self.lto_var).pack(side="left", padx=(0, 20))
        ttk.Checkbutton(row2, text="Show Progress", variable=self.show_progress_var).pack(side="left", padx=(0, 20))
        ttk.Checkbutton(row2, text="Remove Output", variable=self.remove_output_var).pack(side="left")
        
        # Import options
        import_frame = ttk.LabelFrame(parent, text="Import Handling", padding="5")
        import_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Checkbutton(import_frame, text="Follow Imports", variable=self.follow_imports_var,
                       command=self._sync_import_flags).pack(side="left", padx=(0, 20))
        ttk.Checkbutton(import_frame, text="No Follow Imports", variable=self.nofollow_imports_var,
                       command=self._sync_import_flags).pack(side="left")
        
        # Extra arguments
        extra_frame = ttk.LabelFrame(parent, text="Extra Nuitka Arguments", padding="5")
        extra_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Entry(extra_frame, textvariable=self.extra_args_var).pack(fill="x")
        ttk.Label(extra_frame, text="Additional command-line arguments for Nuitka", 
                 font=("TkDefaultFont", 8)).pack(anchor="w", pady=(2, 0))
        
        # Help section
        help_frame = ttk.LabelFrame(parent, text="Help & Documentation", padding="5")
        help_frame.pack(fill="x")
        
        help_buttons = ttk.Frame(help_frame)
        help_buttons.pack(fill="x")
        
        ttk.Button(help_buttons, text="📖 Nuitka Manual", 
                  command=lambda: webbrowser.open("https://nuitka.net/doc/user-manual.html")).pack(side="left", padx=(0, 10))
        ttk.Button(help_buttons, text="🔧 Troubleshooting", 
                  command=self._show_troubleshooting).pack(side="left", padx=(0, 10))
        ttk.Button(help_buttons, text="ℹ About", command=self._show_about).pack(side="left")
    
    def _build_log_tab(self, parent):
        """Build log tab"""
        self.log_widget = LogWidget(parent)
        self.log_widget.pack(fill="both", expand=True, pady=(0, 10))
        
        # Log controls
        log_controls = ttk.Frame(parent)
        log_controls.pack(fill="x")
        
        ttk.Button(log_controls, text="Clear Log", command=self.log_widget.clear).pack(side="left", padx=(0, 10))
        ttk.Button(log_controls, text="Save Log", command=self._save_log).pack(side="left", padx=(0, 10))
        ttk.Button(log_controls, text="📁 Open Output Folder", command=self._open_output_folder).pack(side="left")
    
    def _build_status_bar(self, parent):
        """Build status bar"""
        self.status_frame = ttk.Frame(parent)
        self.status_frame.pack(fill="x", pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var)
        self.status_label.pack(side="left")
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.status_frame, variable=self.progress_var, length=200)
        self.progress_bar.pack(side="right", padx=(10, 0))
    
    def _sync_import_flags(self):
        """Keep import flags mutually exclusive"""
        if self.follow_imports_var.get() and self.nofollow_imports_var.get():
            # If both are set, prefer the last one clicked
            caller = self.root.focus_get()
            if "nofollow" in str(caller):
                self.follow_imports_var.set(False)
            else:
                self.nofollow_imports_var.set(False)
    
    def _browse_script(self):
        """Browse for Python script"""
        filename = filedialog.askopenfilename(
            title="Select Python Script",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
            initialdir=Path(self.script_var.get()).parent if self.script_var.get() else Path.cwd()
        )
        if filename:
            self.script_var.set(filename)
            # Auto-suggest executable name
            suggested_name = Path(filename).stem
            if not self.exe_name_var.get() or self.exe_name_var.get() == DEFAULT_EXE_NAME:
                self.exe_name_var.set(suggested_name)
    
    def _browse_output(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_var.get()
        )
        if directory:
            self.output_var.set(directory)
    
    def _browse_icon(self):
        """Browse for application icon"""
        filetypes = []
        if IS_WINDOWS:
            filetypes = [("Icon files", "*.ico"), ("All files", "*.*")]
        elif IS_MAC:
            filetypes = [("Icon files", "*.icns"), ("All files", "*.*")]
        else:
            filetypes = [("Icon files", "*.ico *.icns *.png"), ("All files", "*.*")]
        
        filename = filedialog.askopenfilename(
            title="Select Application Icon",
            filetypes=filetypes
        )
        if filename:
            self.icon_var.set(filename)
    
    def _show_advanced_options(self):
        """Show advanced options dialog"""
        dialog = AdvancedOptionsDialog(self.root, self.config)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.config.from_dict(dialog.result)
            self.log_widget.log("Advanced options updated")
    
    def _update_config_from_ui(self):
        """Update configuration from UI elements"""
        self.config.script_path = self.script_var.get()
        self.config.output_dir = self.output_var.get()
        self.config.exe_name = self.exe_name_var.get()
        self.config.icon_file = self.icon_var.get()
        self.config.extra_args = self.extra_args_var.get()
        
        # Data files
        data_content = self.data_text.get("1.0", "end").strip()
        self.config.data_files = [line.strip() for line in data_content.splitlines() if line.strip()]
        
        # Flags
        self.config.onefile = self.onefile_var.get()
        self.config.standalone = self.standalone_var.get()
        self.config.no_console = self.no_console_var.get()
        self.config.lto = self.lto_var.get()
        self.config.follow_imports = self.follow_imports_var.get()
        self.config.nofollow_imports = self.nofollow_imports_var.get()
        self.config.show_progress = self.show_progress_var.get()
        self.config.remove_output = self.remove_output_var.get()
    
    def _validate_build_config(self) -> tuple[bool, str]:
        """Validate build configuration"""
        if not self.config.script_path:
            return False, "Please select a Python script"
        
        script_path = Path(self.config.script_path)
        if not script_path.exists():
            return False, f"Script file not found: {script_path}"
        
        if script_path.suffix.lower() != ".py":
            return False, "Selected file is not a Python script (.py)"
        
        if not self.config.output_dir:
            return False, "Please specify an output directory"
        
        if not self.config.exe_name:
            return False, "Please specify an executable name"
        
        # Validate data files
        for data_spec in self.config.data_files:
            if "=" not in data_spec:
                return False, f"Invalid data file specification: {data_spec}\nUse format: source=destination"
        
        return True, "Configuration valid"
    
    def _start_build(self):
        """Start the build process"""
        if self.is_building:
            return
        
        # Update config from UI
        self._update_config_from_ui()
        
        # Validate configuration
        valid, message = self._validate_build_config()
        if not valid:
            messagebox.showerror("Configuration Error", message)
            return
        
        # Check Nuitka
        nuitka_ok, nuitka_msg = NuitkaRunner.check_nuitka()
        if not nuitka_ok:
            messagebox.showerror("Nuitka Error", f"Nuitka is not available:\n{nuitka_msg}")
            return
        
        # Start build in separate thread
        self.is_building = True
        self.build_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.progress_var.set(0)
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        self.status_var.set("Building...")
        
        self.log_widget.clear()
        self.log_widget.log("Starting build process...")
        self.log_widget.log(f"Nuitka status: {nuitka_msg}")
        
        # Start build thread
        self.build_thread = threading.Thread(target=self._build_worker, daemon=True)
        self.build_thread.start()
    
    def _build_worker(self):
        """Worker thread for building"""
        try:
            # Generate command
            cmd = NuitkaRunner.build_command(self.config)
            self.log_widget.log(f"Command: {' '.join(cmd)}")
            
            # Create output directory
            output_dir = Path(self.config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Run Nuitka
            process = subprocess.Popen(
                cmd,
                cwd=str(output_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read output
            for line in process.stdout:
                if not self.is_building:  # Check for cancellation
                    process.terminate()
                    break
                self.log_widget.log(line.rstrip())
            
            # Wait for completion
            return_code = process.wait()
            
            if return_code == 0 and self.is_building:
                self._build_completed_successfully()
            elif self.is_building:
                self._build_failed(f"Build failed with exit code {return_code}")
            else:
                self.log_widget.log("Build cancelled by user")
                
        except Exception as e:
            self._build_failed(f"Build error: {e}")
        finally:
            self._build_finished()
    
    def _build_completed_successfully(self):
        """Handle successful build completion"""
        self.log_widget.log("Build completed successfully!", "SUCCESS")
        
        # Try to find the output executable
        output_dir = Path(self.config.output_dir)
        exe_name = self.config.exe_name
        if IS_WINDOWS and not exe_name.lower().endswith(".exe"):
            exe_name += ".exe"
        
        possible_paths = [
            output_dir / exe_name,
            output_dir / f"{Path(exe_name).stem}.dist" / exe_name,
        ]
        
        output_exe = None
        for path in possible_paths:
            if path.exists():
                output_exe = path
                break
        
        if output_exe:
            self.log_widget.log(f"Executable created: {output_exe}")
            
            # Ask to open output folder
            if messagebox.askyesno("Build Complete", 
                                 f"Build completed successfully!\n\nExecutable: {output_exe.name}\n\nOpen output folder?"):
                self._open_output_folder()
        else:
            self.log_widget.log("Build completed but executable location unknown")
    
    def _build_failed(self, error_msg: str):
        """Handle build failure"""
        self.log_widget.log(error_msg, "ERROR")
        messagebox.showerror("Build Failed", error_msg)
    
    def _build_finished(self):
        """Clean up after build completion"""
        self.is_building = False
        self.build_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_var.set(0)
        self.status_var.set("Ready")
    
    def _stop_build(self):
        """Stop the current build"""
        if self.is_building:
            self.is_building = False
            self.log_widget.log("Stopping build...", "WARNING")
    
    def _open_output_folder(self):
        """Open the output folder in file manager"""
        output_dir = Path(self.config.output_dir)
        try:
            if IS_WINDOWS:
                subprocess.Popen(["explorer", str(output_dir)])
            elif IS_MAC:
                subprocess.Popen(["open", str(output_dir)])
            else:
                subprocess.Popen(["xdg-open", str(output_dir)])
        except Exception as e:
            self.log_widget.log(f"Could not open output folder: {e}", "WARNING")
    
    def _save_log(self):
        """Save build log to file"""
        filename = filedialog.asksaveasfilename(
            title="Save Build Log",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                log_content = self.log_widget.text.get("1.0", "end")
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(log_content)
                self.log_widget.log(f"Log saved to: {filename}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save log: {e}")
    
    def _check_nuitka(self):
        """Check Nuitka installation status"""
        available, message = NuitkaRunner.check_nuitka()
        if available:
            self.status_var.set(f"Ready - {message}")
        else:
            self.status_var.set(f"Nuitka not available - {message}")
            self.build_btn.configure(state="disabled")
    
    def _save_config(self):
        """Save current configuration to file"""
        try:
            self._update_config_from_ui()
            config_data = self.config.to_dict()
            
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
            
            self.log_widget.log(f"Configuration saved to: {CONFIG_FILE}")
            messagebox.showinfo("Configuration Saved", f"Settings saved to:\n{CONFIG_FILE}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save configuration: {e}")
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                self.config.from_dict(config_data)
        except Exception as e:
            # If config loading fails, use defaults
            pass
    
    def _show_troubleshooting(self):
        """Show troubleshooting information"""
        info = """
Troubleshooting Common Issues:

1. Nuitka not found:
   • Install Nuitka: pip install nuitka
   • Or with pipx: pipx install nuitka
   • Ensure Python Scripts directory is in PATH

2. Build errors:
   • Check Python version compatibility
   • Install platform build tools (Visual Studio, Xcode, gcc)
   • Try disabling LTO optimization
   • Check for missing dependencies

3. Runtime errors:
   • Use --standalone mode for distribution
   • Include required data files
   • Check for path-dependent code

4. Large executable size:
   • Disable --follow-imports for smaller size
   • Use specific --include-module instead
   • Consider using --onefile=no

5. Windows antivirus issues:
   • Add output folder to antivirus exceptions
   • Build with debug info: --debug
        """
        
        # Create info window
        info_window = tk.Toplevel(self.root)
        info_window.title("Troubleshooting Guide")
        info_window.geometry("600x500")
        info_window.transient(self.root)
        
        text_widget = tk.Text(info_window, wrap="word", padx=10, pady=10)
        scrollbar = ttk.Scrollbar(info_window, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        text_widget.insert("1.0", info)
        text_widget.configure(state="disabled")
    
    def _show_about(self):
        """Show about dialog"""
        about_text = f"""
{APP_TITLE} v{APP_VERSION}

A comprehensive GUI for the Nuitka Python compiler.

Features:
• Cross-platform executable generation
• Advanced configuration options
• Real-time build logging
• Profile management
• Error handling and validation

Platform: {platform.system()} {platform.release()}
Python: {platform.python_version()}

© 2024 - Enhanced Nuitka GUI
        """.strip()
        
        messagebox.showinfo("About", about_text)
    
    def _on_closing(self):
        """Handle application closing"""
        if self.is_building:
            if messagebox.askokcancel("Build in Progress", 
                                    "A build is currently in progress. Do you want to stop it and exit?"):
                self.is_building = False
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """Start the application"""
        try:
            # Set DPI awareness on Windows
            if IS_WINDOWS:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
        
        self.root.mainloop()

def main():
    """Main entry point"""
    app = MainApplication()
    app.run()

if __name__ == "__main__":
    main()