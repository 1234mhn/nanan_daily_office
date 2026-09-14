#!/bin/bash
set -u
COS=/root/.openclaw/workspace/skills/tencent-cos-skill/scripts/cos_node.mjs
P=media/korean_course/videos

# 52课用 v4（用户选"中间的那个"）
echo "=== 52课 v4 核对 ==="
ls -la out4/ep5_lesson52_2530-2703.mp4
echo "=== 53课 v2 核对 ==="
ls -la out2/ep5_lesson53_2813-2924.mp4
echo "=== 54课 v2 核对 ==="
ls -la out2/ep5_lesson54_3621-3821.mp4

echo "=== 覆盖上传 ==="
node $COS upload --file out4/ep5_lesson52_2530-2703.mp4 --key "$P/ep5_lesson52_2530-2703.mp4" 2>&1 | tail -5
node $COS upload --file out2/ep5_lesson53_2813-2924.mp4 --key "$P/ep5_lesson53_2813-2924.mp4" 2>&1 | tail -5
node $COS upload --file out2/ep5_lesson54_3621-3821.mp4 --key "$P/ep5_lesson54_3621-3821.mp4" 2>&1 | tail -5

echo "=== 上传后核对 ==="
node $COS list --prefix "$P/ep5_lesson5" --max-keys 20 2>&1 | python3 -c "
import sys,json
d=json.load(sys.stdin)
for f in d['files']:
    if any(x in f['key'] for x in ['lesson52_2530','lesson53_2813','lesson54_3621']):
        print(f['key'], round(f['size']/1048576,1),'MB', f['lastModified'], f['etag'][:20])
"
