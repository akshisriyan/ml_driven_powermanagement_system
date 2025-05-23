import subprocess
import os

def run_netlogo_simulation():
    # Path to NetLogo CLI (update based on your NetLogo installation)
    netlogo_path = "C:/Program Files/NetLogo 6.3.0/netlogo-headless.bat"  # Adjust this path
    model_path = "../../../simulation/power_grid.nlogo"
    output_path = "../../../simulation/grid_data.csv"
    
    if not os.path.exists(netlogo_path):
        raise FileNotFoundError(f"NetLogo CLI not found at {netlogo_path}")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"NetLogo model not found at {model_path}")

    # Run NetLogo in headless mode
    cmd = [
        netlogo_path,
        "--model", model_path,
        "--table", output_path
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"NetLogo simulation failed: {e.stderr}")