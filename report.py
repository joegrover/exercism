from flask import Flask
import subprocess
import time
from fresh_start import CWD, PYTHON
from database import extract_report


app = Flask(__name__)


def start_fresh():
    client = subprocess.Popen(
        [PYTHON, str(CWD / "fresh_start.py"), "-p", "nhgis", "-p", "usa"]
    )
    time.sleep(5)
    return client


@app.route("/")
def you_made_it():
    return "You made it! Go to /report.json"


@app.route("/report.json")
def run_extract_report():
    report = extract_report()
    return report


if __name__ == "__main__":
    client = start_fresh()
    try:
        app.run(host="localhost", port=4996)
    except Exception:
        client.kill()
    finally:
        client.kill()
