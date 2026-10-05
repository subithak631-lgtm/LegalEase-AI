import subprocess
import sys
import time
from config import HOST, PORT

def run_services():
    print("🚀 Starting LegalEase Backend & Frontend Services...")
    
    # 1. Start FastAPI Backend
    backend_cmd = [
        sys.executable, "-m", "uvicorn", 
        "LegalEaseAPI.main:app", 
        "--host", HOST, 
        "--port", str(PORT), 
        "--reload"
    ]
    backend_proc = subprocess.Popen(backend_cmd)
    print(f"✅ Backend running at http://{HOST}:{PORT}")
    
    time.sleep(2)  # Wait for backend initialization
    
    # 2. Start Streamlit Frontend
    frontend_cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "frontend/app.py"
    ]
    frontend_proc = subprocess.Popen(frontend_cmd)
    print("✅ Frontend Streamlit interface launching...")
    
    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        backend_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    run_services()