#!/usr/bin/env python3
import base64,json,urllib.request,urllib.error,io,sys
from PIL import Image
def vis(path,prompt,maxw=520,np=120,ctx=4096):
    im=Image.open(path).convert('RGB'); w,h=im.size
    if w>maxw: im=im.resize((maxw,int(h*maxw/w)))
    buf=io.BytesIO(); im.save(buf,'JPEG',quality=80)
    b64=base64.b64encode(buf.getvalue()).decode()
    p={"model":"qwen3.5:9b","stream":False,
       "messages":[{"role":"user","content":prompt,"images":[b64]}],
       "options":{"num_predict":np,"temperature":0.1,"num_ctx":ctx}}
    req=urllib.request.Request("http://127.0.0.1:11434/api/chat",data=json.dumps(p).encode(),headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=900) as r: d=json.loads(r.read().decode()); return d.get("message",{}).get("content","")
    except urllib.error.HTTPError as e: return f"HTTP{e.code}: {e.read().decode()[:200]}"
print(vis(sys.argv[1],sys.argv[2]))
