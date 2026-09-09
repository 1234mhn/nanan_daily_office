#!/bin/bash
# Generate candidate grade probes on problem warm frames; then analyze.
set -u
URL=$(cat /tmp/src_url.txt)
OUT=/root/.openclaw/workspace/l50_colorfix_frames/cmp
mkdir -p "$OUT"
base="zscale=t=linear:npl=%NPL%,format=gbrpf32le,zscale=p=bt709,zscale=t=bt709:m=bt709:r=tv,format=yuv420p"
# We'll append optional post-grade (hue s) which operates on yuv chroma.
declare -A VAR
# name -> "NPL|postvf"
VAR[v0_base100]="100|"
VAR[v1_npl80_s95]="80|hue=s=0.95"
VAR[v2_npl80_s90]="80|hue=s=0.90"
VAR[v3_npl70_s90]="70|hue=s=0.90"
VAR[v4_npl60_s92]="60|hue=s=0.92"
VAR[v5_100_s88]="100|hue=s=0.88"
VAR[v6_npl80_s93_g97]="80|hue=s=0.93,eq=gamma=0.97"

for t in 1180 1195; do
  for name in "${!VAR[@]}"; do
    spec="${VAR[$name]}"; npl="${spec%%|*}"; post="${spec#*|}"
    vf="${base//%NPL%/$npl}"
    [ -n "$post" ] && vf="$vf,$post"
    echo ">> probe $name t=$t npl=$npl post=[$post]"
    if ! timeout 120 ffmpeg -y -hide_banner -loglevel error -ss "$t" -i "$URL" -frames:v 1 -vf "$vf" -q:v 3 "$OUT/${name}_t${t}.jpg" 2>/tmp/err.log; then
       echo "  FAIL: $(tail -2 /tmp/err.log)"
    fi
  done
done
echo "=== probe done ==="
ls -la "$OUT" | grep -E 'v[0-9]' | head
