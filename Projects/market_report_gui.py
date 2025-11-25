#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Market Report — Simple GUI launcher
- Lets you browse for Comps CSV (required) and Subject CSV (optional)
- Lets you choose an output folder
- Runs the existing market_report.py sitting in the same folder
"""

import os, sys, subprocess, threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import scrolledtext
from pathlib import Path

APP_TITLE = "Market Report — GUI"

def here() -> Path:
    return Path(__file__).resolve().parent

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("740x540")
        self.resizable(True, True)

        self.script_path = here() / "market_report.py"

        # Vars
        self.var_comps = tk.StringVar()
        self.var_subject = tk.StringVar()
        self.var_outdir = tk.StringVar(value=str((here() / "out").resolve()))
        self.var_skip_pdf = tk.BooleanVar(value=False)

        # UI
        pad = {"padx": 8, "pady": 6}
        frm = tk.Frame(self); frm.pack(fill="x", **pad)

        tk.Label(frm, text="Comps CSV (required):").grid(row=0, column=0, sticky="w")
        tk.Entry(frm, textvariable=self.var_comps, width=70).grid(row=0, column=1, sticky="we", padx=(6,6))
        tk.Button(frm, text="Browse...", command=self.pick_comps).grid(row=0, column=2)

        tk.Label(frm, text="Subject CSV (optional):").grid(row=1, column=0, sticky="w")
        tk.Entry(frm, textvariable=self.var_subject, width=70).grid(row=1, column=1, sticky="we", padx=(6,6))
        tk.Button(frm, text="Browse...", command=self.pick_subject).grid(row=1, column=2)

        tk.Label(frm, text="Output folder:").grid(row=2, column=0, sticky="w")
        tk.Entry(frm, textvariable=self.var_outdir, width=70).grid(row=2, column=1, sticky="we", padx=(6,6))
        tk.Button(frm, text="Browse...", command=self.pick_outdir).grid(row=2, column=2)

        tk.Checkbutton(frm, text="Skip PDF (use if ReportLab errors)", variable=self.var_skip_pdf).grid(row=3, column=0, columnspan=3, sticky="w")

        tk.Button(frm, text="Run Report", command=self.run_report, bg="#0b5", fg="white").grid(row=4, column=0, columnspan=3, sticky="we", pady=(10,8))

        self.console = scrolledtext.ScrolledText(self, wrap="word", height=18)
        self.console.pack(fill="both", expand=True, padx=8, pady=(0,8))
        self.console.insert("end", f"{APP_TITLE}\nSelect files then click Run Report.\n\n")

        frm.grid_columnconfigure(1, weight=1)

    def pick_comps(self):
        p = filedialog.askopenfilename(title="Select comps CSV", filetypes=[("CSV files","*.csv"), ("All files","*.*")])
        if p: self.var_comps.set(p)

    def pick_subject(self):
        p = filedialog.askopenfilename(title="Select subject CSV (optional)", filetypes=[("CSV files","*.csv"), ("All files","*.*")])
        if p: self.var_subject.set(p)

    def pick_outdir(self):
        p = filedialog.askdirectory(title="Select output folder")
        if p: self.var_outdir.set(p)

    def run_report(self):
        comps = self.var_comps.get().strip()
        outdir = self.var_outdir.get().strip()
        subject = self.var_subject.get().strip()
        no_pdf = self.var_skip_pdf.get()

        if not comps:
            messagebox.showerror("Missing file", "Please choose the Comps CSV."); return
        if not self.script_path.exists():
            messagebox.showerror("Script not found", f"Expected market_report.py at:\n{self.script_path}"); return

        cmd = [sys.executable, str(self.script_path), "--data", comps, "--output_dir", outdir]
        if subject:
            cmd += ["--subject_csv", subject]
        if no_pdf:
            cmd += ["--no-pdf"]

        self.console.delete("1.0", "end")
        self.console.insert("end", "Running:\n" + " ".join(f'"{c}"' if " " in c else c for c in cmd) + "\n\n")
        self.console.see("end")

        def worker():
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=str(here()))
                for line in proc.stdout:
                    self.console.insert("end", line)
                    self.console.see("end")
                rc = proc.wait()
                if rc == 0:
                    self.console.insert("end", "\nDone.\n")
                    messagebox.showinfo("Completed", "Market report finished successfully.")
                else:
                    self.console.insert("end", f"\nExited with code {rc}\n")
                    messagebox.showerror("Error", "The report hit an error. Check console output.")
            except Exception as e:
                self.console.insert("end", f"\nLauncher error: {e}\n")
                messagebox.showerror("Error", str(e))

        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    app = App()
    app.mainloop()