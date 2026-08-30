#!/usr/bin/env python3
# 每周日生成下周各学生词根复习计划，打印为飞书消息文本
import json, urllib.request, urllib.parse, datetime, re

secret = ""
cfg = json.load(open('/root/.openclaw/openclaw.json'))
def walk(o):
    global secret
    if isinstance(o, dict):
        for k, v in o.items():
            if k == 'appSecret' and isinstance(v, str) and len(v) >= 20:
                secret = v
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)
walk(cfg)

def get_token():
    data = urllib.parse.urlencode({
        "app_id": "cli_aa040f2097f9dcde", "app_secret": secret,
        "grant_type": "client_credentials"}).encode()
    d = json.loads(urllib.request.urlopen(urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=data, headers={"Content-Type": "application/x-www-form-urlencoded"}), timeout=15).read().decode())
    return d["tenant_access_token"]

def read_records(app, table):
    tt = get_token()
    hdr = "Bearer " + tt
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app}/tables/{table}/records?page_size=200"
    req = urllib.request.Request(url, headers={"Authorization": hdr})
    d = json.loads(urllib.request.urlopen(req, timeout=20).read().decode())
    return d["data"]["items"]

DIARY_APP = "DIOvb4JoLa6oTisvKHGcCCEjnvh"
DIARY_TABLE = "tblFsRNfrvrTncCG"

def main():
    items = read_records(DIARY_APP, DIARY_TABLE)
    # 按学生分组，取每个学生最近一周(7天)的课，汇总词根
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())  # 本周一
    next_week = today + datetime.timedelta(days=7 - today.weekday())  # 下周一
    week_days = [(next_week + datetime.timedelta(days=i)) for i in range(7)]

    # 按学生收集本周所有课的"上课内容"
    by_student = {}
    for it in items:
        f = it["fields"]
        name = f.get("学生姓名")
        date = f.get("上课日期")
        content = str(f.get("上课内容") or '')
        if not name or not date: continue
        d = datetime.datetime.fromtimestamp(date/1000).date()
        if today - datetime.timedelta(days=6) <= d <= today:  # 近7天
            by_student.setdefault(name, []).append(content)

    today_str = today.strftime('%Y-%m-%d')
    print(f"# 词根复习计划生成 {today_str}")
    if not by_student:
        print("(近7天无上课记录，无计划)")
        return

    for name, contents in by_student.items():
        print(f"\n=== {name} ===")
        print(f"近期上课内容片段:")
        for c in contents:
            print(f"  - {c[:80]}")
    print("\n# 下一步：从以上内容提取词根，排成下周每日2词根计划")

if __name__ == "__main__":
    main()
