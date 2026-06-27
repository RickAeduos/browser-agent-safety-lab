$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$env:PYTHONPATH = $root
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
  $python = "python"
}
& $python -m packages.eval_observatory.report @args

