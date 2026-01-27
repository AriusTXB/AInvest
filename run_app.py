import subprocess
import time
import sys
import os

def run_app():
    print("Starting InvestAI Platform...")
    
    # 1. Start Backend (FastAPI) as a background process
    print("Launching Backend (uvicorn)...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"],
        cwd=os.getcwd()
    )
    
    # Give the backend a moment to initialize
    time.sleep(3)
    
    # 2. Start Frontend (Streamlit)
    print("Launching Frontend (streamlit)...")
    # Streamlit blocks the main thread if run directly, but here we run it as a subprocess too
    # so we can manage both.
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py"],
        cwd=os.getcwd()
    )
    
    print("Services are running!")
    print("   - Backend: http://localhost:8000")
    print("   - Frontend: http://localhost:8501")
    print("PRESS CTRL+C TO STOP ALL SERVICES")

    try:
        # Keep the script running to monitor processes
        while True:
            time.sleep(1)
            # Check if processes are still alive
            if backend_process.poll() is not None:
                print("⚠️ Backend process exited unexpectedly.")
                break
            if frontend_process.poll() is not None:
                print("⚠️ Frontend process exited unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
    finally:
        # Graceful shutdown
        backend_process.terminate()
        frontend_process.terminate()
        print("Goodbye!")

if __name__ == "__main__":
    run_app()
