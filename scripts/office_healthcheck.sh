#!/bin/bash
# 办公室健康检查 —— 只体检不动手，输出报告
# 用法: bash scripts/office_healthcheck.sh
# 设计原则：默认只读，删除类操作一律不自动执行，只报告

WS="/root/.openclaw/workspace"
cd "$WS" || exit 1

REPORT="/tmp/office_health_$(date +%Y%m%d).txt"
exec > >(tee "$REPORT") 2>&1

echo "================= 🏥 办公室健康检查 $(date '+%Y-%m-%d %H:%M') ================="
echo

echo "【1】磁盘空间"
df -h / | tail -1 | awk '{printf "  根分区: %s 已用 / %s 总量 (使用率 %s), 剩余 %s\n", $3, $2, $5, $4}'
USED=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$USED" -gt 85 ]; then echo "  ⚠️ 磁盘使用率超过85%，需要清理"; else echo "  ✅ 磁盘健康"; fi
echo

echo "【2】大目录 TOP10"
du -sh */ .[!.]*/ 2>/dev/null | sort -rh | head -10 | sed 's/^/  /'
echo

echo "【3】待清理垃圾文件"
TMPCOUNT=$(find . -maxdepth 3 \( -name "*.tmp" -o -name "*~" -o -name "*.bak_*" -o -name "*_backup_*" \) 2>/dev/null | grep -v node_modules | grep -v "\.git/" | wc -l)
echo "  临时/备份文件: $TMPCOUNT 个"
find . -maxdepth 3 \( -name "*.tmp" -o -name "*~" -o -name "*.bak_*" -o -name "*_backup_*" \) 2>/dev/null | grep -v node_modules | grep -v "\.git/" | head -10 | sed 's/^/    /'

EMPTYCOUNT=$(find . -maxdepth 3 -type d -empty 2>/dev/null | grep -v node_modules | grep -v "\.git/" | wc -l)
echo "  空目录: $EMPTYCOUNT 个"
find . -maxdepth 3 -type d -empty 2>/dev/null | grep -v node_modules | grep -v "\.git/" | head -10 | sed 's/^/    /'
echo

echo "【4】git 状态"
if [ -d .git ]; then
  DIRTY=$(git status --porcelain | wc -l)
  echo "  未提交改动: $DIRTY 项"
  [ "$DIRTY" -gt 0 ] && git status --porcelain | head -10 | sed 's/^/    /'
  LASTCOMMIT=$(git log -1 --format="%h %s (%ar)" 2>/dev/null)
  echo "  最新提交: $LASTCOMMIT"
  BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null)
  echo "  落后远程: ${BEHIND:-未知} 个提交"
else
  echo "  ⚠️ 非 git 仓库"
fi
echo

echo "【5】系统服务"
for svc in nginx ollama; do
  if systemctl is-active --quiet "$svc" 2>/dev/null; then echo "  ✅ $svc 运行中"; else echo "  ⚠️ $svc 未运行"; fi
done
echo

echo "【6】线上站点连通"
for url in "https://nannan2026.cn/korean/" "https://nannan2026.cn/korean-notes/"; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" -m 8 "$url" 2>/dev/null)
  if [ "$CODE" = "200" ]; then echo "  ✅ $url ($CODE)"; else echo "  ⚠️ $url ($CODE)"; fi
done
echo

echo "【7】负载与内存"
uptime | sed 's/^/  /'
free -h | grep -E "Mem|Swap" | sed 's/^/  /'
echo

echo "【8】cron 定时任务"
crontab -l 2>/dev/null | grep -v "^#" | grep -v "^$" | wc -l | xargs echo "  活跃任务数:"
echo

echo "================= 检查完毕 ================="
echo "报告已存: $REPORT"
echo "提示：本脚本只做只读检查，不会删除任何文件。"
