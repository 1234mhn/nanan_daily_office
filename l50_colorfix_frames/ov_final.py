#!/usr/bin/env python3
import base64,sys,json,urllib.request,urllib.error,io
from PIL import Image
def go(path,prompt,maxw=1400,np=260,num_ctx=4608,model="qwen3.5:9b"):
    im=Image.open(path).convert('RGB')
    r=maxw/float(im.width)
    if r<1: im=im.resize((maxw,int(im.height*r)))
    buf=io.BytesIO(); im.save(buf,'JPEG',quality=84)
    b64=base64.b64encode(buf.getvalue()).decode()
    payload={"model":model,"stream":False,
      "messages":[{"role":"user","content":prompt,"images":[b64]}],
      "options":{"num_predict":np,"temperature":0.0,"num_ctx":num_ctx},
      "keep_alive":"50m"}
    req=urllib.request.Request("http://127.0.0.1:11434/api/chat",data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=900) as res:
            d=json.loads(res.read().decode())
            return d.get("message",{}).get("content",json.dumps(d)[:200])
    except urllib.error.HTTPError as e:
        return f"HTTP{e.code}: {e.read().decode()[:500]}"
    except Exception as e:
        return f"ERR {type(e).__name__}: {e}"
if __name__=="__main__":
    print(go(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else "describe"))
