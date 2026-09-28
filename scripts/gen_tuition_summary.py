from PIL import Image, ImageDraw, ImageFont

W = 760
bold = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
reg = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
def F(s, b=False): return ImageFont.truetype(bold if b else reg, s)

rows = [
    ("第17节", "9月6日", "1.5小时", "90元"),
    ("第18节", "9月20日", "1.5小时", "90元"),
]
head_h, row_h = 62, 66
H = 150 + head_h + row_h*len(rows) + 130 + 60

img = Image.new("RGB", (W, H), "#FFFFFF")
d = ImageDraw.Draw(img)

# 标题
d.text((44, 52), "刘栖伶 · 9月份课时汇总", font=F(38, True), fill="#3B7BE8")
d.text((44, 106), "累计 2 节课 · 3 小时 · 课时费 180 元", font=F(22), fill="#9AA3AF")

# 表格
x0, y0 = 30, 165
colw = [150, 200, 180, 140]
tw = sum(colw)

# 表头（蓝色）
d.rounded_rectangle((x0, y0, x0+tw, y0+head_h), radius=10, fill="#4A8FF7")
x = x0
for h, w in zip(["节次", "上课日期", "时长", "实缴金"], colw):
    d.text((x+w/2, y0+head_h/2), h, font=F(26, True), fill="white", anchor="mm")
    x += w

# 数据行（斑马纹）
y = y0 + head_h
for i, r in enumerate(rows):
    if i % 2 == 1:
        d.rectangle((x0, y, x0+tw, y+row_h), fill="#F5F8FB")
    x = x0
    for c, w in zip(r, colw):
        fnt = F(24, True) if w == 140 else F(24)
        col = "#1F2329" if w == 140 else "#5A6472"
        d.text((x+w/2, y+row_h/2), c, font=fnt, fill=col, anchor="mm")
        x += w
    y += row_h

# 合计行（橙黄圆角）
d.rounded_rectangle((x0, y+16, x0+tw, y+16+86), radius=14, fill="#F5A623")
d.text((x0+tw/2, y+16+43), "累计 2 节 · 3 小时 · 课时费 180 元",
       font=F(28, True), fill="white", anchor="mm")

# 底部小字
d.text((W/2, H-34), "统计截至 2026-09-28", font=F(19), fill="#B0B7C0", anchor="mm")

img.save("/tmp/lql_final.png")
print("ok", img.size)
