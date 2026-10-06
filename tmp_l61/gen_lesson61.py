# -*- coding: utf-8 -*-
"""Generate lesson61.html from lesson54 template structure."""
import html

VIDEO = "https://korean-video-1433876150.cos.ap-guangzhou.myqcloud.com/media/korean_course/videos/ep7_lesson61_10-83.mp4"

# (start, end, kr, cn, en, words[list of (w,mean)], phrase, pattern_html, ex1, ex2, phontxt)
lines = [
 (24.62,25.91,"형은? / 어, 호진아","哥呢？ / 哦，浩镇","-Where is he? / -Hey, Ho-jin.",
  [("형","哥（男生对年长男性）"),("호진","浩镇（人名）"),("아","喂/哎（接名字后，叫熟人）")],
  "형은? — 哥呢？（问“哥在哪”）；语气随性",
  "<b>名词 + 은/는?「……呢？」</b>；有收音+은，无收音+는。",
  "엄마는? → 妈呢？","지선이는? → 智善呢？",
  "호진아 [호지나] 连读（ㄴ + 아）；아 轻声"),
 (35.09,38.17,"형, 일어나, 형, 어?","哥，起来吧，哥","Hey, get up. Come on, get up.",
  [("형","哥"),("일어나다","起来/起身"),("어","啊/喂（催促语气）")],
  "일어나 — 起来（命令/劝诱形）；反复呼喊 형 表急切",
  "<b>动词词干 + 아/어（口语命令）「……吧」</b>。",
  "앉아. → 坐吧。","먹어. → 吃吧。",
  "일어나 [이러나] 收音 ㄹ 弱化、连读顺滑"),
 (38.67,40.22,"어, 호진아","哦，浩镇","Hey, Ho-jin.",
  [("어","哦/嗯（应答、恍然）"),("호진","浩镇"),("아","呼唤词")],
  "어 + 人名 + 아 — “哦，某某”（认出来）",
  "<b>名字有收音 + 아，无收音 + 야</b>；호진 有收音 ㄴ → 호진아（亲昵呼唤）。",
  "민수야. → 民秀呀。","철수야. → 哲秀呀。",
  "호진아 [호지나] 连读（ㄴ + 아）"),
 (41.09,42.89,"왜 창피하게 밖에서 울고 있어?","干吗在外面哭，不丢脸吗？","Why are you crying in public? You're embarrassing yourself.",
  [("왜","为什么/干吗"),("창피하다","丢脸/羞耻"),("밖","外面"),("-에서","在……（地点）"),("울다","哭")],
  "창피하게 — 丢人地（副词形，反问语气）",
  "<b>왜 + 副词形 + 动词现在时?「干吗……（反问/责怪）」</b>。",
  "왜 여기서 자고 있어? → 干吗在这儿睡？","왜 그렇게 말해? → 干吗那么说？",
  "밖에서 [바께서] ㄱ 紧音化；창피하게 连读顺滑"),
 (43.39,44.34,"일어나, 가자, 자","起来吧，我们走","Let's go.",
  [("가다","去/走"),("자","来/走（语助词，催促、引路）")],
  "가자 — 走吧（劝诱形）；자 重复催促",
  "<b>动词词干 + 자「咱们……吧」</b>。",
  "먹자. → 吃吧。","집에 가자. → 回家吧。",
  "无特殊变化；자 短促轻读"),
 (46.56,50.23,"야, 신지선이 무슨 내가 먼저 헤어지자 그랬대","喂，申智善说是我先提的分手","Guess what? Shin Ji-sun said I broke up with her first.",
  [("야","喂（叫熟人）"),("신지선","申智善（人名）"),("무슨","什么/怎么（表不解、反驳）"),("먼저","先"),("헤어지다","分手"),("-대","（转述）说……")],
  "헤어지자 그랬대 — 说（我）提了分手（转述+引述）",
  "<b>动词 + 자고 하다「说要……」</b>；<b>-대 = -다고 해（听说/转述）</b>。",
  "내가 먼저 가자고 했대. → 说是我先说要走的。","그 사람이 사랑한대. → 他说他爱。",
  "그랬대 [그랬때] ㄷ 紧音化；헤어지자 连读"),
 (50.31,52.44,"나는 진짜 그런 적이 없는데","我真的没有那样过啊","But I never did.",
  [("진짜","真的"),("그런","那样的"),("적","时候/次数（表经历）"),("-없다","没有")],
  "그런 적이 없다 — 从没那样过（经历否定）",
  "<b>动词过去 + ㄴ/은 적이 없다「从没……过」</b>。",
  "거짓말한 적이 없어요. → 从没撒过谎。","본 적이 없어요. → 从没见过。",
  "없는데 [업는데] ㅄ 收音简化；적으로 连读"),
 (53.10,56.73,"나보고 잘 생각해 보라고 하는데 난 진짜 그런 적이 없거든?","她让我好好想想，可我真没那样过啊","She told me to think carefully, but I swear I never did.",
  [("나보고","对我（说）/让我"),("생각하다","想"),("-라고 하다","说（让）……"),("-거든","表强调理由/提醒")],
  "생각해 보라고 하다 — 让我好好想想",
  "<b>动词 + (으)라고 하다「让（某人）做……」</b>；<b>句尾 -거든「……嘛/你不知道吗」</b>。",
  "나보고 기다리라고 했어. → 让我等着。","천천히 하라고 했어. → 让慢慢来。",
  "없거든 [업꺼든] ㅄ 紧音化；생각해 连读"),
 (57.23,59.28,"그래, 생각을 해도","好，就算要想","Sure.",
  [("그래","好/行（回应）"),("생각","想法/想"),("-아/어도","即使……也")],
  "생각을 해도 — 就算想（让步）",
  "<b>动词 + 아/어도「即使……也……」</b>（让步连接）。",
  "가도 돼요? → 去也行吗？","힘들어도 해요. → 累也要做。",
  "해도 [해도] ㅎ 弱化自然；생각을 连读"),
 (59.36,60.61,"집에 가서 하자, 알았지?","回家再想吧，知道了吗？","Let's think about it at home.",
  [("집","家"),("-에 가서","去……然后"),("알다","知道"),("-지","确认/叮嘱语气")],
  "알았지? — 知道了吧？（征求同意/叮嘱）",
  "<b>动词 + 아/어서「……然后/因为……」</b>；<b>句尾 -지?「……吧？」</b>。",
  "내일 만나서 하자. → 明天见了再弄吧。","그렇지? → 对吧？",
  "알았지 [아랐찌] ㅆ 紧音化；집에 [지베] 连读"),
 (60.69,62.11,"자, 일어나, 일어나","来，起来，起来","Come on. Up you go.",
  [("자","来（催促）"),("일어나다","起来")],
  "일어나 重复 — 快起来（反复催促）",
  "<b>动词 + 아/어（命令），重复表急切</b>。",
  "빨리, 빨리. → 快点，快点。","가, 가. → 走，走。",
  "일어나 [이러나] 连读顺滑"),
 (62.20,64.62,"나 진짜 너무 화나고 너무 답답해","我真的又气又憋屈","I'm so angry and frustrated.",
  [("화나다","生气"),("답답하다","憋闷/郁闷（心里堵）"),("너무","太")],
  "화나고 답답해 — 又气又闷（两个形容词并列）",
  "<b>形容词/动词 + 고「……并且……」</b>（并列连接）。",
  "예쁘고 착해요. → 又漂亮又善良。","배고프고 피곤해요. → 又饿又累。",
  "화나고 连读；답답해 [답따패] ㄷ 紧音化"),
 (64.70,66.28,"내가 언제 그런 말을 했을까?","我什么时候说过那种话？","When did I ever say that?",
  [("언제","什么时候"),("말","话"),("-했을까","会……吗（推测疑问）")],
  "그런 말을 하다 — 说那种话",
  "<b>动词 + 았/었을까?「（过去）会……吗？」</b>（自问/反问）。",
  "내가 그걸 알았을까? → 我会知道那个吗？","그가 왔을까? → 他来了吗？",
  "했을까 [해쓸까] ㅆ 紧音化；말을 连读"),
 (66.37,67.49,"알았어, 똑바로","知道了，好好走","I get it. Just walk straight.",
  [("알았어","知道了（口语应答）"),("똑바로","好好地/直直地")],
  "똑바로 — 端端正正/好好（副词）",
  "<b>알았어 = 알겠어 的口语缩略</b>；똑바로 作副词修饰动词。",
  "똑바로 앉아. → 坐正。","똑바로 말해. → 好好说。",
  "알았어 [아라써] 连读+紧音化；똑바로 [똑빠로] ㄱ 紧音化"),
 (67.58,69.50,"똑바로 걸어 봐, 똑바로 걸어 / 알겠어","好好走一个看看，好好走 / 知道了","Okay. / Walk straight.",
  [("걷다","走（词干 걸-）"),("-아/어 봐","试……看"),("알겠어","知道了（标准而稍正式）")],
  "걸어 봐 — 走走看（试探/示范）",
  "<b>动词 + 아/어 보다「试试……」</b>；-아 봐「……看看」。",
  "먹어 봐. → 尝尝看。","해 봐. → 试试看。",
  "걸어 봐 [거러 봐] 连读；알겠어 [알게써] ㅆ 紧音化"),
 (70.00,70.83,"제대로 좀 걸어","给我好好走","Walk straight.",
  [("제대로","好好地/正确地"),("좀","一点/请（缓和语气）"),("걷다","走")],
  "제대로 좀 — 稍微好好地（带点不耐烦）",
  "<b>副词 + 좀 + 动词命令「给我……一点」</b>（催促里带情绪）。",
  "제대로 좀 해. → 给我好好做。","좀 빨리 와. → 快点来。",
  "걸어 [거러] 连读"),
]

# vocab summary (from content file, 16-sync)
vocab = [("형","哥"),("일어나다","起来"),("울다","哭"),("창피하다","丢脸"),("밖","外面"),
 ("헤어지다","分手"),("먼저","先"),("생각하다","想"),("진짜","真的"),("적","时候/经历"),
 ("화나다","生气"),("답답하다","憋闷"),("언제","什么时候"),("말","话"),("똑바로","好好地"),
 ("제대로","好好地"),("걷다","走"),("알다","知道"),("자","来（催促）"),("창피","丢脸")]

# pattern summary
patterns = [
 ("名词 + 은/는?","……呢？","형은?"),
 ("动词 + 아/어","……吧（命令）","일어나 / 가자"),
 ("动词 + 자","咱们……吧（劝诱）","가자"),
 ("动词 + (으)라고 하다","让（某人）做……","생각해 보라고 하는데"),
 ("动词 + ㄴ/은 적이 없다","从没……过","그런 적이 없는데"),
 ("动词 + 거든","……嘛（强调理由）","없거든"),
 ("动词 + 아/어도","即使……也","생각을 해도"),
 ("形容/动词 + 고","……并且……","화나고 답답해"),
 ("动词 + 았/었을까?","（过去）会……吗","했을까"),
 ("动词 + 아/어 보다","试试……","걸어 봐"),
]

tips = ("✨ 本课重点(深夜街头·失恋借酒场景)：① 名词 + 은/는?……呢？ ② 动词 + 아/어 命令「……吧」 "
 "③ 动词 + 자「咱们……吧」 ④ 나보고 + (으)라고 하다「让我……」 ⑤ -(으)ㄴ/는 적이 없다「从没……过」 "
 "⑥ 句尾 -거든「……嘛」 ⑦ 아/어도「即使……也」 ⑧ 고「……并且……」 ⑨ 았/었을까?「（过去）会……吗？」 "
 "⑩ 아/어 보다「试试……」")

E = html.escape
out = []
out.append('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>第61课 · 失恋喝酒</title>
<style>*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,sans-serif;background:#f0f2f5;color:#333}
.top{display:flex;align-items:center;padding:10px 16px;background:#1a1a2e;color:#fff}
.top{position:absolute;top:0;left:0;right:0;z-index:100}
.top .back{color:#fff;text-decoration:none;font-size:14px;cursor:pointer}
.top h2{flex:1;text-align:center;font-size:15px;font-weight:600}
.top .quiz-btn{background:rgba(255,255,255,.15);border:none;color:#fff;padding:4px 12px;border-radius:8px;font-size:12px;cursor:pointer}
.video-wrap{background:#000}
video{width:100%;display:block;background:#000}
.content{padding:12px}
.sec{font-size:14px;font-weight:600;padding:10px 0 6px;color:#333;cursor:pointer;user-select:none}
.line{margin-bottom:8px;border:1px solid #eee;border-radius:10px;overflow:hidden;background:#fff}
.line-hd{display:flex;align-items:center;padding:10px 14px;cursor:pointer;background:#fafafa;transition:background .3s ease,border .3s ease,box-shadow .3s ease}
.line-hd .arr{display:inline-block;transition:transform .2s;margin-right:8px;color:#999;font-size:12px}
.kr{font-size:15px;font-weight:600;color:#1a1a2e}
.cn{font-size:13px;color:#555;margin:4px 0 0 14px}
.en{font-size:12px;color:#888;margin:2px 0 0 14px}
.line-exp{padding:10px 14px;background:#fbfcfe;border-top:1px solid #eef}
.line-exp .item{margin:4px 0;font-size:13px;line-height:1.6}
.line-exp .ex{font-size:12.5px;color:#666;margin:3px 0 3px 14px}
.line-exp .ex .c{color:#2e7d32}
.line-exp .phon{font-size:12.5px;color:#8a6d3b;margin:6px 0}
.line-exp .m{color:#444}
.tip{font-size:12.5px;color:#555;line-height:1.75;background:#fffdf5;border:1px solid #f0e8c8;border-radius:10px;padding:10px 12px}
.done-toggle{width:100%;margin:16px 0 6px;padding:11px;border:none;border-radius:10px;background:#667eea;color:#fff;font-size:14px;font-weight:600;cursor:pointer}
.note-box{width:100%;min-height:80px;border:1px solid #ddd;border-radius:10px;padding:10px;font-size:13px;font-family:inherit}
.note-status{font-size:12px;color:#2ecc71;margin-left:6px}
.speak-practice-toggle{width:100%;margin:10px 0 0;padding:11px;border:none;border-radius:10px;background:#f39c12;color:#fff;font-size:14px;font-weight:600;cursor:pointer}
.speak{background:none;border:none;font-size:15px;cursor:pointer;padding:2px 6px}
</style></head><body>
<div class="top"><a class="back" href="index.html">← 返回</a><h2>第61课 · 失恋喝酒</h2><button class="quiz-btn" onclick="toggleQuiz(61)">测验模式</button></div>
<div class="video-wrap"><video controls preload="auto" src="''' + VIDEO + '''"></video></div>
<div class="content">
<div class="sec">📝 台词（点击展开讲解）</div>''')

for i,(s,e,kr,cn,en,words,phrase,pattern,ex1,ex2,phon) in enumerate(lines,1):
    out.append(f'\n<div class="line" data-time-start="{s}" data-time-end="{e}">')
    out.append('  <div class="line-hd" onclick="toggleExp(this)">')
    out.append('    <span class="arr">▸</span>')
    out.append(f'    <p class="kr" style="flex:1">{i}. {E(kr)}</p>')
    out.append(f'''    <button class="speak" onclick="event.stopPropagation();handleSpeak(event,'{kr}')">🔊</button>''')
    out.append('  </div>')
    out.append(f'  <p class="cn">→ {E(cn)}</p>')
    out.append(f'  <p class="en" style="font-size:12px;color:#888;margin:2px 0 0 16px">→ {E(en)}</p>')
    out.append('  <div class="line-exp" style="display:none">')
    out.append('    <div class="item"><b>📍单词</b>')
    out.append('<div style="display:grid;grid-template-columns:1fr 1fr;gap:2px 16px;margin-top:4px">')
    for w,m in words:
        out.append(f'<div><b>{E(w)}</b> — {E(m)}</div>')
    out.append('</div>')
    out.append('</div>')
    out.append(f'    <div class="item"><b>💬 短语</b><br><span class="m">{E(phrase)}</span></div>')
    out.append(f'    <div class="item"><b>📌句型</b><br><span class="m">{pattern}</span></div>')
    out.append(f'    <div class="ex">💬例句1 <span class="c">{E(ex1)}</span></div>')
    out.append(f'    <div class="ex">💬例句2 <span class="c">{E(ex2)}</span></div>')
    out.append(f'    <div class="phon"><b>🎵 音变</b><br><span class="m">{E(phon)}</span></div>')
    out.append('  </div>')
    out.append('</div>')

out.append(f'\n\n<div class="sec">💡 小贴士</div>\n<p class="tip">{E(tips)}</p>')

# vocab
out.append('\n<div class="sec" onclick="toggleVocab(this)" style="cursor:pointer;user-select:none">\n<span style="display:inline-block;transition:transform .2s">▶</span> 📌 单词汇总\n</div>')
out.append('<div id="vocab61" style="display:none">\n<div style="display:grid;grid-template-columns:1fr 1fr;gap:4px 20px;margin:8px 0">')
for w,m in vocab:
    out.append(f'<div style="font-size:13px;padding:3px 0"><b>{E(w)}</b> — {E(m)}</div>')
out.append('</div>\n</div>')

# patterns
out.append('\n<div class="sec" onclick="togglePattern(this)" style="cursor:pointer;user-select:none">\n<span style="display:inline-block;transition:transform .2s">▶</span> 📖 句型总结\n</div>')
out.append('<div id="pattern61" style="display:none">\n<div style="margin:8px 0">')
for idx,(p,mn,ex) in enumerate(patterns,1):
    circ="①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰"[idx-1]
    out.append(f'''<div style="background:#f0f4ff;padding:10px 14px;border-radius:8px;margin:4px 0;border-left:3px solid #3498db">
<b>{circ} {E(p)} — {E(mn)}</b>
<div style="font-size:12px;color:#888">→ {E(ex)}</div>
</div>''')
out.append('</div>\n</div>')

out.append(f'''
<button class="done-toggle" data-lesson="61" onclick="toggleDone(61)">✓ 已完成学习</button>
<div class="sec">✏️ 笔记</div>
<textarea class="note-box" data-note="61" placeholder="在此输入笔记..."></textarea>
<span class="note-status" id="noteStatus61">✓ 已保存</span>
<button class="speak-practice-toggle" onclick="startPractice(61)">口语练习</button>
</div>

<script>
function handleSpeak(event,text){{
  event.stopPropagation();
  if('speechSynthesis' in window){{
    var msg=new SpeechSynthesisUtterance(text);
    msg.lang='ko-KR';
    speechSynthesis.speak(msg);
  }}
}}
function toggleExp(el){{
  var arr=el.querySelector('.arr'),exp=el.parentElement.querySelector('.line-exp');
  if(exp.style.display==='block'){{exp.style.display='none';arr.classList.remove('open')}}
  else{{exp.style.display='block';arr.classList.add('open')}}
}}
function toggleVocab(el){{var s=el.querySelector('span'),c=el.nextElementSibling;if(c.style.display==='none'){{c.style.display='block';s.style.transform='rotate(90deg)'}}else{{c.style.display='none';s.style.transform='rotate(0deg)'}}}}
function togglePattern(el){{var s=el.querySelector('span'),c=el.nextElementSibling;if(c.style.display==='none'){{c.style.display='block';s.style.transform='rotate(90deg)'}}else{{c.style.display='none';s.style.transform='rotate(0deg)'}}}}
function toggleQuiz(n){{alert('测验模式')}}
function toggleDone(n){{alert('已完成')}}
function startPractice(n){{alert('口语练习')}}
var video=document.querySelector('video');
if(video){{
  var lastActiveLine=null;
  video.addEventListener('timeupdate',function(){{
    var t=video.currentTime;
    var lines=document.querySelectorAll('.line');
    var currentLine=null;
    for(var i=0;i<lines.length;i++){{
      var lh=lines[i].querySelector('.line-hd');
      if(lh){{lh.style.background='';lh.style.border='';lh.style.boxShadow='';}}
    }}
    for(var i=0;i<lines.length;i++){{
      var s=parseFloat(lines[i].getAttribute('data-time-start'));
      var e=parseFloat(lines[i].getAttribute('data-time-end'));
      if(t>=s&&t<e){{
        var lh=lines[i].querySelector('.line-hd');
        if(lh){{lh.style.background='#e3f2fd';currentLine=lines[i];lastActiveLine=lines[i];break}}
      }}
    }}
    if(!currentLine&&lastActiveLine){{
      var lh=lastActiveLine.querySelector('.line-hd');
      if(lh){{lh.style.background='#e3f2fd';}}
      currentLine=lastActiveLine;
    }}
    if(currentLine){{
      var exp=currentLine.querySelector('.line-exp');
      var scrollTarget=currentLine;
      if(exp&&exp.style.display==='block'){{scrollTarget=exp;}}else{{scrollTarget=currentLine.querySelector('.line-hd');}}
      if(scrollTarget){{
        var rect=scrollTarget.getBoundingClientRect();
        if(rect.top<0 || rect.bottom>window.innerHeight){{scrollTarget.scrollIntoView({{behavior:"smooth",block:"center"}});}}
      }}
    }}
  }});
}}
(function(){{
  var v=document.querySelector('video');
  if(!v)return;
  var lines=document.querySelectorAll('.line');
  for(var i=0;i<lines.length;i++){{
    (function(el){{
      el.addEventListener('click',function(e){{
        var s=parseFloat(el.getAttribute('data-time-start'));
        if(!isNaN(s)){{v.currentTime=s;v.play()}}
      }});
    }})(lines[i]);
  }}
}})();
</script>
</body>
</html>''')

open('/www/korean_course/lesson61.html','w',encoding='utf-8').write(''.join(out))
print("lesson61.html written:", len(''.join(out)), "bytes")
