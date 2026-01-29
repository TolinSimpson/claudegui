#!/usr/bin/env python3
"""
Claude CLI Configuration GUI

A Tkinter-based GUI for configuring and launching Claude CLI sessions.
Runs on Windows, macOS, and Linux.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import shutil
import os
import sys
import shlex
import tempfile
import stat


class ClaudeGUI:
    """Main application class for Claude CLI GUI."""

    def __init__(self, root):
        self.root = root
        self.root.title("Claude CLI Configuration")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)

        # Initialize all variables
        self._init_variables()

        # Create main layout
        self._create_layout()

        # Update command preview initially
        self._update_command_preview()

    def _get_safe_working_dir(self):
        """Return a safe default working directory, avoiding system paths."""
        cwd = os.getcwd()
        if sys.platform == "win32":
            cwd_lower = cwd.lower()
            # Avoid Windows system directories (e.g. when launched as admin)
            if "system32" in cwd_lower or "syswow64" in cwd_lower or cwd == os.path.splitdrive(cwd)[0] + os.sep:
                return os.path.expanduser("~")
        else:
            # On Unix, avoid root (e.g. when launched from system context)
            if cwd == "/":
                return os.path.expanduser("~")
        return cwd

    def _find_claude_path(self):
        """Find the Claude CLI executable path."""
        # First try PATH
        claude_path = shutil.which("claude")
        if claude_path:
            return claude_path

        # Try common locations per platform
        if sys.platform == "win32":
            possible_paths = [
                os.path.expanduser(r"~\.local\bin\claude.exe"),
                os.path.expanduser(r"~\.local\bin\claude"),
                os.path.expanduser(r"~\AppData\Local\Programs\claude\claude.exe"),
                os.path.expanduser(r"~\AppData\Roaming\npm\claude.cmd"),
            ]
        else:
            possible_paths = [
                os.path.expanduser("~/.local/bin/claude"),
                "/usr/local/bin/claude",
                "/opt/homebrew/bin/claude",
                os.path.expanduser("~/.nvm/current/bin/claude"),
            ]
        for p in possible_paths:
            if os.path.exists(p):
                return p

        # Default fallback (rely on PATH when launched)
        return "claude"

    def _init_variables(self):
        """Initialize all Tkinter variables."""
        # Claude CLI path
        self.claude_path_var = tk.StringVar(value=self._find_claude_path())

        # Core tab
        self.prompt_var = tk.StringVar()
        self.model_var = tk.StringVar(value="opus")
        self.fallback_model_var = tk.StringVar()
        self.continue_var = tk.BooleanVar()
        self.resume_var = tk.StringVar()
        self.fork_session_var = tk.BooleanVar()
        self.session_id_var = tk.StringVar()

        # Agent tab
        self.agent_var = tk.StringVar()
        # agents_json uses Text widget, no StringVar

        # Tools tab
        self.allowed_tools_var = tk.StringVar()
        self.disallowed_tools_var = tk.StringVar()
        self.disable_slash_commands_var = tk.BooleanVar()
        # tools uses Text widget

        # I/O tab
        self.print_mode_var = tk.BooleanVar()
        self.input_format_var = tk.StringVar(value="text")
        self.output_format_var = tk.StringVar(value="text")
        self.include_partial_var = tk.BooleanVar()
        self.replay_user_var = tk.BooleanVar()
        # json_schema uses Text widget

        # MCP tab
        self.mcp_config_var = tk.StringVar()
        self.strict_mcp_var = tk.BooleanVar()
        self.plugin_dirs = []

        # Advanced tab
        self.permission_mode_var = tk.StringVar(value="default")
        self.allow_skip_perms_var = tk.BooleanVar()
        self.skip_perms_var = tk.BooleanVar()
        self.add_dirs = []
        self.file_specs_var = tk.StringVar()
        self.max_budget_var = tk.StringVar()
        self.debug_var = tk.StringVar()
        self.debug_file_var = tk.StringVar()
        self.verbose_var = tk.BooleanVar()
        self.chrome_var = tk.StringVar(value="default")
        self.ide_var = tk.BooleanVar()
        self.settings_var = tk.StringVar()
        self.setting_user_var = tk.BooleanVar()
        self.setting_project_var = tk.BooleanVar()
        self.setting_local_var = tk.BooleanVar()
        self.betas_var = tk.StringVar()
        self.no_session_persistence_var = tk.BooleanVar()

        # Working directory (avoid defaulting to system paths like System32)
        self.working_dir_var = tk.StringVar(value=self._get_safe_working_dir())

    def _create_layout(self):
        """Create the main layout with notebook and bottom panel."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Working directory frame at top
        self._create_working_dir_frame(main_frame)

        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # Create all tabs
        self._create_core_tab()
        self._create_agent_tab()
        self._create_tools_tab()
        self._create_prompts_tab()
        self._create_io_tab()
        self._create_mcp_tab()
        self._create_advanced_tab()

        # Bottom panel with command preview and buttons
        self._create_bottom_panel(main_frame)

    def _create_working_dir_frame(self, parent):
        """Create working directory and Claude path selection frame."""
        # Claude CLI Path
        claude_frame = ttk.LabelFrame(parent, text="Claude CLI Path", padding="5")
        claude_frame.pack(fill=tk.X, pady=(0, 5))

        claude_entry = ttk.Entry(claude_frame, textvariable=self.claude_path_var)
        claude_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        claude_entry.bind("<KeyRelease>", lambda e: self._update_command_preview())

        ttk.Button(claude_frame, text="Browse...", command=self._browse_claude_path).pack(side=tk.RIGHT, padx=(0, 5))
        ttk.Button(claude_frame, text="Auto-detect", command=self._autodetect_claude_path).pack(side=tk.RIGHT)

        # Working Directory
        frame = ttk.LabelFrame(parent, text="Working Directory", padding="5")
        frame.pack(fill=tk.X, pady=(0, 5))

        entry = ttk.Entry(frame, textvariable=self.working_dir_var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        entry.bind("<KeyRelease>", lambda e: self._update_command_preview())

        btn = ttk.Button(frame, text="Browse...", command=self._browse_working_dir)
        btn.pack(side=tk.RIGHT)

    def _browse_claude_path(self):
        """Browse for Claude CLI executable."""
        if sys.platform == "win32":
            filetypes = [("Executable files", "*.exe *.cmd *.bat"), ("All files", "*.*")]
        else:
            filetypes = [("Executable", "*"), ("All files", "*")]
        path = filedialog.askopenfilename(
            title="Select Claude CLI Executable",
            filetypes=filetypes
        )
        if path:
            self.claude_path_var.set(path)
            self._update_command_preview()

    def _autodetect_claude_path(self):
        """Auto-detect Claude CLI path."""
        path = self._find_claude_path()
        self.claude_path_var.set(path)
        self._update_command_preview()
        if path == "claude":
            messagebox.showwarning(
                "Not Found",
                "Could not auto-detect Claude CLI path.\n\n"
                "Please browse to select the claude executable manually,\n"
                "or ensure it's installed and in your PATH."
            )
        else:
            messagebox.showinfo("Found", f"Claude CLI found at:\n{path}")

    def _browse_working_dir(self):
        """Browse for working directory."""
        path = filedialog.askdirectory(initialdir=self.working_dir_var.get())
        if path:
            self.working_dir_var.set(path)
            self._update_command_preview()

    def _create_core_tab(self):
        """Create the Core tab with prompt, model, and session controls."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Core")

        # Prompt
        ttk.Label(tab, text="Prompt (optional):").pack(anchor=tk.W)
        prompt_entry = ttk.Entry(tab, textvariable=self.prompt_var, width=80)
        prompt_entry.pack(fill=tk.X, pady=(0, 10))
        prompt_entry.bind("<KeyRelease>", lambda e: self._update_command_preview())

        # Model frame
        model_frame = ttk.Frame(tab)
        model_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(model_frame, text="Model:").pack(side=tk.LEFT)
        model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=["", "sonnet", "opus", "claude-sonnet-4-5-20250929", "claude-opus-4-20250514"],
            width=35
        )
        model_combo.pack(side=tk.LEFT, padx=(5, 20))
        model_combo.bind("<<ComboboxSelected>>", lambda e: self._update_command_preview())
        model_combo.bind("<KeyRelease>", lambda e: self._update_command_preview())

        ttk.Label(model_frame, text="Fallback Model:").pack(side=tk.LEFT)
        fallback_entry = ttk.Entry(model_frame, textvariable=self.fallback_model_var, width=25)
        fallback_entry.pack(side=tk.LEFT, padx=5)
        fallback_entry.bind("<KeyRelease>", lambda e: self._update_command_preview())

        # Session controls
        session_frame = ttk.LabelFrame(tab, text="Session Controls", padding="10")
        session_frame.pack(fill=tk.X, pady=(0, 10))

        row1 = ttk.Frame(session_frame)
        row1.pack(fill=tk.X, pady=(0, 5))

        ttk.Checkbutton(
            row1, text="Continue (-c)", variable=self.continue_var,
            command=self._update_command_preview
        ).pack(side=tk.LEFT, padx=(0, 20))

        ttk.Checkbutton(
            row1, text="Fork Session", variable=self.fork_session_var,
            command=self._update_command_preview
        ).pack(side=tk.LEFT)

        row2 = ttk.Frame(session_frame)
        row2.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(row2, text="Resume (-r):").pack(side=tk.LEFT)
        resume_entry = ttk.Entry(row2, textvariable=self.resume_var, width=40)
        resume_entry.pack(side=tk.LEFT, padx=5)
        resume_entry.bind("<KeyRelease>", lambda e: self._update_command_preview())

        row3 = ttk.Frame(session_frame)
        row3.pack(fill=tk.X)

        ttk.Label(row3, text="Session ID:").pack(side=tk.LEFT)
        session_entry = ttk.Entry(row3, textvariable=self.session_id_var, width=40)
        session_entry.pack(side=tk.LEFT, padx=5)
        session_entry.bind("<KeyRelease>", lambda e: self._update_command_preview())

    def _create_agent_tab(self):
        """Create the Agent tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Agent")

        # Agent name
        ttk.Label(tab, text="Agent:").pack(anchor=tk.W)
        agent_entry = ttk.Entry(tab, textvariable=self.agent_var, width=50)
        agent_entry.pack(fill=tk.X, pady=(0, 10))
        agent_entry.bind("<KeyRelease>", lambda e: self._update_command_preview())

        # Agents JSON
        ttk.Label(tab, text="Agents JSON (custom agents definition):").pack(anchor=tk.W)
        self.agents_json_text = scrolledtext.ScrolledText(tab, height=15, width=80)
        self.agents_json_text.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.agents_json_text.bind("<KeyRelease>", lambda e: self._update_command_preview())

        ttk.Label(
            tab,
            text='Example: {"reviewer": {"description": "Reviews code", "prompt": "You are a code reviewer"}}',
            foreground="gray"
        ).pack(anchor=tk.W)

    def _create_tools_tab(self):
        """Create the Tools tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Tools")

        # Tools
        ttk.Label(tab, text="Tools (space or comma separated):").pack(anchor=tk.W)
        self.tools_text = scrolledtext.ScrolledText(tab, height=5, width=80)
        self.tools_text.pack(fill=tk.X, pady=(0, 10))
        self.tools_text.bind("<KeyRelease>", lambda e: self._update_command_preview())
        ttk.Label(
            tab,
            text='Use "" to disable all, "default" for all, or list: "Bash,Edit,Read"',
            foreground="gray"
        ).pack(anchor=tk.W, pady=(0, 10))

        # Allowed tools
        ttk.Label(tab, text="Allowed Tools (--allowedTools):").pack(anchor=tk.W)
        allowed_entry = ttk.Entry(tab, textvariable=self.allowed_tools_var, width=60)
        allowed_entry.pack(fill=tk.X, pady=(0, 10))
        allowed_entry.bind("<KeyRelease>", lambda e: self._update_command_preview())
        ttk.Label(tab, text='Example: "Bash(git:*) Edit"', foreground="gray").pack(anchor=tk.W, pady=(0, 10))

        # Disallowed tools
        ttk.Label(tab, text="Disallowed Tools (--disallowedTools):").pack(anchor=tk.W)
        disallowed_entry = ttk.Entry(tab, textvariable=self.disallowed_tools_var, width=60)
        disallowed_entry.pack(fill=tk.X, pady=(0, 10))
        disallowed_entry.bind("<KeyRelease>", lambda e: self._update_command_preview())

        # Disable slash commands
        ttk.Checkbutton(
            tab, text="Disable Slash Commands", variable=self.disable_slash_commands_var,
            command=self._update_command_preview
        ).pack(anchor=tk.W)

    def _create_prompts_tab(self):
        """Create the Prompts tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Prompts")

        # System prompt
        ttk.Label(tab, text="System Prompt (--system-prompt):").pack(anchor=tk.W)
        self.system_prompt_text = scrolledtext.ScrolledText(tab, height=10, width=80)
        self.system_prompt_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.system_prompt_text.bind("<KeyRelease>", lambda e: self._update_command_preview())

        # Append system prompt
        ttk.Label(tab, text="Append System Prompt (--append-system-prompt):").pack(anchor=tk.W)
        self.append_prompt_text = scrolledtext.ScrolledText(tab, height=10, width=80)
        self.append_prompt_text.pack(fill=tk.BOTH, expand=True)
        self.append_prompt_text.bind("<KeyRelease>", lambda e: self._update_command_preview())

    def _create_io_tab(self):
        """Create the Input/Output tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Input/Output")

        # Print mode
        ttk.Checkbutton(
            tab, text="Print Mode (-p) - Non-interactive output", variable=self.print_mode_var,
            command=self._update_command_preview
        ).pack(anchor=tk.W, pady=(0, 10))

        # Formats frame
        formats_frame = ttk.Frame(tab)
        formats_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(formats_frame, text="Input Format:").pack(side=tk.LEFT)
        input_combo = ttk.Combobox(
            formats_frame, textvariable=self.input_format_var,
            values=["text", "stream-json"], width=15, state="readonly"
        )
        input_combo.pack(side=tk.LEFT, padx=(5, 20))
        input_combo.bind("<<ComboboxSelected>>", lambda e: self._update_command_preview())

        ttk.Label(formats_frame, text="Output Format:").pack(side=tk.LEFT)
        output_combo = ttk.Combobox(
            formats_frame, textvariable=self.output_format_var,
            values=["text", "json", "stream-json"], width=15, state="readonly"
        )
        output_combo.pack(side=tk.LEFT, padx=5)
        output_combo.bind("<<ComboboxSelected>>", lambda e: self._update_command_preview())

        # JSON Schema
        ttk.Label(tab, text="JSON Schema (--json-schema):").pack(anchor=tk.W)
        self.json_schema_text = scrolledtext.ScrolledText(tab, height=8, width=80)
        self.json_schema_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.json_schema_text.bind("<KeyRelease>", lambda e: self._update_command_preview())
        ttk.Label(
            tab,
            text='Example: {"type":"object","properties":{"name":{"type":"string"}},"required":["name"]}',
            foreground="gray"
        ).pack(anchor=tk.W, pady=(0, 10))

        # Checkboxes
        ttk.Checkbutton(
            tab, text="Include Partial Messages", variable=self.include_partial_var,
            command=self._update_command_preview
        ).pack(anchor=tk.W)

        ttk.Checkbutton(
            tab, text="Replay User Messages", variable=self.replay_user_var,
            command=self._update_command_preview
        ).pack(anchor=tk.W)

    def _create_mcp_tab(self):
        """Create the MCP & Plugins tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="MCP & Plugins")

        # MCP Config
        mcp_frame = ttk.Frame(tab)
        mcp_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(mcp_frame, text="MCP Config (--mcp-config):").pack(side=tk.LEFT)
        mcp_entry = ttk.Entry(mcp_frame, textvariable=self.mcp_config_var, width=50)
        mcp_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        mcp_entry.bind("<KeyRelease>", lambda e: self._update_command_preview())

        ttk.Button(mcp_frame, text="Browse...", command=self._browse_mcp_config).pack(side=tk.RIGHT)

        ttk.Checkbutton(
            tab, text="Strict MCP Config (only use servers from --mcp-config)",
            variable=self.strict_mcp_var, command=self._update_command_preview
        ).pack(anchor=tk.W, pady=(0, 15))

        # Plugin directories
        ttk.Label(tab, text="Plugin Directories (--plugin-dir):").pack(anchor=tk.W)

        plugin_frame = ttk.Frame(tab)
        plugin_frame.pack(fill=tk.BOTH, expand=True)

        self.plugin_listbox = tk.Listbox(plugin_frame, height=8)
        self.plugin_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(plugin_frame, orient=tk.VERTICAL, command=self.plugin_listbox.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.plugin_listbox.config(yscrollcommand=scrollbar.set)

        btn_frame = ttk.Frame(plugin_frame)
        btn_frame.pack(side=tk.LEFT, padx=10)

        ttk.Button(btn_frame, text="Add...", command=self._add_plugin_dir).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Remove", command=self._remove_plugin_dir).pack(fill=tk.X, pady=2)

    def _browse_mcp_config(self):
        """Browse for MCP config file."""
        path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if path:
            self.mcp_config_var.set(path)
            self._update_command_preview()

    def _add_plugin_dir(self):
        """Add a plugin directory."""
        path = filedialog.askdirectory()
        if path and path not in self.plugin_dirs:
            self.plugin_dirs.append(path)
            self.plugin_listbox.insert(tk.END, path)
            self._update_command_preview()

    def _remove_plugin_dir(self):
        """Remove selected plugin directory."""
        selection = self.plugin_listbox.curselection()
        if selection:
            idx = selection[0]
            self.plugin_listbox.delete(idx)
            del self.plugin_dirs[idx]
            self._update_command_preview()

    def _create_advanced_tab(self):
        """Create the Advanced tab."""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Advanced")

        # Create a canvas with scrollbar for the advanced tab
        canvas = tk.Canvas(tab)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        content = scrollable_frame

        # Permission Mode
        perm_frame = ttk.LabelFrame(content, text="Permissions", padding="10")
        perm_frame.pack(fill=tk.X, pady=(0, 10))

        row1 = ttk.Frame(perm_frame)
        row1.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(row1, text="Permission Mode:").pack(side=tk.LEFT)
        perm_combo = ttk.Combobox(
            row1, textvariable=self.permission_mode_var,
            values=["default", "acceptEdits", "bypassPermissions", "delegate", "dontAsk", "plan"],
            width=20, state="readonly"
        )
        perm_combo.pack(side=tk.LEFT, padx=5)
        perm_combo.bind("<<ComboboxSelected>>", lambda e: self._update_command_preview())

        ttk.Checkbutton(
            perm_frame, text="Allow Dangerously Skip Permissions",
            variable=self.allow_skip_perms_var, command=self._update_command_preview
        ).pack(anchor=tk.W)

        ttk.Checkbutton(
            perm_frame, text="Dangerously Skip Permissions (bypass all checks)",
            variable=self.skip_perms_var, command=self._update_command_preview
        ).pack(anchor=tk.W)

        # Additional Directories
        dir_frame = ttk.LabelFrame(content, text="Additional Directories (--add-dir)", padding="10")
        dir_frame.pack(fill=tk.X, pady=(0, 10))

        dir_list_frame = ttk.Frame(dir_frame)
        dir_list_frame.pack(fill=tk.X)

        self.add_dir_listbox = tk.Listbox(dir_list_frame, height=4)
        self.add_dir_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)

        dir_btn_frame = ttk.Frame(dir_list_frame)
        dir_btn_frame.pack(side=tk.LEFT, padx=5)

        ttk.Button(dir_btn_frame, text="Add", command=self._add_directory).pack(fill=tk.X, pady=1)
        ttk.Button(dir_btn_frame, text="Remove", command=self._remove_directory).pack(fill=tk.X, pady=1)

        # File specs
        file_frame = ttk.Frame(content)
        file_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(file_frame, text="File Specs (--file):").pack(side=tk.LEFT)
        file_entry = ttk.Entry(file_frame, textvariable=self.file_specs_var, width=50)
        file_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        file_entry.bind("<KeyRelease>", lambda e: self._update_command_preview())

        # Budget
        budget_frame = ttk.Frame(content)
        budget_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(budget_frame, text="Max Budget USD (--max-budget-usd):").pack(side=tk.LEFT)
        budget_entry = ttk.Entry(budget_frame, textvariable=self.max_budget_var, width=10)
        budget_entry.pack(side=tk.LEFT, padx=5)
        budget_entry.bind("<KeyRelease>", lambda e: self._update_command_preview())

        # Debug options
        debug_frame = ttk.LabelFrame(content, text="Debug Options", padding="10")
        debug_frame.pack(fill=tk.X, pady=(0, 10))

        debug_row1 = ttk.Frame(debug_frame)
        debug_row1.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(debug_row1, text="Debug Filter:").pack(side=tk.LEFT)
        debug_entry = ttk.Entry(debug_row1, textvariable=self.debug_var, width=30)
        debug_entry.pack(side=tk.LEFT, padx=5)
        debug_entry.bind("<KeyRelease>", lambda e: self._update_command_preview())

        ttk.Checkbutton(
            debug_row1, text="Verbose", variable=self.verbose_var,
            command=self._update_command_preview
        ).pack(side=tk.LEFT, padx=10)

        debug_row2 = ttk.Frame(debug_frame)
        debug_row2.pack(fill=tk.X)

        ttk.Label(debug_row2, text="Debug File:").pack(side=tk.LEFT)
        debug_file_entry = ttk.Entry(debug_row2, textvariable=self.debug_file_var, width=40)
        debug_file_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        debug_file_entry.bind("<KeyRelease>", lambda e: self._update_command_preview())

        ttk.Button(debug_row2, text="Browse...", command=self._browse_debug_file).pack(side=tk.RIGHT)

        # Chrome/IDE
        chrome_frame = ttk.LabelFrame(content, text="Chrome & IDE", padding="10")
        chrome_frame.pack(fill=tk.X, pady=(0, 10))

        chrome_row = ttk.Frame(chrome_frame)
        chrome_row.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(chrome_row, text="Chrome Integration:").pack(side=tk.LEFT)
        chrome_combo = ttk.Combobox(
            chrome_row, textvariable=self.chrome_var,
            values=["default", "enabled", "disabled"], width=15, state="readonly"
        )
        chrome_combo.pack(side=tk.LEFT, padx=5)
        chrome_combo.bind("<<ComboboxSelected>>", lambda e: self._update_command_preview())

        ttk.Checkbutton(
            chrome_frame, text="Auto-connect to IDE (--ide)", variable=self.ide_var,
            command=self._update_command_preview
        ).pack(anchor=tk.W)

        # Settings
        settings_frame = ttk.LabelFrame(content, text="Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        settings_row1 = ttk.Frame(settings_frame)
        settings_row1.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(settings_row1, text="Settings File/JSON:").pack(side=tk.LEFT)
        settings_entry = ttk.Entry(settings_row1, textvariable=self.settings_var, width=40)
        settings_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        settings_entry.bind("<KeyRelease>", lambda e: self._update_command_preview())

        ttk.Button(settings_row1, text="Browse...", command=self._browse_settings).pack(side=tk.RIGHT)

        settings_row2 = ttk.Frame(settings_frame)
        settings_row2.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(settings_row2, text="Setting Sources:").pack(side=tk.LEFT)
        ttk.Checkbutton(
            settings_row2, text="user", variable=self.setting_user_var,
            command=self._update_command_preview
        ).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(
            settings_row2, text="project", variable=self.setting_project_var,
            command=self._update_command_preview
        ).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(
            settings_row2, text="local", variable=self.setting_local_var,
            command=self._update_command_preview
        ).pack(side=tk.LEFT, padx=5)

        # Betas
        betas_row = ttk.Frame(settings_frame)
        betas_row.pack(fill=tk.X)

        ttk.Label(betas_row, text="Betas:").pack(side=tk.LEFT)
        betas_entry = ttk.Entry(betas_row, textvariable=self.betas_var, width=40)
        betas_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        betas_entry.bind("<KeyRelease>", lambda e: self._update_command_preview())

        # Session persistence
        ttk.Checkbutton(
            content, text="No Session Persistence (--no-session-persistence)",
            variable=self.no_session_persistence_var, command=self._update_command_preview
        ).pack(anchor=tk.W)

    def _add_directory(self):
        """Add an additional directory."""
        path = filedialog.askdirectory()
        if path and path not in self.add_dirs:
            self.add_dirs.append(path)
            self.add_dir_listbox.insert(tk.END, path)
            self._update_command_preview()

    def _remove_directory(self):
        """Remove selected additional directory."""
        selection = self.add_dir_listbox.curselection()
        if selection:
            idx = selection[0]
            self.add_dir_listbox.delete(idx)
            del self.add_dirs[idx]
            self._update_command_preview()

    def _browse_debug_file(self):
        """Browse for debug file."""
        path = filedialog.asksaveasfilename(defaultextension=".log")
        if path:
            self.debug_file_var.set(path)
            self._update_command_preview()

    def _browse_settings(self):
        """Browse for settings file."""
        path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if path:
            self.settings_var.set(path)
            self._update_command_preview()

    def _create_bottom_panel(self, parent):
        """Create the bottom panel with command preview and buttons."""
        bottom_frame = ttk.LabelFrame(parent, text="Command Preview", padding="10")
        bottom_frame.pack(fill=tk.X, pady=(10, 0))

        # Command preview text
        self.command_preview = scrolledtext.ScrolledText(
            bottom_frame, height=4, width=80, state=tk.DISABLED, wrap=tk.WORD
        )
        self.command_preview.pack(fill=tk.X, pady=(0, 10))

        # Buttons
        btn_frame = ttk.Frame(bottom_frame)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="Reset All", command=self._reset_all).pack(side=tk.LEFT)

        ttk.Button(btn_frame, text="Launch", command=self._launch_claude).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Copy Command", command=self._copy_command).pack(side=tk.RIGHT)

    def _quote_arg(self, arg):
        """Quote an argument for command line display (platform-aware)."""
        if not arg:
            return '""' if sys.platform == "win32" else "''"
        if sys.platform == "win32":
            # Windows: double quotes, escape "
            if ' ' in arg or '"' in arg or '\t' in arg or '\n' in arg or any(c in arg for c in '&|<>^'):
                escaped = arg.replace('"', '\\"')
                return f'"{escaped}"'
            return arg
        # Unix: use shlex.quote for shell-safe display
        return shlex.quote(arg)

    def _build_command(self):
        """Build the command list from current settings."""
        # Use configured claude path
        claude_path = self.claude_path_var.get() or "claude"
        cmd = [claude_path]

        # Model
        if self.model_var.get():
            cmd.extend(["--model", self.model_var.get()])

        # Fallback model
        if self.fallback_model_var.get():
            cmd.extend(["--fallback-model", self.fallback_model_var.get()])

        # Session controls
        if self.continue_var.get():
            cmd.append("-c")

        if self.resume_var.get():
            cmd.extend(["-r", self.resume_var.get()])

        if self.fork_session_var.get():
            cmd.append("--fork-session")

        if self.session_id_var.get():
            cmd.extend(["--session-id", self.session_id_var.get()])

        # Agent
        if self.agent_var.get():
            cmd.extend(["--agent", self.agent_var.get()])

        # Agents JSON
        agents_json = self.agents_json_text.get("1.0", tk.END).strip()
        if agents_json:
            cmd.extend(["--agents", agents_json])

        # Tools
        tools = self.tools_text.get("1.0", tk.END).strip()
        if tools:
            cmd.extend(["--tools", tools])

        # Allowed tools
        if self.allowed_tools_var.get():
            cmd.extend(["--allowedTools", self.allowed_tools_var.get()])

        # Disallowed tools
        if self.disallowed_tools_var.get():
            cmd.extend(["--disallowedTools", self.disallowed_tools_var.get()])

        # Disable slash commands
        if self.disable_slash_commands_var.get():
            cmd.append("--disable-slash-commands")

        # System prompt
        system_prompt = self.system_prompt_text.get("1.0", tk.END).strip()
        if system_prompt:
            cmd.extend(["--system-prompt", system_prompt])

        # Append system prompt
        append_prompt = self.append_prompt_text.get("1.0", tk.END).strip()
        if append_prompt:
            cmd.extend(["--append-system-prompt", append_prompt])

        # Print mode
        if self.print_mode_var.get():
            cmd.append("-p")

        # Input format
        if self.input_format_var.get() != "text":
            cmd.extend(["--input-format", self.input_format_var.get()])

        # Output format
        if self.output_format_var.get() != "text":
            cmd.extend(["--output-format", self.output_format_var.get()])

        # JSON schema
        json_schema = self.json_schema_text.get("1.0", tk.END).strip()
        if json_schema:
            cmd.extend(["--json-schema", json_schema])

        # Include partial messages
        if self.include_partial_var.get():
            cmd.append("--include-partial-messages")

        # Replay user messages
        if self.replay_user_var.get():
            cmd.append("--replay-user-messages")

        # MCP config
        if self.mcp_config_var.get():
            cmd.extend(["--mcp-config", self.mcp_config_var.get()])

        # Strict MCP config
        if self.strict_mcp_var.get():
            cmd.append("--strict-mcp-config")

        # Plugin directories
        for plugin_dir in self.plugin_dirs:
            cmd.extend(["--plugin-dir", plugin_dir])

        # Permission mode
        if self.permission_mode_var.get() != "default":
            cmd.extend(["--permission-mode", self.permission_mode_var.get()])

        # Skip permissions
        if self.allow_skip_perms_var.get():
            cmd.append("--allow-dangerously-skip-permissions")

        if self.skip_perms_var.get():
            cmd.append("--dangerously-skip-permissions")

        # Additional directories
        for add_dir in self.add_dirs:
            cmd.extend(["--add-dir", add_dir])

        # File specs
        if self.file_specs_var.get():
            cmd.extend(["--file", self.file_specs_var.get()])

        # Max budget
        if self.max_budget_var.get():
            cmd.extend(["--max-budget-usd", self.max_budget_var.get()])

        # Debug
        if self.debug_var.get():
            cmd.extend(["--debug", self.debug_var.get()])
        
        if self.debug_file_var.get():
            cmd.extend(["--debug-file", self.debug_file_var.get()])

        if self.verbose_var.get():
            cmd.append("--verbose")

        # Chrome
        if self.chrome_var.get() == "enabled":
            cmd.append("--chrome")
        elif self.chrome_var.get() == "disabled":
            cmd.append("--no-chrome")

        # IDE
        if self.ide_var.get():
            cmd.append("--ide")

        # Settings
        if self.settings_var.get():
            cmd.extend(["--settings", self.settings_var.get()])

        # Setting sources
        sources = []
        if self.setting_user_var.get():
            sources.append("user")
        if self.setting_project_var.get():
            sources.append("project")
        if self.setting_local_var.get():
            sources.append("local")
        if sources:
            cmd.extend(["--setting-sources", ",".join(sources)])

        # Betas
        if self.betas_var.get():
            cmd.extend(["--betas", self.betas_var.get()])

        # No session persistence
        if self.no_session_persistence_var.get():
            cmd.append("--no-session-persistence")

        # Prompt (must be last, as positional argument)
        if self.prompt_var.get():
            cmd.append(self.prompt_var.get())

        return cmd

    def _get_command_string(self):
        """Get the command as a display string."""
        cmd = self._build_command()
        # Build display string with proper quoting
        parts = []
        for arg in cmd:
            parts.append(self._quote_arg(arg))
        return " ".join(parts)

    def _update_command_preview(self):
        """Update the command preview text."""
        cmd_str = self._get_command_string()
        self.command_preview.config(state=tk.NORMAL)
        self.command_preview.delete("1.0", tk.END)
        self.command_preview.insert("1.0", cmd_str)
        self.command_preview.config(state=tk.DISABLED)

    def _copy_command(self):
        """Copy command to clipboard."""
        cmd_str = self._get_command_string()
        self.root.clipboard_clear()
        self.root.clipboard_append(cmd_str)
        messagebox.showinfo("Copied", "Command copied to clipboard!")

    def _launch_claude(self):
        """Launch Claude CLI with the configured options."""
        cmd = self._build_command()
        working_dir = self.working_dir_var.get().strip() or self._get_safe_working_dir()

        if not os.path.isdir(working_dir):
            messagebox.showerror("Error", f"Working directory does not exist: {working_dir}")
            return

        try:
            if sys.platform == "win32":
                # Windows: new console window
                subprocess.Popen(
                    cmd,
                    cwd=working_dir,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                # Unix: run in a new terminal so the user sees interactive output
                self._launch_claude_unix(cmd, working_dir)
            messagebox.showinfo("Launched", "Claude CLI has been launched in a new window!")
        except FileNotFoundError:
            messagebox.showerror(
                "Error",
                "Could not find Claude CLI. Make sure 'claude' is installed and in your PATH.\n\n"
                "You can install it with: npm install -g @anthropic-ai/claude-code"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Claude CLI:\n{e}")

    def _launch_claude_unix(self, cmd, working_dir):
        """Launch Claude CLI in a new terminal on Unix (macOS/Linux)."""
        fd, script_path = tempfile.mkstemp(suffix=".sh", prefix="claude_gui_")
        try:
            # Script: cd to dir, run claude, then remove self
            script_content = (
                "#!/bin/sh\n"
                "cd " + shlex.quote(working_dir) + " && "
                + " ".join(shlex.quote(a) for a in cmd) + "\n"
                "rm -f " + shlex.quote(script_path) + "\n"
            )
            os.write(fd, script_content.encode())
            os.close(fd)
            os.chmod(script_path, stat.S_IRWXU)
        except OSError:
            os.close(fd)
            try:
                os.remove(script_path)
            except OSError:
                pass
            raise

        launchers = []
        if sys.platform == "darwin":
            # macOS: use osascript so Terminal runs the script (open -a doesn't pass args well)
            script_escaped = script_path.replace("\\", "\\\\").replace('"', '\\"')
            launchers.append(["osascript", "-e", 'tell application "Terminal" to do script "sh ' + script_escaped + '"'])
        # Linux and others: try common terminal emulators
        launchers.extend([
            ["x-terminal-emulator", "-e", "sh " + shlex.quote(script_path) + "; exec sh"],
            ["gnome-terminal", "--", "sh", "-c", "sh " + shlex.quote(script_path) + "; exec bash"],
            ["xterm", "-e", "sh " + shlex.quote(script_path) + "; exec sh"],
            ["konsole", "-e", "sh", shlex.quote(script_path)],
            ["xfce4-terminal", "-e", "sh " + shlex.quote(script_path) + "; exec sh"],
        ])
        for argv in launchers:
            try:
                exe = shutil.which(argv[0]) if not argv[0].startswith("/") else argv[0]
                if exe and (os.path.exists(exe) if os.path.isabs(exe) else True):
                    subprocess.Popen(argv, start_new_session=True)
                    return
            except (OSError, FileNotFoundError):
                continue
        # Fallback: run in background and clean up script
        try:
            subprocess.Popen(cmd, cwd=working_dir, start_new_session=True)
        finally:
            try:
                os.remove(script_path)
            except OSError:
                pass
        messagebox.showinfo(
            "Launched in background",
            "Claude CLI was started but no terminal was found to show output.\n\n"
            "Run it from a terminal, or install a terminal emulator (e.g. gnome-terminal, xterm)."
        )

    def _reset_all(self):
        """Reset all settings to defaults."""
        if not messagebox.askyesno("Confirm Reset", "Reset all settings to defaults?"):
            return

        # Reset all variables
        self.claude_path_var.set(self._find_claude_path())
        self.working_dir_var.set(self._get_safe_working_dir())
        self.prompt_var.set("")
        self.model_var.set("opus")
        self.fallback_model_var.set("")
        self.continue_var.set(False)
        self.resume_var.set("")
        self.fork_session_var.set(False)
        self.session_id_var.set("")
        self.agent_var.set("")
        self.agents_json_text.delete("1.0", tk.END)
        self.tools_text.delete("1.0", tk.END)
        self.allowed_tools_var.set("")
        self.disallowed_tools_var.set("")
        self.disable_slash_commands_var.set(False)
        self.system_prompt_text.delete("1.0", tk.END)
        self.append_prompt_text.delete("1.0", tk.END)
        self.print_mode_var.set(False)
        self.input_format_var.set("text")
        self.output_format_var.set("text")
        self.json_schema_text.delete("1.0", tk.END)
        self.include_partial_var.set(False)
        self.replay_user_var.set(False)
        self.mcp_config_var.set("")
        self.strict_mcp_var.set(False)
        self.plugin_dirs.clear()
        self.plugin_listbox.delete(0, tk.END)
        self.permission_mode_var.set("default")
        self.allow_skip_perms_var.set(False)
        self.skip_perms_var.set(False)
        self.add_dirs.clear()
        self.add_dir_listbox.delete(0, tk.END)
        self.file_specs_var.set("")
        self.max_budget_var.set("")
        self.debug_var.set("")
        self.debug_file_var.set("")
        self.verbose_var.set(False)
        self.chrome_var.set("default")
        self.ide_var.set(False)
        self.settings_var.set("")
        self.setting_user_var.set(False)
        self.setting_project_var.set(False)
        self.setting_local_var.set(False)
        self.betas_var.set("")
        self.no_session_persistence_var.set(False)

        self._update_command_preview()


def main():
    """Main entry point."""
    root = tk.Tk()
    app = ClaudeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
