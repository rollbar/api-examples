# coding: utf-8

import json, time, requests


def start_job(query, access_token):
    url = "https://api.rollbar.com/api/1/rql/jobs"
    data = {
        "query_string": query,
    }

    res = requests.post(
        url, headers={"X-Rollbar-Access-Token": access_token}, json=data
    )
    return res.json(), res.status_code < 400


def get_job(job_id, access_token):
    url = "https://api.rollbar.com/api/1/rql/job/%d" % job_id

    res = requests.get(url, headers={"X-Rollbar-Access-Token": access_token})
    return res.json(), res.status_code < 400


def get_result(job_id, access_token, expand=False):
    url = "https://api.rollbar.com/api/1/rql/job/%d/result" % job_id
    if expand:
        url += "&expand=result"

    res = requests.get(url, headers={"X-Rollbar-Access-Token": access_token})
    return res.json(), res.status_code < 400


def run_query(query, access_token):
    job, success = start_job(query, access_token)

    while success and job["result"]["status"] in ("new", "running"):
        job, success = get_job(job["result"]["id"], access_token)
        time.sleep(3)

    if success:
        return get_result(job["result"]["id"], access_token)
    else:
        return job, False


DEMO_QUERY = (
    "select body.message.body, count(*) number_of_messages "
    "from item_occurrence "
    "where timestamp > unix_timestamp() - 60 * 60 * 24 * 30 "
    "group by body.message.body "
    "order by 2 desc"
)

DEMO_ACCESS_TOKEN = "9baa92910b304f8c9eeb39c3c0319b21"  # The demo read access token

if __name__ == "__main__":
    result, succeeded = run_query(DEMO_QUERY, DEMO_ACCESS_TOKEN)
    if not succeeded:
        print("Failed to run query")
    else:
        print(json.dumps(result))
