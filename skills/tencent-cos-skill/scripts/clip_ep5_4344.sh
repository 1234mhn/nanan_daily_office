#!/bin/bash
# Clip EP5 lessons 43 & 44 from COS signed URL (HDR->SDR, no full download)
URL=$(tr -d '\r\n' < /tmp/ep5_signed_url.txt)
echo "URL length: ${#URL}"

clip() {
  local start=$1 end=$2 out=$3
  echo "Clipping ${start}-${end} -> $out"
  ffmpeg -loglevel error -ss "$start" -to "$end" -i "$URL" \
    -map 0:v -map 0:a:0 \
    -vf "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,format=yuv420p,scale=1920:1080" \
    -c:v libx264 -crf 22 -preset fast -c:a aac -b:a 192k "$out" -y \
    && echo "OK $out" || echo "FAIL $out"
}

clip 549 576 /tmp/ep5_lesson43_0909-0936.mp4
clip 691 732 /tmp/ep5_lesson44_1131-1212.mp4
echo "ALL CLIPS DONE"
ls -la /tmp/ep5_lesson43_0909-0936.mp4 /tmp/ep5_lesson44_1131-1212.mp4 2>/dev/null
