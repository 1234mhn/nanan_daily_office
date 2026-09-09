#!/bin/bash
# probe grade variants on given source abs times, save jpg to cmp dir
set -u
URL=$(cat /tmp/src_url.txt)
OUT=/root/.openclaw/workspace/l50_colorfix_frames/cmp
mkdir -p "$OUT"
probe(){ # t variantname filterstring
  local t="$1" name="$2" vf="$3"
  timeout 120 ffmpeg -y -hide_banner -loglevel error -ss "$t" -i "$URL" \
    -frames:v 1 -vf "$vf" -q:v 3 "$OUT/${name}_t${t}.jpg"
}
# F0 base chain function of npl
# probes as separate invocations:
