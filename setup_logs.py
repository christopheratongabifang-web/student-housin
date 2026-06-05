import os
import sys

# Create logs directory
logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(logs_dir, exist_ok=True)
print(f"Logs directory created at: {logs_dir}")
