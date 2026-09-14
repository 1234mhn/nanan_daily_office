#!/bin/bash
# 52-54课 色调统一修复 — 对标51课基准（Y≈102, SAT≈14）
# 铁律：不下载原片、不删对象、不改页面；只读签名URL→调色→覆盖同名KEY
set -u
COS=/root/.openclaw/workspace/skills/tencent-cos-skill/scripts/cos_node.mjs
PREFIX=media/korean_course/videos
OUT=/root/.openclaw/workspace/l52_54_colorfix
mkdir -p $OUT/frames $OUT/out

sign() { node $COS sign-url --key "$1" --expires 7200 2>/dev/null | python3 -c "import sys,json;print(json.load(sys.stdin)['url'])"; }

# 课号:文件名:调色链
run() {
  local tag="$1" key="$2" vf="$3"
  echo "=================== $tag  $key"
  local url; url=$(sign "$PREFIX/$key")
  [ -z "$url" ] && { echo "!! sign failed"; return 1; }

  echo "-- 修复前抽帧"
  ffmpeg -v error -ss 8 -i "$url" -vf "format=yuv444p,signalstats,metadata=print:file=-" -frames:v 1 -f null - 2>&1 | grep -oE "YAVG=[0-9.]+|SATAVG=[0-9.]+" | tr '\n' ' '; echo
  ffmpeg -v error -ss 20 -i "$url" -frames:v 1 -q:v 2 "$OUT/frames/${tag}_before.jpg" -y

  echo "-- 调色+重编码"
  ffmpeg -v error -i "$url" -vf "${vf}" \
    -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p \
    -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
    -c:a copy "$OUT/out/$key" -y
  [ -s "$OUT/out/$key" ] || { echo "!! encode failed"; return 1; }

  echo "-- 修复后抽帧"
  ffmpeg -v error -ss 8 -i "$OUT/out/$key" -vf "format=yuv444p,signalstats,metadata=print:file=-" -frames:v 1 -f null - 2>&1 | grep -oE "YAVG=[0-9.]+|SATAVG=[0-9.]+" | tr '\n' ' '; echo
  ffmpeg -v error -ss 20 -i "$OUT/out/$key" -frames:v 1 -q:v 2 "$OUT/frames/${tag}_after.jpg" -y
  ls -la "$OUT/out/$key"
}

run L52 ep5_lesson52_2530-2703.mp4 "format=yuv420p,eq=brightness=-0.10:contrast=0.96:saturation=0.94,format=yuv420p"
run L53 ep5_lesson53_2813-2924.mp4 "format=yuv420p,eq=brightness=-0.03:contrast=1.02:saturation=0.98,format=yuv420p"
run L54 ep5_lesson54_3621-3821.mp4 "format=yuv420p,hue=s=0.80,eq=contrast=0.97,format=yuv420p"
echo "=== DONE ==="
