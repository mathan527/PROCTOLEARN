"""
Granian ASGI Server Runner
Fast Rust-based ASGI server - 2-3x faster than Uvicorn
"""
import subprocess
import sys

def main():
    """Run the FastAPI app with Granian"""
    cmd = [
        "python",
        "-m",
        "granian",
        "--interface", "asgi",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",  # Auto-reload on code changes
        "--workers", "1",  # Set to 1 for Windows (Windows doesn't support multiple workers)
        "--log-level", "info",
    ]
    
    print("Starting ProctoLearn with Granian (Rust ASGI Server)")
    print(f"Running: {' '.join(cmd)}")
    print("Note: Windows only supports 1 worker (OS limitation)")
    print("Granian is ready!")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Granian server...")
        sys.exit(0)

if __name__ == "__main__":
    main()
