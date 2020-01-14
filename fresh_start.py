import random
import database
from pymongo import MongoClient
from pathlib import Path
import subprocess
import sys
import time
import json
from mock_requests import mock_nhgis_request, mock_usa_request

CWD = Path.cwd()
PYTHON = sys.executable


def run_client():
    client = subprocess.Popen(
        [PYTHON, str(CWD / "extract_requests_client.py"), "-p", "nhgis", "-p", "usa"]
    )
    time.sleep(5)
    return client


def run():
    mclient = MongoClient(host="0.0.0.0", port=27017)
    mclient.drop_database("extract_requests")
    # load database with sample-by-variable connections from csv
    database.load_usa_sample_variables()
    # start the client to get extract requests from RabbitMQ
    client = run_client()
    # run some mock extract requests
    for _ in range(random.randint(1, 10)):
        mock_nhgis_request()
        mock_usa_request()
    # run a report:
    print(json.dumps(database.extract_report()))
    # keep client running:
    print("client is still running, waiting for more extracts...")
    client.communicate()


if __name__ == "__main__":
    run()
