import re, sys
sys.path.insert(0,'.')
# 重新定义精简干净的词根表(纯展示名->命中会偏，需干净库)
from roots_lib import ROOTS
words=[w.strip().lower() for w in open('wordlist.txt') if w.strip()]
# 排除过短/过于普通的基础词影响不大，全量参与
result={}
meta={}
for disp, variants in ROOTS.items():
    if not variants: continue
    # 归一化变体
    hits=[]
    for w in words:
        wl=w
        # 变体匹配：作为子串(词根常出现在词内)
        for v in variants:
            if len(v)>=3 and v in wl:
                hits.append(w)
                break
    # 去重(一个词可能命中同一根多次)
    hits=list(dict.fromkeys(hits))
    result[disp]=len(hits)
    meta[disp]=hits[:6]
# 排序
ranked=sorted(result.items(), key=lambda x:-x[1])
print("词根数:",len(ranked)-sum(1 for r in ranked if r[1]==0))
print("=== 命中词表词前50(排除0) ===")
cnt=0
for disp,n in ranked:
    if n==0: continue
    cnt+=1
    if cnt>50: break
    print(f"{n:3d}  {disp:16s} {meta[disp]}")
