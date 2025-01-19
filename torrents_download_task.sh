#!/bin/bash

cd /data/annas/torrents_download_task

torrent_fn="torrent."`date "+%Y-%m-%d"`".json"
aria2c --all-proxy=http://192.168.100.2:10081 --out=$torrent_fn https://zh.annas-archive.org/dyn/torrents.json
jq -r '.. | .url? // empty' $torrent_fn > $torrent_fn".list.txt"
aria2c --all-proxy=http://192.168.100.2:10081  --follow-torrent=false --dir=torrents --check-integrity --continue=true --max-concurrent-downloads=50 --input-file  $torrent_fn".list.txt"
