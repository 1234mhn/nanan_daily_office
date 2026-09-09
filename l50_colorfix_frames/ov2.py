#!/usr/bin/env python3
import base64,sys,json,urllib.request,urllib.error
def chat_vis(path,prompt,model="qwen3.5:9b",num_predict=300):
    with open(path,'rb') as f: b64=base64.b64encode(f.read()).decode()
    payload={"model":model,"stream":False,
      "messages":[{"role":"user","content":prompt,
                   "images":[b64]}],
      "options":{"num_predict":num_predict,"temperature":0.2}}
    req=urllib.request.Request("http://127.0.0.1:11434/api/chat",data=json.dumps(payload).encode(),
        headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=400) as r:
        return json.loads(r.read().decode()).get("message",{}).get("content","")
if __name__=="__main__":
    print(chat_vis(sys.argv[1], sys.argv[2] if len(sys.argv)>1 else "describe"))
