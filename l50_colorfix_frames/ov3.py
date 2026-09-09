#!/usr/bin/env python3
import base64,sys,json,urllib.request,urllib.error,io
from PIL import Image
def go(path,prompt,model="qwen3.5:9b",np=200,maxw=896):
    im=Image.open(path).convert('RGB')
    r=maxw/float(im.width); 
    if r<1: im=im.resize((maxw,int(im.height*r)))
    buf=io.BytesIO(); im.save(buf,'JPEG',quality=82)
    b64=base64.b64encode(buf.getvalue()).decode()
    payload={"model":model,"stream":False,
      "messages":[{"role":"user","content":prompt,"images":[b64]}],
      "options":{"num_predict":np,"temperature":0.1,"num_ctx":12288},
      "keep_alive":"20m"}
    req=urllib.request.Request("http://127.0.0.1:11434/api/chat",data=json.dumps(payload).encode(),
        headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=600) as res:
            d=json.loads(res.read().decode())
            return d.get("message",{}).get("content","")
    except urllib.error.HTTPError as e:
        return f"HTTP{e.code}: {e.read().decode()[:400]}"
if __name__=="__main__":
    print(go(sys.argv[1],sys.argv[2]))
