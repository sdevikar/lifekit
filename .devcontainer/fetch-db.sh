#!/usr/bin/env bash
# Fetch the dogfood product DB snapshot for this codespace.
# The DB is attached as an asset on the private release tag dogfood-db-v1
# (see STATUS.md); the codespace's automatic GITHUB_TOKEN authorizes the
# download. Re-upload a fresh asset to refresh the snapshot.
set -euo pipefail
mkdir -p ~/.lifekit
ASSET_URL=$(python3 - <<'EOF'
import json, os, urllib.request
req = urllib.request.Request(
    'https://api.github.com/repos/sdevikar/lifekit/releases/tags/dogfood-db-v1',
    headers={'Authorization': 'Bearer ' + os.environ['GITHUB_TOKEN'],
             'Accept': 'application/vnd.github+json'})
print(json.load(urllib.request.urlopen(req))['assets'][0]['url'])
EOF
)
curl -sSL -H "Authorization: Bearer $GITHUB_TOKEN" \
     -H 'Accept: application/octet-stream' \
     "$ASSET_URL" -o ~/.lifekit/lifekit.db
ls -la ~/.lifekit/lifekit.db
