#!/bin/bash
### Delete all occurrences of a Rollbar item

### Parameters
# The item counter from the item url: https://rollbar.com/<account>/<project>/item/<ITEM_COUNTER>/
ITEM_COUNTER="$1"
# A project access token with 'read' scope
READ_TOKEN="$2"
# A project access token with 'write' scope
WRITE_TOKEN="$3"


HOST='https://api.rollbar.com'
API="$HOST/api/1"

item_id=$(curl -s -k "$API/item_by_counter/$ITEM_COUNTER?access_token=$READ_TOKEN" | jq .result.itemId)
page=1
tmp_file=$(mktemp /tmp/rollbar.XXX)

while :
do
    printf "\n\nDeleting occurrences of https://rollbar.com/item/$item_id from page $page\n\n"

    curl -s -k "$API/item/$item_id/instances?page=$page&access_token=$READ_TOKEN" | \
	jq .result.instances[].id > "$tmp_file"

    < "$tmp_file" xargs -P20 -I instance_id curl -s -k -XDELETE "$API/instance/instance_id?access_token=$WRITE_TOKEN"

    if [ $(wc -l < $tmp_file) -eq 0 ]
    then break
    else ((page++))
    fi
done

rm -rf "$tmp_file"
