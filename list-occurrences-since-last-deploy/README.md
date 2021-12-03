This example shows how to use the Rollbar API from Python to list all occurrences in an environment since the last deploy.

If you just want to read the code, take a look at `list_occurrences_since_last_deploy.py` in this repo.

To install and run, you will need:

- Python 2.7 or Python 3
- pip
- A Rollbar project read access token

To install:

```
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

To run, install and then:

```
python list_occurrences_since_last_deploy.py PROJECT_READ_ACCESS_TOKEN ENVIRONMENT_NAME
```
