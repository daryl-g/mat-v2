# Driver code to start the dashboard

# Imports
import subprocess

from loguru import logger

if __name__ == "__main__":
    try:
        subprocess.run(["streamlit", "run", "src/index.py", "--server.port", "8080"])
    except KeyboardInterrupt:
        logger.warning("Dashboard stopped by user.")
    except Exception as e:
        logger.error(f"Error starting dashboard: {e}")
