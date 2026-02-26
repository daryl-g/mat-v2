# Driver code to start the dashboard

# Imports
import subprocess
import os

from loguru import logger

if __name__ == "__main__":
    try:
        subprocess.run(["streamlit", "run", "src/index.py", "--server.port", "8080"])

        # Clear the temp folder after the dashboard is closed
        temp_folder = "data/tmp"
        if os.path.exists(temp_folder):
            for file in os.listdir(temp_folder):
                if file != "temp.json":
                    file_path = os.path.join(temp_folder, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
            logger.info("Temp folder cleared.")
    except KeyboardInterrupt:
        logger.warning("Dashboard stopped by user.")
    except Exception as e:
        logger.error(f"Error starting dashboard: {e}")
