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


def main():
    account_access_token = sys.argv[1]
    commit = '--commit' in sys.argv

    # list the projects in this account
    resp = requests.get('https://api.rollbar.com/api/1/projects',
        headers={'X-Rollbar-Access-Token': account_access_token})
    projects = resp.json()['result']
    
    for project in projects:
        handle_project(account_access_token, project, commit)


def handle_project(account_access_token, project, commit):
    project_id = project['id']

    print("Handling project:", project_id, project['name'])

    # list all project access tokens
    resp = requests.get('https://api.rollbar.com/api/1/project/%d/access_tokens' % project_id,
        headers={'X-Rollbar-Access-Token': account_access_token})
    for project_token in resp.json()['result']:
        handle_project_token(account_access_token, project_id, project_token, commit)

    print()


def handle_project_token(account_access_token, project_id, project_token, commit):
    project_access_token = project_token['access_token']

    print("Handling project", project_id, "token", project_access_token)
    print("-- Current rate limit:", project_token['rate_limit_window_count'], "per",
        project_token['rate_limit_window_size'])
    if project_token['rate_limit_window_size'] is None and project_token['rate_limit_window_count'] is None:
        print("-- No limit; skipping")
    else:
        print("-- Clearing limit...")
        if commit:
            resp = requests.patch(
                'https://api.rollbar.com/api/1/project/{}/access_token/{}'.format(project_id, project_access_token),
                {'rate_limit_window_count': 0, 'rate_limit_window_size': 0},
                headers={'X-Rollbar-Access-Token': account_access_token})
            resp_json = resp.json()
            if resp_json['err']:
                print("---- Error:", resp_json['message'])
            else:
                print("---- Done.")
        else:
            print("---- Not in commit mode, skipping")
        

    print()
    
    

if __name__ == '__main__':
    main()
