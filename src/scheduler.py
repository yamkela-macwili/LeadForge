import schedule
import time
import subprocess
import sys
from datetime import datetime

def job():
    print(f"[{datetime.now()}] Starting scheduled lead generation job...")
    # Run the main script as a subprocess
    try:
        subprocess.run([sys.executable, "src/main.py"], check=True)
        print(f"[{datetime.now()}] Job completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[{datetime.now()}] Job failed with error: {e}")

def run_scheduler():
    print("Scheduler started. Running job every day at 06:00 (and once now for testing).")
    
    # Schedule the job
    schedule.every().day.at("06:00").do(job)
    
    # Also run immediately for demonstration purposes if needed, 
    # but typically a scheduler waits. 
    # For this verification, we might want to trigger it manually or just let it wait.
    # Let's run it once immediately to prove it works.
    job()
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_scheduler()
