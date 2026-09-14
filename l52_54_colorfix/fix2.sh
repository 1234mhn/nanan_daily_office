#!/bin/bash
# 52-54课 色调统一修复 v2 — 对标51课基准（Y≈102, SAT≈14）
# 修正v1错误：53课原偏暗应提亮；52/54降饱和力度加大
set -u
COS=/root/.openclaw/workspace/skills/tencent-cos-skill/scripts/cos_node.mjs
PREFIX=media/korean_course/videos
OUT=/root/.openclaw/workspace/l52_54_colorfix
mkdir -p $OUT/frames2 $OUT/out2

sign() { node $COS sign-url --key "$1" --expires 7200 2>/dev/null | python3 -c "import sys,json;print(json.load(sys.stdin)['url'])"; }

# 在正片多个点位（8/20/40秒）采样，避免片头帧误导
sample() {
  local f="$1"; local label="$2"
  echo -n "  $label: "
  for t in 8 20 40; do
    ffmpeg -v error -ss $t -i "$f" -vf "format=yuv444p,signalstats,metadata=print:file=-" -frames:v 1 -f null - 2>&1 \
      | grep -oE "YAVG=[0-9.]+|SATAVG=[0-9.]+" | head -2 | tr '\n' ' '
  done
  echo
}

run() {
  local tag="$1" key="$2" vf="$3"
  echo "=================== $tag  $key"
  local url; url=$(sign "$PREFIX/$key")
  [ -z "$url" ] && { echo "!! sign failed"; return 1; }

  ffmpeg -v error -ss 20 -i "$url" -frames:v 1 -q:v 2 "$OUT/frames2/${tag}_before.jpg" -y
  echo "  修复前:"; sample "$url" before

  ffmpeg -v error -i "$url" -vf "${vf}" \
    -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p \
    -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
    -c:a copy "$OUT/out2/$key" -y
  [ -s "$OUT/out2/$key" ] || { echo "!! encode failed"; return 1; }

  echo "  修复后:"; sample "$OUT/out2/$key" after
  ffmpeg -v error -ss 20 -i "$OUT/out2/$key" -frames:v 1 -q:v 2 "$OUT/frames2/${tag}_after.jpg" -y
  ls -la "$OUT/out2/$key" | awk '{print "  size:",$5}'
}

# 52: 偏亮+偏饱和 -> 压亮度 + 降饱和
run L52 ep5_lesson52_2530-2703.mp4 "format=yuv420p,eq=brightness=-0.13:saturation=0.82:contrast=1.03,format=yuv420p"
# 53: 偏暗偏灰 -> 提亮 + 略补饱和
run L53 ep5_lesson53_2813-2924.mp4 "format=yuv420p,eq=brightness=+0.06:saturation=1.15:contrast=1.02,format=yuv420p"
# 54: 过饱和 -> 大幅降饱和
run L54 ep5_lesson54_3621-3821.mp4 "format=yuv420p,hue=s=0.72,eq=contrast=0.98,format=yuv420p"
echo "=== DONE ==="
