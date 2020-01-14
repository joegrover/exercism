import requests
import pandas
import random

sv_df = pandas.read_csv("sample_variables.csv")


host = "https://jgrover.hiring.ipums.org"
usa_endpoint = host + "/publish_usa"
nhgis_endpoint = host + "/publish_nhgis"

samples = set(sv_df["sample_name"].to_list())
variables = set(sv_df["variable_mnemonic"].to_list())
data_tables = set(["1790_cPop.dt1", "1790_cPop.dt8", "1800_cPop.dt1", "1800_cPop.dt9"])
users = ["glip", "glop", "rocko", "heffer", "Filburt"]


def mock_usa_request(repeats=2):
    k_s = random.randint(1, len(samples))
    s = random.sample(samples, k=k_s)
    k_v = random.randint(1, len(variables))
    v = random.sample(variables, k=k_v)
    u = random.choice(users)
    params = {
        "samples[]": s,
        "variables[]": v,
        "user": u,
        "submit": "Submit",
    }
    # XXX Need to repeat here until I figure out the whole client-only
    # -gets-every-other-message RabbitMQ issue.
    for _ in range(repeats):
        resp = requests.get(usa_endpoint, params=params)
        print(resp)
    return resp


def mock_nhgis_request(repeats=1):
    k_d = random.randint(1, len(data_tables))
    d = random.sample(data_tables, k=k_d)
    u = random.choice(users)
    params = {
        "data_tables[]": d,
        "user": u,
        "submit": "Submit",
    }
    # XXX Need to repeat here until I figure out the whole client-only
    # -gets-every-other-message RabbitMQ issue.
    for _ in range(repeats):
        resp = requests.get(nhgis_endpoint, params=params)
        print(resp)
    return resp
