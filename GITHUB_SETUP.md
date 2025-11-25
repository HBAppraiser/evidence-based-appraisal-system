# GitHub Repository Setup Guide

## Step-by-Step Instructions

### 1. Create GitHub Repository

**Option A: Via GitHub Website**
1. Go to https://github.com/new
2. Repository name: `evidence-based-appraisal-system`
3. Description: `Hybrid R + Python statistical analysis platform for residential real estate appraisals using Evidence-Based Valuation methodology`
4. Choose **Private** (recommended - contains client work) or Public
5. ✅ Add README file (we already have one)
6. ✅ Add .gitignore (we already have one)
7. ✅ Choose license: MIT (we already have LICENSE file)
8. Click **Create repository**

**Option B: Via GitHub CLI**
```bash
# Install GitHub CLI first: https://cli.github.com/
gh repo create evidence-based-appraisal-system --private --description "Evidence-Based Appraisal System"
```

### 2. Initialize Local Repository

Open PowerShell in your project directory:

```powershell
# Navigate to project folder
cd "C:\Agentic PROJECT_PYTHON_Appraisal Templates"

# Initialize git repository
git init

# Add all files (respects .gitignore)
git add .

# Check what will be committed
git status

# First commit
git commit -m "Initial commit: Evidence-Based Appraisal System v1.0"
```

### 3. Connect to GitHub

```powershell
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/evidence-based-appraisal-system.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

### 4. Verify Upload

Go to: `https://github.com/YOUR_USERNAME/evidence-based-appraisal-system`

You should see:
- ✅ README.md displayed on home page
- ✅ All folders: templates/, python/, config/, data/, docs/, batch/
- ✅ 26+ files uploaded
- ✅ No sensitive data (client names, real property addresses, etc.)

### 5. Create Branches (Recommended)

```powershell
# Create development branch
git checkout -b dev

# Push dev branch
git push -u origin dev

# Switch back to main
git checkout main
```

**Branching Strategy:**
- `main` - Production-ready code only
- `dev` - Active development
- `feature/chart-improvements` - Specific features
- `fix/column-detection` - Bug fixes

### 6. Add Collaborators (Optional)

1. Go to repository Settings → Collaborators
2. Click **Add people**
3. Enter GitHub usernames or emails
4. Choose permission level:
   - **Read** - View only
   - **Write** - Can push
   - **Admin** - Full control

## 🔒 Security Checklist

Before pushing, verify `.gitignore` excludes:

```powershell
# Check ignored files
git check-ignore -v config/market_analysis_inputs.json
git check-ignore -v data/client_sales.csv
```

**Must be ignored:**
- ✅ `config/market_analysis_inputs.json` (contains client names, addresses)
- ✅ `data/*.csv` (except test files)
- ✅ `docs/extracted_reports/*.txt` (appraisal reports)
- ✅ `validation_info.json` (contains project specifics)
- ✅ `*.xlsx`, `*.pdf` output files

**Safe to commit:**
- ✅ `config/market_analysis_inputs_example.json` (template)
- ✅ `data/test_small.csv` (synthetic test data)
- ✅ All Python `.py` files
- ✅ All `.qmd` template files
- ✅ Documentation `.md` files
- ✅ Batch `.bat` files

## 📦 What Gets Uploaded

### ✅ Will be committed:
```
templates/
  Evidence_Based_Appraisal_Report.qmd
  Hybrid_Appraisal_Report.qmd
  01-Hybrid-Wrangle.qmd

python/
  market_analysis_v2.3.3.py
  generate_charts.py
  adjustment_analysis.py
  simple_appraiser_v7_1.py
  create_excel.py
  create_pdf.py
  Run_Integrated_Analysis.py
  csv_picker.py

config/
  market_analysis_inputs_example.json  ← Template only

data/
  test_small.csv  ← Test data only
  sales_data_processed.csv  ← If you want
  statistics_summary.csv  ← If you want

docs/
  Chart_Generation_Guide.md
  Statistical_Analysis_Guide.md
  PROMPT_Residential_Analysis.md

batch/
  Run_Analysis.bat
  Open_Form.bat

README.md
requirements.txt
.gitignore
LICENSE
```

### ❌ Will be ignored:
```
config/
  market_analysis_inputs.json  ← Contains real client data
  validation_info.json  ← Contains real project results

data/
  *.csv (except test files)  ← Real MLS data

docs/extracted_reports/
  *.txt  ← Extracted appraisal reports

output/
  *.png  ← Generated charts
  *.xlsx  ← Generated Excel files
  *.pdf  ← Generated PDF reports

__pycache__/  ← Python bytecode
.vscode/  ← IDE settings
```

## 🔄 Daily Workflow

### Making Changes

```powershell
# Check status
git status

# Add specific files
git add python/market_analysis_v2.3.3.py
git add templates/Evidence_Based_Appraisal_Report.qmd

# Or add all changed files
git add .

# Commit with message
git commit -m "Enhanced trend analysis with R² confidence intervals"

# Push to GitHub
git push
```

### Good Commit Messages

```powershell
# ✅ Good
git commit -m "Add machine learning validation section to EBV template"
git commit -m "Fix column auto-detection for MLS variations"
git commit -m "Update Chart 5 regression equation formatting"

# ❌ Bad
git commit -m "updates"
git commit -m "fixed stuff"
git commit -m "changes"
```

## 🌿 Branch Workflow

```powershell
# Create feature branch
git checkout -b feature/add-dashboard

# Make changes...
# ... edit files ...

# Commit changes
git add .
git commit -m "Add Streamlit dashboard for interactive analysis"

# Push feature branch
git push -u origin feature/add-dashboard

# Merge into main (via GitHub Pull Request or locally)
git checkout main
git merge feature/add-dashboard
git push

# Delete merged branch
git branch -d feature/add-dashboard
```

## 📊 Repository Statistics

After setup, you'll have:
- **~2,000+ lines of Python code**
- **~1,400+ lines of Quarto/R code**
- **7 professional chart generators**
- **26 integrated files**
- **4 methodologies integrated**
- **Full documentation**

## 🆘 Troubleshooting

### Issue: "fatal: remote origin already exists"
```powershell
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/evidence-based-appraisal-system.git
```

### Issue: Authentication failed
```powershell
# Use GitHub Personal Access Token
# 1. Go to GitHub Settings → Developer settings → Personal access tokens
# 2. Generate new token with 'repo' scope
# 3. Use token as password when prompted
```

### Issue: Large files rejected
```powershell
# Check file sizes
Get-ChildItem -Recurse | Where-Object { $_.Length -gt 50MB }

# Remove large files from tracking
git rm --cached large_file.csv
# Add to .gitignore
echo "large_file.csv" >> .gitignore
git add .gitignore
git commit -m "Remove large file from tracking"
```

### Issue: Sensitive data accidentally committed
```powershell
# Remove file from history (use BFG Repo-Cleaner or git-filter-repo)
# Easier: Delete repo, fix .gitignore, re-create repo

# Quick fix for last commit only:
git rm --cached config/market_analysis_inputs.json
git commit --amend -m "Initial commit (removed sensitive data)"
git push --force
```

## 🎯 Next Steps After Setup

1. ✅ Verify repository is private (if needed)
2. ✅ Add repository description and topics (tags)
3. ✅ Enable GitHub Actions (optional CI/CD)
4. ✅ Add repository secrets for credentials
5. ✅ Create first GitHub Release (v1.0.0)
6. ✅ Add GitHub Pages for documentation (optional)

## 📝 GitHub Topics (Tags)

Add these topics to your repository for discoverability:
- `real-estate`
- `appraisal`
- `evidence-based-valuation`
- `r`
- `python`
- `quarto`
- `statistics`
- `machine-learning`
- `data-analysis`
- `regression-analysis`

---

**Need Help?** Check GitHub's official guides:
- https://docs.github.com/en/get-started/quickstart
- https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
