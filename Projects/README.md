# Market Report Generator

**Run (Windows, PowerShell):**
```powershell
cd C:\Projects
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python market_report.py --data sample_data.csv --output_dir out
```

If `Activate.ps1` is blocked:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
.venv\Scripts\Activate.ps1
```
