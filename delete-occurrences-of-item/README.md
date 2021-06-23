# Delete all occurrences of an item

A simple bash script that deletes all occurrences of a Rollbar item via the API.
Be careful with running this script; there is no way to recover the occurrences you delete!

## Usage
```
bash delete_item.sh <item_counter> <read_token> <write_token>
```

- `<item_counter>`  The number you see in the url of the item page: https://rollbar.com/<account>/<project>/item/<item_counter>
- `<read_token>`    A project access token with *read* scope
- `<write_token>`   A project access token with *write* scope

## Dependencies

This script uses [`jq`](https://stedolan.github.io/jq/) and [`curl`](https://curl.haxx.se/).

## Notes

The script loops over the occurrences of the item until it finds any, but sometimes some occurrences are still remain.
If you want to make sure that all occurrences are deleted, just check the UI if there are any occurrences left and run
the script again.
