import base64, json, sys, urllib.request, time, os

KEY = "a6b812027dfd46a487e747d555e916a4.c2m6hD16qyzVv0d6"
URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
PROMPT = "请输出这张PPT页面上的全部文字（标题、正文、公式、图注、引用），若页面只有图片/示意图，请简述其结构与标注。不要编造。"


def ocr(path, prompt=PROMPT, tries=6):
    b = base64.b64encode(open(path, 'rb').read()).decode()
    payload = {"model": "glm-4.6v-flash", "messages": [{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": b}},
        {"type": "text", "text": prompt}]}], "temperature": 0.1}
    last = ""
    for i in range(tries):
        req = urllib.request.Request(URL, data=json.dumps(payload).encode(),
                                     headers={"Authorization": "Bearer " + KEY,
                                              "Content-Type": "application/json"})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=180))
            return r["choices"][0]["message"]["content"]
        except Exception as e:
            last = str(e)
            time.sleep(15 * (i + 1))
    return f"[ERROR {last}]"


if __name__ == "__main__":
    d = sys.argv[1]
    out = sys.argv[2]
    done = set()
    if os.path.exists(out):
        for line in open(out):
            if line.startswith('===== PAGE '):
                done.add(line.split()[2])
    pages = [p for p in sorted(os.listdir(d)) if p not in done]
    with open(out, 'a') as f:
        for p in pages:
            t = ocr(os.path.join(d, p))
            f.write(f"\n===== PAGE {p} =====\n{t}\n")
            f.flush()
            print(p, "ok", flush=True)
            time.sleep(3)
    print("DONE")
