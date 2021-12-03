"""
Clears all user-defined rate limits for all projects in an account

Use with an account access token that has scopes 'read' and 'write'

Usage:

python clear_all_rate_limits.py YOUR_ACCOUNT_ACCESS_TOKEN --commit
"""

from __future__ import print_function

import sys
from pprint import pprint

import requests

num_projects = 0
num_tokens = 0
num_tokens_with_limits = 0
num_tokens_updated = 0
num_tokens_skipped = 0
num_errors = 0


def main():
    account_access_token = sys.argv[1]
    commit = "--commit" in sys.argv

    # list the projects in this account
    resp = requests.get(
        "https://api.rollbar.com/api/1/projects",
        headers={"X-Rollbar-Access-Token": account_access_token},
    )
    projects = resp.json()["result"]

    for project in projects:
        handle_project(account_access_token, project, commit)

    # print stats
    print("Projects:", num_projects)
    print("Tokens", num_tokens)
    print("Tokens with limits:", num_tokens_with_limits)
    print("Tokens updated:", num_tokens_updated)
    print("Tokens skipped:", num_tokens_skipped)
    print("Errors:", num_errors)


def handle_project(account_access_token, project, commit):
    global num_projects
    num_projects += 1
    project_id = project["id"]

    print("Handling project:", project_id, project["name"])

    # list all project access tokens
    resp = requests.get(
        "https://api.rollbar.com/api/1/project/%d/access_tokens" % project_id,
        headers={"X-Rollbar-Access-Token": account_access_token},
    )
    for project_token in resp.json()["result"]:
        handle_project_token(account_access_token, project_id, project_token, commit)

    print()


def handle_project_token(account_access_token, project_id, project_token, commit):
    global num_tokens, num_tokens_with_limits, num_tokens_updated, num_tokens_skipped, num_errors

    num_tokens += 1
    project_access_token = project_token["access_token"]

    print("Handling project", project_id, "token", project_access_token)
    print(
        "-- Current rate limit:",
        project_token["rate_limit_window_count"],
        "per",
        project_token["rate_limit_window_size"],
    )
    if (
        project_token["rate_limit_window_size"] is None
        and project_token["rate_limit_window_count"] is None
    ):
        num_tokens_skipped += 1
        print("-- No limit; skipping")
    else:
        num_tokens_with_limits += 1
        print("-- Clearing limit...")
        if commit:
            resp = requests.patch(
                "https://api.rollbar.com/api/1/project/{}/access_token/{}".format(
                    project_id, project_access_token
                ),
                {"rate_limit_window_count": 0, "rate_limit_window_size": 0},
                headers={"X-Rollbar-Access-Token": account_access_token},
            )
            resp_json = resp.json()
            if resp_json["err"]:
                num_errros += 1
                print("---- Error:", resp_json["message"])
            else:
                num_tokens_updated += 1
                print("---- Done.")
        else:
            num_tokens_skipped += 1
            print("---- Not in commit mode, skipping")

    print()


if __name__ == "__main__":
    main()
