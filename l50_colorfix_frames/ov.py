#!/usr/bin/env python3
import base64, sys, json, urllib.request
def vis(path, prompt, model="qwen3.5:9b"):
    with open(path,'rb') as f:
        b64=base64.b64encode(f.read()).decode()
    payload={"model":model,"prompt":prompt,
        "images":[b64],"stream":False,
        "options":{"num_predict":600}}
    req=urllib.request.Request("http://127.0.0.1:11434/api/generate",
        data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=300) as r:
        d=json.loads(r.read().decode())
    return d.get("response","")
if __name__=="__main__":
    p=sys.argv[1]; pr=sys.argv[2] if len(sys.argv)>2 else "详细描述这个视频画面。"
    print(vis(p,pr))
