"""
ETL Log Analyzer - Desktop Application
A comprehensive tool for parsing and analyzing ETL logs from multiple sources
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import re
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import threading


class LogParser:
    """Handles parsing of different log formats"""
    
    # Common log patterns
    PATTERNS = {
        'timestamp': [
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',
            r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})',
            r'(\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',
        ],
        'error': [
            r'(ERROR|SEVERE|FATAL|Exception|Failed)',
            r'(error|failure|exception)',
        ],
        'warning': [
            r'(WARNING|WARN)',
        ],
        'info': [
            r'(INFO|Information)',
        ],
        'success': [
            r'(SUCCESS|Completed|Finished)',
        ],
        'duration': [
            r'duration[:\s]+(\d+\.?\d*)\s*(s|ms|seconds|milliseconds)',
            r'elapsed[:\s]+(\d+\.?\d*)\s*(s|ms|seconds|milliseconds)',
            r'took\s+(\d+\.?\d*)\s*(s|ms|seconds|milliseconds)',
        ],
        'job_name': [
            r'job[:\s]+([A-Za-z0-9_\-]+)',
            r'workflow[:\s]+([A-Za-z0-9_\-]+)',
            r'session[:\s]+([A-Za-z0-9_\-]+)',
        ],
        'rows_processed': [
            r'(\d+)\s+rows?\s+(processed|loaded|extracted|inserted)',
            r'processed\s+(\d+)\s+records?',
        ]
    }
    
    @staticmethod
    def parse_log_file(filepath: str) -> pd.DataFrame:
        """Parse log file and extract structured data"""
        entries = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                entry = {
                    'line_number': line_num,
                    'raw_text': line.strip(),
                    'timestamp': LogParser._extract_timestamp(line),
                    'level': LogParser._extract_level(line),
                    'job_name': LogParser._extract_job_name(line),
                    'duration': LogParser._extract_duration(line),
                    'rows_processed': LogParser._extract_rows_processed(line),
                    'is_error': LogParser._is_error(line),
                    'is_warning': LogParser._is_warning(line),
                }
                entries.append(entry)
                
            df = pd.DataFrame(entries)
            return df
            
        except Exception as e:
            raise Exception(f"Error parsing log file: {str(e)}")
    
    @staticmethod
    def _extract_timestamp(line: str) -> Optional[str]:
        """Extract timestamp from log line"""
        for pattern in LogParser.PATTERNS['timestamp']:
            match = re.search(pattern, line)
            if match:
                return match.group(1).strip('[]')
        return None
    
    @staticmethod
    def _extract_level(line: str) -> str:
        """Extract log level"""
        if LogParser._is_error(line):
            return 'ERROR'
        elif LogParser._is_warning(line):
            return 'WARNING'
        elif re.search(LogParser.PATTERNS['success'][0], line, re.IGNORECASE):
            return 'SUCCESS'
        elif re.search(LogParser.PATTERNS['info'][0], line, re.IGNORECASE):
            return 'INFO'
        return 'UNKNOWN'
    
    @staticmethod
    def _extract_job_name(line: str) -> Optional[str]:
        """Extract job/workflow name"""
        for pattern in LogParser.PATTERNS['job_name']:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    @staticmethod
    def _extract_duration(line: str) -> Optional[float]:
        """Extract duration in seconds"""
        for pattern in LogParser.PATTERNS['duration']:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                unit = match.group(2).lower()
                if 'ms' in unit or 'millisecond' in unit:
                    value = value / 1000
                return value
        return None
    
    @staticmethod
    def _extract_rows_processed(line: str) -> Optional[int]:
        """Extract number of rows processed"""
        for pattern in LogParser.PATTERNS['rows_processed']:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None
    
    @staticmethod
    def _is_error(line: str) -> bool:
        """Check if line contains error"""
        for pattern in LogParser.PATTERNS['error']:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def _is_warning(line: str) -> bool:
        """Check if line contains warning"""
        for pattern in LogParser.PATTERNS['warning']:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False


class LogAnalyzer:
    """Analyzes parsed log data"""
    
    @staticmethod
    def analyze(df: pd.DataFrame) -> Dict:
        """Perform comprehensive analysis on log data"""
        analysis = {
            'summary': LogAnalyzer._get_summary(df),
            'errors': LogAnalyzer._get_errors(df),
            'warnings': LogAnalyzer._get_warnings(df),
            'performance': LogAnalyzer._analyze_performance(df),
            'jobs': LogAnalyzer._analyze_jobs(df),
            'root_causes': LogAnalyzer._suggest_root_causes(df),
        }
        return analysis
    
    @staticmethod
    def _get_summary(df: pd.DataFrame) -> Dict:
        """Get summary statistics"""
        return {
            'total_lines': len(df),
            'error_count': df['is_error'].sum(),
            'warning_count': df['is_warning'].sum(),
            'unique_jobs': df['job_name'].nunique(),
            'time_range': LogAnalyzer._get_time_range(df),
        }
    
    @staticmethod
    def _get_errors(df: pd.DataFrame) -> pd.DataFrame:
        """Get all error entries"""
        error_mask = df['is_error'] == True
        return df[error_mask].copy()
    
    @staticmethod
    def _get_warnings(df: pd.DataFrame) -> pd.DataFrame:
        """Get all warning entries"""
        warning_mask = df['is_warning'] == True
        return df[warning_mask].copy()
    
    @staticmethod
    def _analyze_performance(df: pd.DataFrame) -> Dict:
        """Analyze performance metrics"""
        duration_data = df[df['duration'].notna()]
        rows_data = df[df['rows_processed'].notna()]
        
        return {
            'avg_duration': duration_data['duration'].mean() if len(duration_data) > 0 else 0,
            'max_duration': duration_data['duration'].max() if len(duration_data) > 0 else 0,
            'total_rows_processed': rows_data['rows_processed'].sum() if len(rows_data) > 0 else 0,
            'slow_operations': duration_data.nlargest(10, 'duration') if len(duration_data) > 0 else pd.DataFrame(),
        }
    
    @staticmethod
    def _analyze_jobs(df: pd.DataFrame) -> Dict:
        """Analyze job-specific metrics"""
        jobs_data = df[df['job_name'].notna()].copy()
        
        if len(jobs_data) == 0:
            return {}
        
        job_stats = {}
        for job_name in jobs_data['job_name'].unique():
            job_df = jobs_data[jobs_data['job_name'] == job_name]
            job_stats[job_name] = {
                'occurrences': len(job_df),
                'errors': job_df['is_error'].sum(),
                'warnings': job_df['is_warning'].sum(),
                'avg_duration': job_df['duration'].mean() if job_df['duration'].notna().any() else None,
            }
        
        return job_stats
    
    @staticmethod
    def _suggest_root_causes(df: pd.DataFrame) -> List[str]:
        """Suggest potential root causes based on log patterns"""
        suggestions = []
        
        # Check for common error patterns
        error_df = df[df['is_error'] == True]
        
        if len(error_df) > 0:
            # Connection errors
            connection_errors = error_df[error_df['raw_text'].str.contains(
                'connection|timeout|network', case=False, na=False)]
            if len(connection_errors) > 0:
                suggestions.append(f"⚠️ Connection/Network Issues: {len(connection_errors)} occurrences")
            
            # Memory errors
            memory_errors = error_df[error_df['raw_text'].str.contains(
                'memory|heap|out of memory', case=False, na=False)]
            if len(memory_errors) > 0:
                suggestions.append(f"⚠️ Memory Issues: {len(memory_errors)} occurrences")
            
            # Data quality errors
            data_errors = error_df[error_df['raw_text'].str.contains(
                'null|invalid|corrupt|constraint', case=False, na=False)]
            if len(data_errors) > 0:
                suggestions.append(f"⚠️ Data Quality Issues: {len(data_errors)} occurrences")
            
            # Permission errors
            permission_errors = error_df[error_df['raw_text'].str.contains(
                'permission|denied|unauthorized|access', case=False, na=False)]
            if len(permission_errors) > 0:
                suggestions.append(f"⚠️ Permission/Access Issues: {len(permission_errors)} occurrences")
        
        # Performance issues
        slow_ops = df[df['duration'] > 60].copy()  # Operations > 60 seconds
        if len(slow_ops) > 0:
            suggestions.append(f"⚠️ Performance Bottlenecks: {len(slow_ops)} slow operations (>60s)")
        
        if not suggestions:
            suggestions.append("✓ No obvious issues detected")
        
        return suggestions
    
    @staticmethod
    def _get_time_range(df: pd.DataFrame) -> str:
        """Get time range of logs"""
        timestamps = df[df['timestamp'].notna()]['timestamp']
        if len(timestamps) > 0:
            return f"{timestamps.iloc[0]} to {timestamps.iloc[-1]}"
        return "Unknown"


class ETLLogAnalyzerApp:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ETL Log Analyzer")
        self.root.geometry("1400x900")
        
        # Data storage
        self.current_df = None
        self.current_analysis = None
        self.current_filepath = None
        
        # Setup UI
        self._setup_styles()
        self._create_menu()
        self._create_main_layout()
        
    def _setup_styles(self):
        """Setup ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Error.TLabel', foreground='red')
        style.configure('Warning.TLabel', foreground='orange')
        style.configure('Success.TLabel', foreground='green')
        
    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Log File", command=self.open_log_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Export Analysis Report", command=self.export_report, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Summary", command=lambda: self.notebook.select(0))
        view_menu.add_command(label="Errors", command=lambda: self.notebook.select(1))
        view_menu.add_command(label="Timeline", command=lambda: self.notebook.select(2))
        view_menu.add_command(label="Performance", command=lambda: self.notebook.select(3))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.open_log_file())
        self.root.bind('<Control-e>', lambda e: self.export_report())
        
    def _create_main_layout(self):
        """Create main application layout"""
        # Top toolbar
        self._create_toolbar()
        
        # Main content area with tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create tabs
        self._create_summary_tab()
        self._create_errors_tab()
        self._create_timeline_tab()
        self._create_performance_tab()
        self._create_search_tab()
        
        # Status bar
        self._create_status_bar()
        
    def _create_toolbar(self):
        """Create toolbar with common actions"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side='top', fill='x', padx=5, pady=5)
        
        ttk.Button(toolbar, text="📂 Open Log", command=self.open_log_file).pack(side='left', padx=2)
        ttk.Button(toolbar, text="🔄 Refresh", command=self.refresh_analysis).pack(side='left', padx=2)
        ttk.Button(toolbar, text="📊 Export Report", command=self.export_report).pack(side='left', padx=2)
        
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=10)
        
        ttk.Label(toolbar, text="Filter:").pack(side='left', padx=5)
        self.filter_var = tk.StringVar()
        filter_combo = ttk.Combobox(toolbar, textvariable=self.filter_var, width=15,
                                     values=['All', 'Errors Only', 'Warnings Only', 'Info Only'])
        filter_combo.set('All')
        filter_combo.pack(side='left', padx=2)
        filter_combo.bind('<<ComboboxSelected>>', self.apply_filter)
        
    def _create_summary_tab(self):
        """Create summary overview tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📋 Summary")
        
        # Create scrollable frame
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Summary content
        self.summary_text = scrolledtext.ScrolledText(scrollable_frame, height=40, width=160,
                                                       font=('Courier', 10))
        self.summary_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def _create_errors_tab(self):
        """Create errors and warnings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="❌ Errors & Warnings")
        
        # Split into two sections
        paned = ttk.PanedWindow(frame, orient='vertical')
        paned.pack(fill='both', expand=True)
        
        # Errors section
        errors_frame = ttk.LabelFrame(paned, text="Errors", padding=10)
        paned.add(errors_frame)
        
        self.errors_tree = ttk.Treeview(errors_frame, columns=('Line', 'Timestamp', 'Message'),
                                         show='tree headings', height=15)
        self.errors_tree.heading('Line', text='Line #')
        self.errors_tree.heading('Timestamp', text='Timestamp')
        self.errors_tree.heading('Message', text='Error Message')
        self.errors_tree.column('Line', width=80)
        self.errors_tree.column('Timestamp', width=180)
        self.errors_tree.column('Message', width=800)
        
        errors_scroll = ttk.Scrollbar(errors_frame, orient='vertical', command=self.errors_tree.yview)
        self.errors_tree.configure(yscrollcommand=errors_scroll.set)
        
        self.errors_tree.pack(side='left', fill='both', expand=True)
        errors_scroll.pack(side='right', fill='y')
        
        # Warnings section
        warnings_frame = ttk.LabelFrame(paned, text="Warnings", padding=10)
        paned.add(warnings_frame)
        
        self.warnings_tree = ttk.Treeview(warnings_frame, columns=('Line', 'Timestamp', 'Message'),
                                           show='tree headings', height=15)
        self.warnings_tree.heading('Line', text='Line #')
        self.warnings_tree.heading('Timestamp', text='Timestamp')
        self.warnings_tree.heading('Message', text='Warning Message')
        self.warnings_tree.column('Line', width=80)
        self.warnings_tree.column('Timestamp', width=180)
        self.warnings_tree.column('Message', width=800)
        
        warnings_scroll = ttk.Scrollbar(warnings_frame, orient='vertical', command=self.warnings_tree.yview)
        self.warnings_tree.configure(yscrollcommand=warnings_scroll.set)
        
        self.warnings_tree.pack(side='left', fill='both', expand=True)
        warnings_scroll.pack(side='right', fill='y')
        
    def _create_timeline_tab(self):
        """Create visual timeline tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📈 Timeline")
        
        # Create matplotlib figure
        self.timeline_fig = Figure(figsize=(12, 8), dpi=100)
        self.timeline_canvas = FigureCanvasTkAgg(self.timeline_fig, frame)
        self.timeline_canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
        
    def _create_performance_tab(self):
        """Create performance analysis tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="⚡ Performance")
        
        # Create matplotlib figure
        self.perf_fig = Figure(figsize=(12, 8), dpi=100)
        self.perf_canvas = FigureCanvasTkAgg(self.perf_fig, frame)
        self.perf_canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
        
    def _create_search_tab(self):
        """Create search and filter tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🔍 Search")
        
        # Search controls
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(search_frame, text="Search:").pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        search_entry.pack(side='left', padx=5)
        ttk.Button(search_frame, text="Search", command=self.perform_search).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side='left', padx=5)
        
        # Results
        results_frame = ttk.Frame(frame)
        results_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.search_results = scrolledtext.ScrolledText(results_frame, height=35, width=160,
                                                         font=('Courier', 10))
        self.search_results.pack(fill='both', expand=True)
        
    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Label(self.root, text="Ready", relief='sunken', anchor='w')
        self.status_bar.pack(side='bottom', fill='x')
        
    def open_log_file(self):
        """Open and parse log file"""
        filepath = filedialog.askopenfilename(
            title="Select Log File",
            filetypes=[
                ("Log files", "*.log"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if not filepath:
            return
        
        self.current_filepath = filepath
        self.status_bar.config(text=f"Loading {Path(filepath).name}...")
        self.root.update()
        
        # Parse in thread to avoid blocking UI
        thread = threading.Thread(target=self._parse_and_analyze, args=(filepath,))
        thread.start()
        
    def _parse_and_analyze(self, filepath):
        """Parse log file and perform analysis"""
        try:
            # Parse log file
            self.current_df = LogParser.parse_log_file(filepath)
            
            # Analyze
            self.current_analysis = LogAnalyzer.analyze(self.current_df)
            
            # Update UI on main thread
            self.root.after(0, self._update_ui_after_load)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to parse log file:\n{str(e)}"))
            self.root.after(0, lambda: self.status_bar.config(text="Ready"))
            
    def _update_ui_after_load(self):
        """Update all UI components after loading data"""
        self._update_summary()
        self._update_errors_tab()
        self._update_timeline()
        self._update_performance()
        
        filename = Path(self.current_filepath).name
        self.status_bar.config(text=f"Loaded: {filename} ({len(self.current_df)} lines)")
        
        messagebox.showinfo("Success", f"Log file parsed successfully!\n\n"
                                      f"Total lines: {len(self.current_df)}\n"
                                      f"Errors: {self.current_analysis['summary']['error_count']}\n"
                                      f"Warnings: {self.current_analysis['summary']['warning_count']}")
        
    def _update_summary(self):
        """Update summary tab"""
        self.summary_text.delete('1.0', 'end')
        
        if self.current_analysis is None:
            self.summary_text.insert('end', "No log file loaded. Please open a log file to begin analysis.")
            return
        
        summary = self.current_analysis['summary']
        
        # Header
        self.summary_text.insert('end', "="*100 + "\n")
        self.summary_text.insert('end', "ETL LOG ANALYSIS REPORT\n")
        self.summary_text.insert('end', "="*100 + "\n\n")
        
        self.summary_text.insert('end', f"File: {Path(self.current_filepath).name}\n")
        self.summary_text.insert('end', f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.summary_text.insert('end', f"Time Range: {summary['time_range']}\n\n")
        
        # Summary statistics
        self.summary_text.insert('end', "SUMMARY STATISTICS\n")
        self.summary_text.insert('end', "-"*100 + "\n")
        self.summary_text.insert('end', f"Total Lines:        {summary['total_lines']:,}\n")
        self.summary_text.insert('end', f"Errors:             {summary['error_count']:,}\n")
        self.summary_text.insert('end', f"Warnings:           {summary['warning_count']:,}\n")
        self.summary_text.insert('end', f"Unique Jobs:        {summary['unique_jobs']}\n\n")
        
        # Root cause suggestions
        self.summary_text.insert('end', "ROOT CAUSE ANALYSIS\n")
        self.summary_text.insert('end', "-"*100 + "\n")
        for suggestion in self.current_analysis['root_causes']:
            self.summary_text.insert('end', f"{suggestion}\n")
        self.summary_text.insert('end', "\n")
        
        # Performance metrics
        perf = self.current_analysis['performance']
        self.summary_text.insert('end', "PERFORMANCE METRICS\n")
        self.summary_text.insert('end', "-"*100 + "\n")
        self.summary_text.insert('end', f"Average Duration:   {perf['avg_duration']:.2f}s\n")
        self.summary_text.insert('end', f"Max Duration:       {perf['max_duration']:.2f}s\n")
        self.summary_text.insert('end', f"Total Rows:         {perf['total_rows_processed']:,}\n\n")
        
        # Job statistics
        if self.current_analysis['jobs']:
            self.summary_text.insert('end', "JOB STATISTICS\n")
            self.summary_text.insert('end', "-"*100 + "\n")
            self.summary_text.insert('end', f"{'Job Name':<40} {'Runs':<10} {'Errors':<10} {'Warnings':<10} {'Avg Duration':<15}\n")
            self.summary_text.insert('end', "-"*100 + "\n")
            
            for job_name, stats in self.current_analysis['jobs'].items():
                avg_dur = f"{stats['avg_duration']:.2f}s" if stats['avg_duration'] else "N/A"
                self.summary_text.insert('end', 
                    f"{job_name:<40} {stats['occurrences']:<10} {stats['errors']:<10} "
                    f"{stats['warnings']:<10} {avg_dur:<15}\n")
            self.summary_text.insert('end', "\n")
        
        # Top slow operations
        slow_ops = perf['slow_operations']
        if len(slow_ops) > 0:
            self.summary_text.insert('end', "TOP 10 SLOWEST OPERATIONS\n")
            self.summary_text.insert('end', "-"*100 + "\n")
            for idx, row in slow_ops.iterrows():
                self.summary_text.insert('end', 
                    f"Line {row['line_number']}: {row['duration']:.2f}s - {row['raw_text'][:80]}\n")
        
    def _update_errors_tab(self):
        """Update errors and warnings tab"""
        # Clear existing items
        for item in self.errors_tree.get_children():
            self.errors_tree.delete(item)
        for item in self.warnings_tree.get_children():
            self.warnings_tree.delete(item)
        
        if self.current_analysis is None:
            return
        
        # Populate errors
        errors_df = self.current_analysis['errors']
        for idx, row in errors_df.iterrows():
            self.errors_tree.insert('', 'end', values=(
                row['line_number'],
                row['timestamp'] or 'N/A',
                row['raw_text'][:200]
            ))
        
        # Populate warnings
        warnings_df = self.current_analysis['warnings']
        for idx, row in warnings_df.iterrows():
            self.warnings_tree.insert('', 'end', values=(
                row['line_number'],
                row['timestamp'] or 'N/A',
                row['raw_text'][:200]
            ))
        
    def _update_timeline(self):
        """Update timeline visualization"""
        self.timeline_fig.clear()
        
        if self.current_df is None:
            ax = self.timeline_fig.add_subplot(111)
            ax.text(0.5, 0.5, 'No data loaded', ha='center', va='center', fontsize=14)
            self.timeline_canvas.draw()
            return
        
        # Filter data with timestamps
        df = self.current_df[self.current_df['timestamp'].notna()].copy()
        
        if len(df) == 0:
            ax = self.timeline_fig.add_subplot(111)
            ax.text(0.5, 0.5, 'No timestamp data available', ha='center', va='center', fontsize=14)
            self.timeline_canvas.draw()
            return
        
        # Create timeline plot
        ax1 = self.timeline_fig.add_subplot(211)
        
        # Count events by type over time
        error_mask = df['is_error'] == True
        warning_mask = df['is_warning'] == True
        
        ax1.scatter(range(len(df)), [1] * len(df), c='blue', alpha=0.3, s=10, label='Info')
        if error_mask.any():
            error_indices = df[error_mask].index
            ax1.scatter([list(df.index).index(i) for i in error_indices], 
                       [1] * len(error_indices), c='red', s=50, label='Errors', marker='X')
        if warning_mask.any():
            warning_indices = df[warning_mask].index
            ax1.scatter([list(df.index).index(i) for i in warning_indices],
                       [1] * len(warning_indices), c='orange', s=30, label='Warnings', marker='^')
        
        ax1.set_xlabel('Log Entry Index')
        ax1.set_ylabel('Events')
        ax1.set_title('Event Timeline')
        ax1.legend()
        ax1.set_yticks([])
        ax1.grid(True, alpha=0.3)
        
        # Duration timeline
        ax2 = self.timeline_fig.add_subplot(212)
        duration_data = df[df['duration'].notna()]
        
        if len(duration_data) > 0:
            indices = [list(df.index).index(i) for i in duration_data.index]
            ax2.bar(indices, duration_data['duration'], alpha=0.6, color='green')
            ax2.set_xlabel('Log Entry Index')
            ax2.set_ylabel('Duration (seconds)')
            ax2.set_title('Operation Duration Over Time')
            ax2.grid(True, alpha=0.3)
        else:
            ax2.text(0.5, 0.5, 'No duration data available', ha='center', va='center', fontsize=12)
        
        self.timeline_fig.tight_layout()
        self.timeline_canvas.draw()
        
    def _update_performance(self):
        """Update performance visualizations"""
        self.perf_fig.clear()
        
        if self.current_analysis is None:
            ax = self.perf_fig.add_subplot(111)
            ax.text(0.5, 0.5, 'No data loaded', ha='center', va='center', fontsize=14)
            self.perf_canvas.draw()
            return
        
        # Job performance comparison
        if self.current_analysis['jobs']:
            ax1 = self.perf_fig.add_subplot(221)
            jobs = list(self.current_analysis['jobs'].keys())
            errors = [self.current_analysis['jobs'][j]['errors'] for j in jobs]
            warnings = [self.current_analysis['jobs'][j]['warnings'] for j in jobs]
            
            x = range(len(jobs))
            width = 0.35
            ax1.bar([i - width/2 for i in x], errors, width, label='Errors', color='red', alpha=0.7)
            ax1.bar([i + width/2 for i in x], warnings, width, label='Warnings', color='orange', alpha=0.7)
            ax1.set_xlabel('Job')
            ax1.set_ylabel('Count')
            ax1.set_title('Errors and Warnings by Job')
            ax1.set_xticks(x)
            ax1.set_xticklabels([j[:15] for j in jobs], rotation=45, ha='right')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
        
        # Duration distribution
        ax2 = self.perf_fig.add_subplot(222)
        if self.current_df is not None:
            duration_data = self.current_df[self.current_df['duration'].notna()]['duration']
            
            if len(duration_data) > 0:
                ax2.hist(duration_data, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
                ax2.set_xlabel('Duration (seconds)')
                ax2.set_ylabel('Frequency')
                ax2.set_title('Duration Distribution')
                ax2.grid(True, alpha=0.3)
            else:
                ax2.text(0.5, 0.5, 'No duration data', ha='center', va='center', fontsize=12)
                ax2.set_title('Duration Distribution')
        
        # Log level distribution
        ax3 = self.perf_fig.add_subplot(223)
        if self.current_df is not None:
            level_counts = self.current_df['level'].value_counts()
            if len(level_counts) > 0:
                colors = {'ERROR': 'red', 'WARNING': 'orange', 'INFO': 'blue', 
                         'SUCCESS': 'green', 'UNKNOWN': 'gray'}
                pie_colors = [colors.get(level, 'gray') for level in level_counts.index]
                ax3.pie(level_counts.values, labels=list(level_counts.index), autopct='%1.1f%%',
                       colors=pie_colors, startangle=90)
            ax3.set_title('Log Level Distribution')
        
        # Rows processed over time
        ax4 = self.perf_fig.add_subplot(224)
        if self.current_df is not None:
            rows_data = self.current_df[self.current_df['rows_processed'].notna()]
            
            if len(rows_data) > 0:
                ax4.plot(range(len(rows_data)), rows_data['rows_processed'].values, 
                        marker='o', linestyle='-', color='purple', alpha=0.7)
                ax4.set_xlabel('Operation Index')
                ax4.set_ylabel('Rows Processed')
                ax4.set_title('Data Processing Volume')
                ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, 'No data available', ha='center', va='center', fontsize=12)
                ax4.set_title('Data Processing Volume')
        
        self.perf_fig.tight_layout()
        self.perf_canvas.draw()
        
    def perform_search(self):
        """Perform search on log data"""
        if self.current_df is None:
            messagebox.showwarning("Warning", "Please load a log file first.")
            return
        
        search_term = self.search_var.get().strip()
        if not search_term:
            messagebox.showwarning("Warning", "Please enter a search term.")
            return
        
        self.search_results.delete('1.0', 'end')
        
        # Search in raw text
        matches = self.current_df[self.current_df['raw_text'].str.contains(
            search_term, case=False, na=False, regex=False)]
        
        self.search_results.insert('end', f"Search results for: '{search_term}'\n")
        self.search_results.insert('end', f"Found {len(matches)} matches\n")
        self.search_results.insert('end', "="*100 + "\n\n")
        
        for idx, row in matches.iterrows():
            self.search_results.insert('end', f"Line {row['line_number']}: ")
            
            # Highlight search term
            text = row['raw_text']
            self.search_results.insert('end', f"{text}\n\n")
        
        if len(matches) == 0:
            self.search_results.insert('end', "No matches found.\n")
        
    def clear_search(self):
        """Clear search results"""
        self.search_var.set('')
        self.search_results.delete('1.0', 'end')
        
    def apply_filter(self, event=None):
        """Apply filter to displayed data"""
        if self.current_df is None:
            return
        
        filter_value = self.filter_var.get()
        # Note: This would need additional implementation to actually filter the displays
        # For now, just update the status
        self.status_bar.config(text=f"Filter applied: {filter_value}")
        
    def refresh_analysis(self):
        """Refresh analysis with current data"""
        if self.current_filepath:
            self.status_bar.config(text="Refreshing analysis...")
            self.root.update()
            thread = threading.Thread(target=self._parse_and_analyze, args=(self.current_filepath,))
            thread.start()
        else:
            messagebox.showinfo("Info", "No log file loaded.")
        
    def export_report(self):
        """Export analysis report"""
        if self.current_analysis is None:
            messagebox.showwarning("Warning", "Please load a log file first.")
            return
        
        filepath = filedialog.asksaveasfilename(
            title="Save Analysis Report",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("HTML files", "*.html"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if not filepath:
            return
        
        try:
            if filepath.endswith('.json'):
                # Export as JSON with proper type conversion
                # Convert job stats to handle None/NaN values
                jobs_export = {}
                for job_name, stats in self.current_analysis['jobs'].items():
                    jobs_export[job_name] = {
                        'occurrences': int(stats['occurrences']),
                        'errors': int(stats['errors']),
                        'warnings': int(stats['warnings']),
                        'avg_duration': float(stats['avg_duration']) if stats['avg_duration'] is not None else None,
                    }
                
                export_data = {
                    'summary': {
                        'total_lines': int(self.current_analysis['summary']['total_lines']),
                        'error_count': int(self.current_analysis['summary']['error_count']),
                        'warning_count': int(self.current_analysis['summary']['warning_count']),
                        'unique_jobs': int(self.current_analysis['summary']['unique_jobs']),
                        'time_range': str(self.current_analysis['summary']['time_range']),
                    },
                    'root_causes': self.current_analysis['root_causes'],
                    'performance': {
                        'avg_duration': float(self.current_analysis['performance']['avg_duration']),
                        'max_duration': float(self.current_analysis['performance']['max_duration']),
                        'total_rows_processed': int(self.current_analysis['performance']['total_rows_processed']),
                    },
                    'jobs': jobs_export,
                }
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2)
            else:
                # Export as text
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(self.summary_text.get('1.0', 'end'))
            
            messagebox.showinfo("Success", f"Report exported to:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report:\n{str(e)}")
        
    def show_about(self):
        """Show about dialog"""
        about_text = """ETL Log Analyzer v1.0
        
A comprehensive tool for analyzing ETL log files.

Features:
• Multi-format log parsing
• Error detection and highlighting
• Performance analysis
• Visual timeline of job runs
• Root cause suggestions
• Log search and filtering
• Export analysis reports

Created with Python + Tkinter
"""
        messagebox.showinfo("About", about_text)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ETLLogAnalyzerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()