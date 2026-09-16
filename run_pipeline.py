import subprocess
import time

def run_script(script_name):
    print(f"\n[{time.strftime('%X')}] running {script_name}...")
    try:
        subprocess.run(["python", script_name], check=True)
        print(f"[{time.strftime('%X')}] run {script_name} successfully")
    except subprocess.CalledProcessError as e:
        print(f"[{time.strftime('%X')}] Error {script_name}: {e}")
        exit(1)

if __name__ == "__main__":
    print("="*50)
    print(" RoV Draft Recommender Updating")
    print("="*50)
    
    run_script("fetch_data.py")
    time.sleep(1)
    
    run_script("cleaning_data.py")
    time.sleep(1)
    
    run_script("calculate_stats.py")
    
    print("\n" + "="*50)
    print("Complete All Scripts")
    print("="*50)