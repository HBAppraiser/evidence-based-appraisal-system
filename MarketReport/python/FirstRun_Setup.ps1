# Bootstrap embedded Python 3.12.10 to C:\MarketReport\python and install deps
$ErrorActionPreference = "Stop"
$base = "C:\MarketReport"
$pyDir = Join-Path $base "python"
if (!(Test-Path $pyDir)) { New-Item -ItemType Directory -Path $pyDir | Out-Null }
$zip = Join-Path $base "python-3.12.10-embed-amd64.zip"
$uri = "https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip"
if (!(Test-Path $zip)) { Invoke-WebRequest -Uri $uri -OutFile $zip }
Expand-Archive -Path $zip -DestinationPath $pyDir -Force
$pth = Get-ChildItem -Path $pyDir -Filter "python312._pth" | Select-Object -First 1
if ($null -eq $pth) { throw "python312._pth not found" }
$content = Get-Content $pth.FullName
if ($content -notmatch "import site") { Add-Content -Path $pth.FullName -Value "import site" }
$pyExe = Join-Path $pyDir "python.exe"
$gp = Join-Path $base "get-pip.py"
if (!(Test-Path $gp)) { Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $gp }
& $pyExe $gp
& $pyExe -m pip install --upgrade pip
& $pyExe -m pip install -r (Join-Path $base "requirements.txt")
Write-Host "Embedded Python ready."
