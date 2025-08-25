# setup.ps1

$env:TF_ENABLE_ONEDNN_OPTS = "0"
$env:TF_CPP_MIN_LOG_LEVEL = "3"
$env:PYTHONDONTWRITEBYTECODE = "1"

uv run main.py