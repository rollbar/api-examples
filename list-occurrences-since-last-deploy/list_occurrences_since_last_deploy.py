"""
Example showing how to use the Rollbar API to list all occurrences since the last deploy
"""

from __future__ import print_function

import sys
import requests


# Occurrences are returned descending by ID, which is approximately but not exactly
# descending by timestamp. We'll keep searching through occurrences until we reach one that
# is this many seconds older than the last deploy.
SEARCH_BUFFER_SECONDS = 60


def fetch_last_deploy_timestamp(access_token, environment):
    """
    Return the timestamp of the last deploy in `environment`
    """
    # The /api/1/deploys endpoint returns all deploys in descending order by timestamp
    # We'll iterate through them until we find one that matches `environment`.

    page = 1
    while True:
        result = requests.get(
            "https://api.rollbar.com/api/1/deploys?page={}".format(page),
            headers={"X-Rollbar-Access-Token": access_token},
        )
        deploys = result.json()["result"]["deploys"]
        if not deploys:
            # we've reached the end of the list
            return None

        for deploy in deploys:
            if deploy["environment"] == environment:
                return deploy["start_time"]
        page += 1


def print_occurrences_since_timestamp(access_token, environment, min_timestamp):
    """
    Prints all occurrences (as json) since the specified timestamp
    """

    page = 1
    while True:
        result = requests.get(
            "https://api.rollbar.com/api/1/instances/?page={}".format(page),
            headers={"X-Rollbar-Access-Token": access_token},
        )
        occurrences = result.json()["result"]["instances"]
        if not occurrences:
            # reached the end of the list
            return

        for occurrence in occurrences:
            # filter by environment
            if occurrence["data"]["environment"] == environment:
                # now check timestamp
                if occurrence["timestamp"] >= min_timestamp:
                    print(occurrence["data"])
                elif occurrence["timestamp"] < min_timestamp - SEARCH_BUFFER_SECONDS:
                    # we've found an occurrence older than the min timestamp minus the buffer.
                    # done searching.
                    return

        page += 1


def main(access_token, environment):
    last_deploy_timestamp = fetch_last_deploy_timestamp(access_token, environment)
    print_occurrences_since_timestamp(access_token, environment, last_deploy_timestamp)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: python list_occurrences_since_last_deploy.py <project read access token> <environment name>"
        )
        sys.exit(1)

    access_token = sys.argv[1]
    environment = sys.argv[2]

    main(access_token, environment)
