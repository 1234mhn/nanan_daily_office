#!/bin/bash
set -u
COS=/root/.openclaw/workspace/skills/tencent-cos-skill/scripts/cos_node.mjs
OUT=/root/.openclaw/workspace/l52_54_colorfix
mkdir -p $OUT/frames4 $OUT/out4
KEY=ep5_lesson52_2530-2703.mp4
URL=$(node $COS sign-url --key "media/korean_course/videos/$KEY" --expires 7200 2>/dev/null | python3 -c "import sys,json;print(json.load(sys.stdin)['url'])")

sample(){ echo -n "  $1: "; for t in 8 20 40; do ffmpeg -v error -ss $t -i "$2" -vf "format=yuv444p,signalstats,metadata=print:file=-" -frames:v 1 -f null - 2>&1 | grep -oE "YAVG=[0-9.]+|SATAVG=[0-9.]+" | head -2 | tr '\n' ' '; done; echo; }

sample "原始" "$URL"
# v4: 回到 -0.13 档，但饱和度再降一点 -> 目标 Y≈105 附近
ffmpeg -v error -i "$URL" -vf "format=yuv420p,eq=brightness=-0.135:saturation=0.80:contrast=1.03,format=yuv420p" \
  -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
  -c:a copy "$OUT/out4/$KEY" -y
sample "v4" "$OUT/out4/$KEY"
ffmpeg -v error -ss 20 -i "$URL" -frames:v 1 -q:v 2 "$OUT/frames4/L52_b.jpg" -y
ffmpeg -v error -ss 20 -i "$OUT/out4/$KEY" -frames:v 1 -q:v 2 "$OUT/frames4/L52_a.jpg" -y
ls -la "$OUT/out4/$KEY" | awk '{print "  size:",$5}'
