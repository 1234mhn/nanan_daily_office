# -*- coding: utf-8 -*-
"""给 lesson55.html / lesson56.html 的每句补英文行（.en），风格同 lesson61"""
import re

BASE='/www/korean_course'

EN55 = {
1:"→ That night, that night.",
2:"→ For the first time, I desperately wished",
3:"→ that my delusion would come true.",
4:"→ But the Earth can never reach the Sun,",
5:"→ and in the Seoul sky",
6:"→ no aurora appears.",
7:"→ Ho-jin.",
8:"→ Let's go back inside now.",
9:"→ You can keep watching until it's over.",
10:"→ No, it's fine.",
11:"→ I don't want to see the moment it disappears.",
12:"→ We watched it together as promised, so this is far enough for me.",
}

EN56 = {
1:"→ It's gone.",
2:"→ I told you to wait inside — why are you standing out here?",
3:"→ Were you scared because I said I'd kill you earlier?",
4:"→ I was scared for a second, but...",
5:"→ I'm waiting to find out why I should be scared at all.",
6:"→ ...that's what I'm waiting for.",
7:"→ Just pretend you didn't hear what you heard earlier.",
8:"→ Huh?",
9:"→ I'm not a very good liar.",
10:"→ The wedding being called off...",
11:"→ I just don't want people to know.",
12:"→ They'll all find out soon anyway.",
13:"→ Are you picking a fight with me?",
14:"→ Huh? You're the director who said you'd kill me first!",
15:"→ So you're not scared after I hit you — you're just messing with me for fun?",
16:"→ My reflexes are excellent — I used to be an athlete.",
17:"→ That's why I'm still alive and well.",
18:"→ The phone's ringing again.",
19:"→ Take it.",
20:"→ So I don't accidentally answer it again.",
}

def patch(num, enmap):
    p=f'{BASE}/lesson{num}.html'
    s=open(p,encoding='utf-8').read()
    cnt=0
    def repl(m):
        nonlocal cnt
        n=int(m.group(1)); body=m.group(0)
        if n not in enmap: return body
        cnt+=1
        en=enmap[n].replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
        return body + f'\n  <p class="en" style="font-size:12px;color:#888;margin:2px 0 0 16px">{en}</p>'
    # 在每句 <p class="cn">→ ...</p> 后追加 <p class="en">
    s=re.sub(r'<p class="cn">→ [^<]*</p>\n?', lambda m: m.group(0).rstrip('\n')+'\n', s)
    # 用更稳妥的方式：抓 <div class="line" ...> ... <p class="cn">...</p>
    out=[]
    pos=0
    for m in re.finditer(r'<p class="cn">(.*?)</p>', s, re.S):
        pass
    # 直接按顺序替换
    parts=re.split(r'(<p class="cn">.*?</p>)', s, flags=re.S)
    idx=0
    res=[]
    for part in parts:
        res.append(part)
        if part.startswith('<p class="cn">'):
            idx+=1
            if idx in enmap:
                en=enmap[idx].replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
                if idx==0: pass
                res.append(f'\n  <p class="en" style="font-size:12px;color:#888;margin:2px 0 0 16px">{en}</p>')
                cnt+=1
    s=''.join(res)
    open(p,'w',encoding='utf-8').write(s)
    print(f'lesson{num}.html: 补英文 {cnt} 条')

patch(55, EN55)
patch(56, EN56)
