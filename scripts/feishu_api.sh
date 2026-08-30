#!/usr/bin/env bash
# 飞书应用身份 API 封装：用 appSecret 自动签发 tenant token（不过期、无需扫码）
# 用法:
#   ./feishu_api.sh read <app_token> <table_id> [page_size]
#   ./feishu_api.sh fields <app_token> <table_id>
#   ./feishu_api.sh create <app_token> <table_id> '<fields_json>'
#   ./feishu_api.sh batch_create <app_token> <table_id> '<records_json>'
#   ./feishu_api.sh update <app_token> <table_id> <record_id> '<fields_json>'

set -euo pipefail
APP_ID="cli_aa040f2097f9dcde"
CONFIG="/root/.openclaw/openclaw.json"
TOKEN_FILE="/tmp/feishu_tenant_token.json"

# 从 openclaw.json 读 appSecret
get_secret() {
  python3 - <<'PY'
import json
cfg = json.load(open("/root/.openclaw/openclaw.json"))
found = None
def walk(o):
    global found
    if isinstance(o, dict):
        for k,v in o.items():
            if 'secret' in k.lower() and isinstance(v,str) and len(v)>=20:
                found = v
            walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
walk(cfg)
print(found)
PY
}

# 获取 tenant token（带缓存，接近过期才刷新）
get_token() {
  local now=$(date +%s)
  if [ -f "$TOKEN_FILE" ]; then
    local exp=$(python3 -c "import json;print(json.load(open('$TOKEN_FILE')).get('expire_at',0))" 2>/dev/null || echo 0)
    if [ "$now" -lt "$((exp - 600))" ]; then
      python3 -c "import json;print(json.load(open('$TOKEN_FILE'))['token'])"
      return
    fi
  fi
  local secret=$(get_secret)
  local resp=$(curl -s -m 15 -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "app_id=$APP_ID" \
    --data-urlencode "app_secret=$secret" \
    --data-urlencode "grant_type=client_credentials")
  local code=$(echo "$resp" | python3 -c "import json,sys;print(json.load(sys.stdin).get('code',''))" 2>/dev/null)
  if [ "$code" != "0" ]; then
    echo "ERROR 签发token失败: $(echo "$resp" | head -c 200)" >&2
    return 1
  fi
  local tok=$(echo "$resp" | python3 -c "import json,sys;print(json.load(sys.stdin)['tenant_access_token'])")
  # expire ~ 7200s
  python3 -c "import json;json.dump({'token':'$tok','expire_at':$(date +%s)+7200}, open('$TOKEN_FILE','w'))"
  echo "$tok"
}

CMD="${1:-read}"
TOKEN=$(get_token) || exit 1

case "$CMD" in
  read)
    # read <app> <table>
    curl -s -m 20 "https://open.feishu.cn/open-apis/bitable/v1/apps/$2/tables/$3/records?page_size=${4:-200}" \
      -H "Authorization: Bearer $TOKEN" ;;
  fields)
    curl -s -m 20 "https://open.feishu.cn/open-apis/bitable/v1/apps/$2/tables/$3/fields?page_size=100" \
      -H "Authorization: Bearer $TOKEN" ;;
  create)
    curl -s -m 20 -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/$2/tables/$3/records" \
      -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
      -d "{\"fields\":$4}" ;;
  batch_create)
    curl -s -m 20 -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/$2/tables/$3/records/batch_create" \
      -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
      -d "{\"records\":$4}" ;;
  update)
    curl -s -m 20 -X PUT "https://open.feishu.cn/open-apis/bitable/v1/apps/$2/tables/$3/records/$4" \
      -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
      -d "{\"fields\":$5}" ;;
  *) echo "未知命令: $CMD" >&2; exit 1 ;;
esac
