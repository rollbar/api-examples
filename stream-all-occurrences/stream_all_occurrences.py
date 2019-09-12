"""
Streams (to stdout) all occurrences in a project
"""

from __future__ import print_function

import sys
import time

import requests


def handle_occurrence(occ):
    simple_title = get_simple_title(occ['data']['body'])
    print(occ['id'], time.ctime(occ['timestamp']), simple_title)


def get_simple_title(body):
    try:
        if 'trace_chain' in body and len(body['trace_chain']) > 0:
            return make_simple_title(body['trace_chain'][0]['exception'])
        elif 'trace' in body:
            return make_simple_title(body['trace']['exception'])
        else:
            return body['message']['body']
    except Exception as e:
        print("Error making title:", e)
        return "(unknown)"


def make_simple_title(exception):
    try:
        return "{}: {}".format(exception['class'], exception['message'])
    except KeyError:
        return repr(exception)


def init_min_id(project_read_token):
    """
    Init min id to the current max id.
    """
    for occ in fetch_occurrences(project_read_token):
        return occ['id']
    return 0


def stream_all_occurrences(project_read_token, min_id=None):
    last_id = None  # 'max' id
    
    max_id = None
    
    if min_id is None:
        min_id = init_min_id(project_read_token)  # min id we have ever seen - stop streaming if we reach this id

    while True:
        print("last_id:", last_id, "max_id:", max_id, "min_id:", min_id)
        try:
            iterator = fetch_occurrences(project_read_token, last_id, min_id)
        except Exception as e:
            # wait and retry?
            print("Got error, waiting:", e)
            time.sleep(10)
            continue
        else:
            any_results = False
            for occ in iterator:
                any_results = True
                # initialize max_id if not yet set
                if max_id is None:
                    max_id = occ['id']
                # update last_id
                last_id = occ['id']
                # occ['data'] contains the occurrence payload. If you want to do something with the data, you can do that here.
                handle_occurrence(occ)
            
            if not any_results:
                print("Reached end.")
                
                # Set min_id to our starting id, and then reset max_id and last_id
                min_id = max_id
                max_id = None
                last_id = None

                # wait for a bit
                time.sleep(5)



def fetch_occurrences(project_read_token, last_id=None, min_id=0):
    """
    Fetch occurrences from a project. This will iterate through all occurrences in descending order by id,
    starting from `last_id`.

    last_id: the high id to start from
    min_id: the low id to not go beyond (not go lower than)
    """
    url = 'https://api.rollbar.com/api/1/instances?access_token={}'.format(project_read_token)
    if last_id is not None:
        url += '&lastId={}'.format(last_id)

    resp = requests.get(url)
    result = resp.json()
    if result['err'] == 0:
        for elem in result['result']['instances']:
            if elem['id'] >= min_id:
                yield elem
            else:
                #print("Skipping elem id {} beyond min_id {}".format(elem['id'], min_id))
                pass
    else:
        raise Exception("Error loading data from Rollbar API: %r", result)


if __name__ == '__main__':
    project_read_token = sys.argv[1]
    min_id = None
    if len(sys.argv) > 2:
        min_id = int(sys.argv[2])
    
    try:
        stream_all_occurrences(project_read_token, min_id)
    except KeyboardInterrupt:
        print("Exiting...")
