# 高中3500词可拆的高频希腊/拉丁词根（含发音变体），键=展示名
ROOTS = {
 # 拉丁动词根
 "spect": ["spect","spic","spis"],         # 看
 "ject": ["ject"],                          # 扔
 "port": ["port"],                          # 拿运
 "duct": ["duct","duc"],                    # 引导
 "dict": ["dict","dic"],                    # 说
 "mit/miss": ["mit","miss","mis","mitt"],   # 送
 "fer": ["fer"],                            # 带拿
 "pos/pon": ["pos","pon","posit","posi"],   # 放 (pos 太短会产生很多误命中，改用词根poun/posit)
 "tract": ["tract","trai"],                 # 拉
 "form": ["form"],                          # 形状
 "press": ["press","prim"],                 # 压 (press误伤少)
 "claim": ["claim","clam"],                 # 喊主张
 "rupt": ["rupt"],                          # 破
 "scribe/script": ["scrib","script"],       # 写
 "vers/vert": ["vers","vert"],              # 转
 "cede/ceed/cess": ["ceed","cede","cess"],  # 走让步
 "ven/vent": ["ven","vent"],                # 来
 "serve": ["serv","serva"],                 # 保服务
 "struct": ["struct","stru"],               # 建造
 "pend/pens": ["pend","pens"],              # 挂称
 "flect/flex": ["flect","flex"],            # 弯曲
 "mov/mot/mob": ["mov","mot","mob","movab"],# 动
 "volv/volu": ["volv","volu"],              # 滚转
 "puls/pel/pell": ["puls","pel","pell","peal"],# 推驱
 "vid/vis": ["vid","vis"],                  # 看
 "aud/audi": ["aud","audi"],                # 听
 "sent/sens": ["sent","sens"],              # 感觉
 "cred": ["cred"],                          # 相信
 "fid": ["fid"],                            # 信
 "sign": ["sign"],                          # 标记
 "fac/fic/fect": ["fect","fic","fac","fact","facil"],# 做 (fac/fact)
 "fact": ["fact"],
 "ten/tain/tent": ["tain","ten","tent","tin"],# 保持 (tain)
 "tain": ["tain"],
 "cov": ["cov","cover"],                    # 盖(用cover)
 "leg/lect": ["lect","leg"],                # 选读法 (lect 短)
 "cip/capt/cept": ["cept","ceive","cip","capt","ceiv"],# 拿取 (ceive)
 "ceive": ["ceive"],
 "corp": ["corp","corpor"],                 # 体
 "anim": ["anim"],                          # 生命气
 "dorm": ["dorm"],                          # 睡
 "dic/dict": [],
 "spir": ["spir"],                          # 呼吸神
 "aqua": ["aqua"],                          # 水
 "therm": ["therm","thermo"],               # 热
 "phon": ["phon","phone"],                  # 声
 "gram/graph": ["graph","gram","gramm"],    # 写画
 "bio": ["bio"],                            # 生命
 "geo": ["geo"],                            # 地
 "astr": ["astr","astro"],                  # 星
 "tele": ["tele"],                          # 远
 "scope": ["scope"],                        # 看器
 "meter/meter": ["meter","metr"],           # 测量
 "chron": ["chron"],                        # 时间
 "path": ["path","pathy","patho"],          # 感受病
 "auto": ["auto"],                          # 自
 "manu/man": ["manu","man","manip"],        # 手 (man 太短误伤)
 "ped": ["ped","pedi"],                     # 脚
 "dens": ["dens"],                          # 密
 "lumin": ["lumin"],                        # 光
 "nov": ["nov"],                            # 新
 "prim": ["prim","prem"],                   # 首
 "sci": ["sci"],                            # 知
 "doc/doct": ["doc","doct"],                # 教
 "med": ["med","medi"],                     # 中
 "mit/mis": [],
 "solv/sol": ["solv","solu"],               # 解
 "val/vail": ["val","vail","valu"],         # 强值
 "vary/ver": ["veri","var","viro"],         # 变(用var)
 "nounce/nunci": ["noun","nunci"],          # 报
 "min": ["min","mini"],                     # 小
 "magn/maj/max": ["magn","maj","max"],      # 大
 "multi": ["multi","mult"],                 # 多
 "uni": ["uni"],                            # 一
 "bi": [],                                  # 二 太短
 "tri": ["tri"],                            # 三
 "mono": ["mono"],                          # 单一
 "super": ["super"],                        # 上
 "sub": ["sub"],                            # 下
 "inter": ["inter"],                        # 间
 "trans": ["trans","tran"],                 # 横
 "com/con": ["com","con","col","cor","co"], # 共同 (con/co短)
 "contra": ["contra","counter"],            # 反
 "anti": ["anti"],                          # 反
 "pre": [], "post": ["post"], "pro": [],    # 前缀单独列
 "circum": ["circum","circu"],              # 环
 "equi/equ": ["equ","equal","equi"],        # 等
 "frag/fract": ["fract","frag"],            # 破折
 "migr": ["migr"],                          # 迁移
 "mort": ["mort"],                          # 死
 "flu": ["flu","flux"],                     # 流
 "viv/vit": ["viv","vit","vivi"],           # 活
 "san": [], "sen": [], "secur": ["secur"],  #
 "liber": ["liber"],                        # 自由
 "liber/li": [],
 "nomin/nym": ["nomin","onym","nom"],       # 名
 "vers": [],
 "liter": ["liter"],                        # 字
 "langu": ["langu","lingu","ling"],         # 舌语言
 "loc": [], "locus": [], "locat": ["loc","local","loc"],
 "luc/lumin": [],
 "log": ["log","logy","logi"],              # 言学
 "spec": [],
 "synchron": ["synchron"],
 "techn": ["techn"],                        # 技艺
 "turbo": ["turb"],                         # 扰
 "alter/ali": ["alter","altern","ali"],     # 他变
 "ambul": ["ambul"],                        # 走
 "ann/enn": ["ann","enn"],                  # 年
 "anthrop": ["anthrop"],                    # 人
 "apt/ept": ["apt","ept"],                  # 适合
 "arm": ["arm","armo"],                     # 武装 (arm误伤)
 "art": ["art","arti"],                     # 技艺艺 (art)
 "ast": [], "aud": [],
 "bat": [], "bell": ["bell"],               # 战
 "bene": ["bene"],                          # 好
 "botan": ["botan"],                        # 植物
 "brev": ["brev"],                          # 短
 "cand": ["cand"],                          # 白热
 "capit": ["capit"],                        # 头
 "card/cord/cour": ["cour","cord","card"],  # 心
 "carn": ["carn"],                          # 肉
 "caut": ["caut"],                          # 慎
 "cav": ["cav"],                            # 空
 "celer": ["celer"],                        # 快
 "center/centr": ["centr","center"],        # 中心
 "cern/cern": [],
 "cert": ["cert"],                          # 确定
 "cid/cis": ["cis","cid"],                  # 切 (cis短)
 "circ": ["circ","circul"],                 # 环
 "civil": ["civ","civil","civ"],            # 民
 "clar": ["clar","clari"],                  # 清楚
 "clin": ["clin"],                          # 斜
 "clud/clus": ["clud","clus","clos"],       # 关
 "cogn": ["cogn","gnos"],                   # 知
 "cresc/cresc": ["creas","cresc","cret","crit"],# 增长create
 "creat": ["creat","crat"],
 "cruc": ["cruc","cruci"],                  # 十字
 "cult": ["cult"],                          # 耕种文化
 "cur/curs": ["curs","curr","cur"],         # 跑
 "cus/custom": ["custom","cus"],            # 习惯
 "cyc": ["cyc","cycl"],                     # 圆轮
 "dam": ["damn","dem"],                     # 伤
 "dei/div": ["divin","dei","divin"],        # 神
 "dent": ["dent"],                          # 牙
 "derm": ["derm"],                          # 皮
 "don/dot": ["don","dot","donat"],          # 给
 "dur": ["dur"],                            # 持久
 "dyn/dynam": ["dynam","dyn"],              # 力
 "ego": ["ego"],                            # 我
 "empt/am": ["empt","ampl"],                # 取示例
 "equ": [], "err": ["err"],                 # 错游
 "facil": [], "fall/fals": ["fall","fals","fail"],# 错
 "ferv": ["ferv"],                          # 热涌
 "fess": ["fess"],                          # 说承认
 "fin": ["fin","finis"],                    # 界限
 "firm": ["firm"],                          # 牢固
 "fiss": [], "fix": ["fix"],                # 固定
 "flat": ["flat","flate"],                  # 吹平
 "flict": ["flict"],                        # 打击
 "flor": ["flor","flour"],                  # 花
 "foli": [], "fore": [], "fort": ["fort","forc","forc"],# 强
 "fug": ["fug"],                            # 逃
 "fund/found": ["fund","found","fus","foun"],# 底倒
 "fusion": [],
 "gen": ["gen","geni","gener","gend"],      # 生种类
 "glomer": [], "grad": ["grad","gress"],    # 步
 "grat": ["grat","grace","graci"],          # 感激悦
 "grav": ["grav","griev","grie"],           # 重
 "greg": ["greg"],                          # 群
 "habit": ["habit","hibit"],                # 持有hab
 "hap": ["hap","hap"],                      # 机会遇
 "haut": [], "helic": ["helic","helico"],   # 螺旋
 "here": ["her","hes","here","hesit"],      # 粘
 "heter": ["heter","hetero"],               # 异
 "hom": ["homo","hom"],                     # 同
 "hosp/host": ["hosp","host","hospit"],     # 客
 "hum": ["hum","humin"],                    # 地人
 "hydr": ["hydr","hydro"],                  # 水
 "ide/ideo": ["ideo","idea"],               # 观念
 "insul": ["insul"],                        # 岛
 "integr": ["integr"],                      # 完整
 "it": ["it","itiner"],                     # 行走 (it短)
 "jac/ject": [], "ju": ["jur","jus","just","judg","judic"],# 法
 "labor": ["labor","labour"],               # 劳动
 "laps": ["laps"],                          # 滑
 "lax/leas": ["lax","leas"],                # 松
 "lev": ["lev","liev","liev"],              # 举轻
 "lig/lia": ["lig","li","lex","leg"],       # 绑(用lig/lex/lect已count?这里lex)
 "lingu": [], "log": [],
 "long": ["long","leng"],                   # 长
 "lud/lus": ["lud","lus"],                  # 玩
 "lumin": [], "macr": ["macro","macr"],     # 大
 "magn": [], "mal": ["mal","male"],         # 坏
 "man": [], "mand": ["mand","mend"],        # 命令
 "mar": ["mar","mari"],                     # 海
 "mater/matr": ["matr","mater"],            # 母
 "matur": [], "med": [], "medi": [],
 "memor": ["memor","memo"],                 # 记忆
 "ment": [], "merc": ["merc","merch"],      # 贸易商
 "merg": ["merg","mers"],                   # 沉浸
 "meter": [], "micr": ["micro","micr"],     # 小
 "milit": ["milit"],                        # 兵
 "min": [], "mir": ["mir"],                 # 惊奇看
 "mis": [], "mob": [], "mod": ["mod","moder","model"],# 式样
 "mon": ["mon","monit"],                    # 提醒
 "monstr": ["monstr"],                      # 示
 "mont": ["mont"],                          # 山
 "morph": ["morph"],                        # 形
 "mov": [], "mort": [],
 "mut": ["mut"],                            # 变
 "myst": ["myst"],                          # 神秘
 "nasc/nat": ["nat","nasc","nais"],         # 生
 "nau/nav": ["nav","navig"],                # 船
 "necr": [], "neg": ["neg","negat"],        # 否
 "nihil": [], "noc/nox": ["noc","nox"],     # 害
 "nomin": [], "norm": ["norm"],             # 规
 "not": ["not","nota"],                     # 知标
 "null": [], "nutri": ["nutri","nurtur","nutrition"],# 养
 "ocul": ["ocul"],                          # 眼
 "od": ["od","ode"],                        # 路歌
 "oper": ["oper"],                          # 工作
 "opt": ["opt","optim"],                    # 选择
 "ora/ora": ["orat","ora"],                 # 说
 "orb": [], "ordin": ["ordin","order"],     # 顺
 "ori": ["ori","orient"],                   # 升起
 "orn": [], "oss": [], "pac": ["pac","paci","peace"],# 和平
 "pan": ["pan","panto"],                    # 全
 "par": ["par","para"],                     # 准备生
 "pater/patr": ["patr","pater"],            # 父
 "pati/pass": ["pass","pati","passi","path"],# 忍受感
 "pecc": [], "petit": ["petit","pet","pea"],# 求
 "petr": ["petr","petro"],                  # 石
 "phil": ["phil","philo"],                  # 爱
 "phob": ["phob"],                          # 怕
 "phot": ["phot","photo"],                  # 光
 "place/plais": ["pleas","plac","plais"],   # 使悦
 "plant": [], "plaud/plaus": ["plaud","plaus","plod","plos"],# 拍
 "plic/plex/ply": ["plic","plex","ply","pli"],# 折叠
 "plor": ["plor"],                          # 哭
 "plu": [], "pod": ["pod"],                 # 脚
 "poli/polis": ["polis","polit","poli"],    # 城市
 "pon": [], "popul": ["popul","pop"],       # 民
 "por": [], "portend": [], "pot": ["pot","poten","poss"],# 能
 "preci": ["preci","prais","pric","preci"], # 价值
 "reg/rect": ["rect","regular","reg"],      # 统治直
 "rid/ris": ["rid","ris"],                  # 笑
 "riv": ["riv"],                            # 岸流
 "rod/ros": ["rod","ros"],                  # 咬
 "rot/roll": ["rot","roll","rotat"],        # 转卷
 "rub/rud": ["rud","rub"],                  # 粗红
 "rur/rustic": [], "sacr/sanct": ["sacr","sanct"],# 神圣
 "sal/salt/sul": ["sal","sault","sult"],    # 跳
 "salv/save": ["salv","secut","sav"],       # 救
 "sci": [], "sec/sect/seg": ["sect","secu","sec"],# 切跟随
 "seme": [], "ser/sert": ["ser","sert","sere"],# 连
 "serv": [], "sign": [],
 "simi/simul": ["simul","simi","simil"],    # 相似
 "sist": ["sist","stit","sist"],            # 站
 "soci": ["soci"],                          # 伴社
 "sol": [], "somn": [], "son": ["son","sonor"],# 声音
 "soph": ["soph"],                          # 智慧
 "sorb": [], "sort": ["sort"],              # 种类
 "spond/spons": ["spond","spons","sponsor"],# 承诺
 "st/statu": ["statu","stat","stit","stand","stanc","stin"],# 站(st太短)
 "stell": ["stell"],                        # 星
 "stin": [], "stip": [], "strain/strict": ["strict","strain","stren"],# 拉紧
 "stru": [], "sum/summ": ["summ","sum"],    # 总顶
 "suade": ["suade","suas"],                 # 劝
 "sui": [], "sum": [], "syn": ["syn","syl","sym","sys"],# 共
 "tac/tacit": ["tac","tacit"],              # 静
 "tact/tag/tang": ["tact","tag","tang","tig"],# 触(有歧义)
 "tail": ["tail"],                          # 切
 "teg": [], "tempor": ["tempor"],           # 时
 "tend/tens/tent": ["tend","tens"],         # 伸紧(tent已在)
 "term": ["termin","term"],                # 界
 "terr": ["terr","terro","terra"],         # 地恐
 "test": ["test"],                          # 证
 "text": ["text","textil"],                 # 织
 "theo/the": ["theo","the"],                # 神(the短)
 "therap": ["therap"],                      # 治疗
 "thes/thet": ["thes","thet"],              # 放置
 "toler": ["toler"],                        # 忍受
 "tom": [], "ton": ["ton"],                 # 音
 "tort": ["tort","tors"],                   # 扭
 "tour": ["tour","torn"],                   # 转旅
 "tox": [], "trem": ["trem"],               # 颤抖
 "trib": ["trib","tribut"],                 # 给缴纳
 "troph": [], "trud/trus": ["trud","trus"], # 推
 "umb": [], "umbr": ["umbr"],               # 阴
 "und/ound": ["und","ound"],                # 波浪
 "urb": ["urb"],                            # 城市
 "us/util": ["util","us"],                  # 用
 "vac": ["vac","vacu"],                     # 空
 "vad/vas": ["vad","vas"],                  # 走
 "vapor": ["vapor"],                        # 汽
 "veget": [], "vell": [], "ven": [], "ver": ["ver","veri"],# 真(veri与var冲突)
 "verb": ["verb"],                          # 词
 "verm": [], "vest": ["vest"],              # 衣
 "vi/via": ["via","viad"],                  # 路
 "vibr": ["vibr"],                          # 摆动
 "vict/vinc": ["vict","vinc","vinc"],       # 胜
 "vig": ["vig"],                            # 活强力
 "viol": ["viol"],                          # 力
 "vir": ["vir"],                            # 男
 "vis": [], "voc/vok": ["voc","vok"],       # 声喊
 "vol/volunt": ["volunt","vol"],            # 意愿
 "volc": [], "vor": [], "voy": [], "zo": ["zo"],# 动(voc/vok/vol重)
}
