# Helper script to install CUDA-enabled PyTorch for QLX Easy-RAG
# Targets CUDA 12.1 which is the current most stable common version

Write-Host "Checking for CUDA support in PyTorch..." -ForegroundColor Cyan

# Force reinstall with CUDA index
.\venv\Scripts\pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --force-reinstall

# Verify installation
Write-Host "`nVerifying CUDA installation..." -ForegroundColor Cyan
.\venv\Scripts\python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'Torch version: {torch.__version__}')"

$check = .\venv\Scripts\python -c "import torch; exit(0 if torch.cuda.is_available() else 1)"
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ SUCCESS: CUDA is now available!" -ForegroundColor Green
} else {
    Write-Host "`n❌ FAILED: CUDA is still not available. Please ensure your NVIDIA drivers are up to date." -ForegroundColor Red
}
