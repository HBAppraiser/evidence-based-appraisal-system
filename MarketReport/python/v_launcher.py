import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess, os, shutil

def find_python():
    if shutil.which("python"):
        return ["python"]
    if shutil.which("py"):
        return ["py","-3"]
    emb = os.path.join(os.path.dirname(__file__), "python", "python.exe")
    if os.path.isfile(emb):
        return [emb]
    return None

def run_script(data_path, subject_path, outdir):
    py = find_python()
    if not py:
        messagebox.showerror("Python not found","No Python interpreter found.\nRun FirstRun_Setup.ps1 or install Python.")
        return
    cmd = py + ["market_report_generator_python.py","--data",data_path,"--output_dir",outdir]
    if subject_path:
        cmd += ["--subject_csv", subject_path]
    try:
        subprocess.Popen(cmd, shell=False)
    except Exception as e:
        messagebox.showerror("Launch error", f"Could not start:\n{e}")

def browse_file(entry):
    p = filedialog.askopenfilename(filetypes=[("CSV","*.csv"),("All files","*.*")])
    if p: entry.delete(0,tk.END); entry.insert(0,p)

def browse_dir(entry):
    p = filedialog.askdirectory()
    if p: entry.delete(0,tk.END); entry.insert(0,p)

def main():
    root = tk.Tk(); root.title("Market Report Generator")
    for i in range(3): root.grid_columnconfigure(i, weight=0)
    root.grid_columnconfigure(1, weight=1)

    tk.Label(root,text="Market Data CSV:").grid(row=0,column=0,sticky="e",padx=6,pady=6)
    e_data = tk.Entry(root,width=60); e_data.grid(row=0,column=1,sticky="we",padx=6,pady=6)
    tk.Button(root,text="Browse",command=lambda:browse_file(e_data)).grid(row=0,column=2,padx=6,pady=6)

    tk.Label(root,text="Subject CSV (optional):").grid(row=1,column=0,sticky="e",padx=6,pady=6)
    e_subj = tk.Entry(root,width=60); e_subj.grid(row=1,column=1,sticky="we",padx=6,pady=6)
    tk.Button(root,text="Browse",command=lambda:browse_file(e_subj)).grid(row=1,column=2,padx=6,pady=6)

    tk.Label(root,text="Output Directory:").grid(row=2,column=0,sticky="e",padx=6,pady=6)
    e_out = tk.Entry(root,width=60); e_out.grid(row=2,column=1,sticky="we",padx=6,pady=6)
    tk.Button(root,text="Browse",command=lambda:browse_dir(e_out)).grid(row=2,column=2,padx=6,pady=6)

    def go():
        d, s, o = e_data.get().strip(), e_subj.get().strip(), e_out.get().strip()
        if not d or not o:
            messagebox.showerror("Missing info","Pick a Market Data CSV and Output Directory."); return
        if not os.path.isfile(d): messagebox.showerror("Invalid file","Market CSV not found."); return
        if s and not os.path.isfile(s): messagebox.showerror("Invalid file","Subject CSV not found."); return
        if not os.path.isdir(o):
            try: os.makedirs(o, exist_ok=True)
            except Exception as e: messagebox.showerror("Output error", str(e)); return
        run_script(d, s, o); messagebox.showinfo("Started","Report generation has started.")

    tk.Button(root,text="Generate Report",command=go,width=24).grid(row=3,column=1,pady=12)

    try:
        default_out = os.path.join(os.path.expanduser("~"),"Documents","MarketReports")
        e_out.insert(0, default_out)
    except Exception: pass

    root.mainloop()

if __name__ == "__main__":
    main()
