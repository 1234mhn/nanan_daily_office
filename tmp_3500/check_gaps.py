words=[w.strip().lower() for w in open('wordlist.txt') if w.strip()]
# 用户已收录的词根(含变体)，判断补漏：扫描候选词根，找"词表里能带2+词、但用户版本漏了"
# 已收录 (拿豆包清单所有含词根的展示拆分)
have=['spect','spec','spic','duc','duct','port','ced','ceed','cess','fer','fac','fic','fect','fact',
'act','ag','ject','form','ceiv','cept','ceive','vis','vid','tend','tens','tent','pos','pon','posit',
'rupt','mit','miss','pend','pens','press','tract','grad','gress','cident','cad','cas','cid','cur','curs','curr',
'ven','vent','sens','sent','solv','solu','solut','val','valu','viv','vit','fin','struct','vers','vert','pel','puls',
'cred','nat','nasc','man','manu','pet','sequ','secut','sci','spond','spons','clud','clus','log','loqu','sum','sume','sumpt',
'bio','cern','cert','gen','gener','lect','leg','lig','flect','flex','tribute','volv','volut','audi','sign','opt','scrib','script',
'don','dot','dat','dur','err','graph','gram','loc','memor','mem','ped','spir','spira','circ','cycl','fort','forc','sim','simil',
'serv','urb','phon','prim','rect','test','turb']

def hits(sub):
    out=[]
    for w in words:
        if len(sub)>=3 and sub in w:
            out.append(w)
    return out

# 额外候选：3500常见但版本可能漏的
candidates = {
 'dict/dic':['dict'],          #说 predict dictation 版没有!
 'claim/clam':['claim','clam'],
 'flect/flex':['flect','flex'],
 'sist':['sist','stit'],           # resist
 'move/mob/mot/mutch':['move','mob','mut','mot'],  # 动的词族(版里无 mot)
 'ward':[], 'able':[],
 'jun':['jun'], 'major':[],
 'press':['press'],
 'dict':['dict'],
 'aware':[], 'scribe':[],
 'ordinary/order':['order','ordin'],
 'path/pathy':['path'],           # sympathy 版漏 path!
 'doc/doct':['doc','doct'],
 'mort':['mort'],
 'nov':['nov'],                    # novel innovate
 'lumin':['lumin','lustr'],
 'sol':[],  # sun/soli
 'locu':[],
 'fug':[],
 'viol':['viol'],
 'habit/hibit':['habit','hibit'],
 'vit':['vit'],
 'toler':['toler'],
 'trib':['trib','tribut'],
 'liter':['liter'],
 'med/medi':['medi','med'],
 'mod':['mod'],
 'mon':['mon'], 
 'oper':['oper'],
 'pac':['pac'],
 'part':['part'],  # 部分 participate
 'centr':['centr'],
 'cogn':['cogn'],
 'commun':[],
 'cap/capit':['capit','cap'],
 'card/cord':['cord'],
 'carn':[],
 'cid':[],
 'cit':['cit'],  # excite city 不太算根,skip
 'clar':['clar'],
 'clin':['clin'],
 'habit':[],
}
print("=== 词表里能带词的候选根，检查是否补漏(列出命中的) ===")
for disp,vs in candidates.items():
    for v in vs:
        h=hits(v)
        if len(h)>=2:
            hv=[x for x in h]
            print(f"{disp:22s} 命中{len(h):3d}: {hv[:8]}")
