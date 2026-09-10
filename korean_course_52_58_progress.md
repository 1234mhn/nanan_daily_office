# 韩语课程 第52~58课 加课进度（2026-09-10 重启）

> 任务定义（来自 2026-09-09 用户布置，用户 09-10 已确认余额到位，重启开工）
> 片源更正：第52/53/54课 = COS **第5集 S01E05**；第55~58课 = COS **第6集 S01E06**

| 课 | 片源 | 起止(整集时间) | 阶段1内容 | 用户核对 | 阶段2注入 | 已上线 |
|:--|:--|:--|:--|:--|:--|:--|
| 52 | ep05 | 25:55–27:03 | ✅ 见 korean_course_52_58_progress_52.md | ⬜ | ⬜ | ⬜ |
| 53 | ep05 | 28:14–29:24 | ✅ 见 korean_course_52_58_progress_53.md | ⬜ | ⬜ | ⬜ |
| 54 | ep05 | 36:24–38:21 | ✅ 见 korean_course_52_58_progress_54.md | ⬜ | ⬜ | ⬜ |
| 55 | ep06 | 09:47–12:06 | ⬜ | ⬜ | ⬜ | ⬜ |
| 56 | ep06 | 15:00–15:46 | ⬜ | ⬜ | ⬜ | ⬜ |
| 57 | ep06 | 16:46–17:15 | ⬜ | ⬜ | ⬜ | ⬜ |
| 58 | ep06 | 17:18–18:53 | ⬜ | ⬜ | ⬜ | ⬜ |

## 关键环境
- COS bucket: `korean-video-1433876150` / region `ap-guangzhou` / 密钥已持久化在 skill .env
- 源片：`爱情怎么翻译全集/Can This Love Be Translated？ S01E05 - 第 5 集 - 2160p WEB-DL HDR10 H265 DDP 5.1 Atmos.mkv`（ep05）、`...S01E06 - 第 6 集...mkv`（ep06）
- 成片存 `media/korean_course/videos/epX_lessonNN_起-止.mp4`，bt709
- 页面模板/流程见 `SOP集合/SOP-韩语课程更新流程.md` + `skills/课程产品师/SKILL.md`

## 52~54 阶段1 产出（2026-09-10 完成）

| 课 | 视频 COS Key | 台词数 | 课标题(候选) | 产出文件 |
|:--|:--|:--:|:--|:--|
| 52 | `media/korean_course/videos/ep5_lesson52_2555-2703.mp4` | 20 | 重逢在片场 | `korean_course_52_58_progress_52.md` |
| 53 | `media/korean_course/videos/ep5_lesson53_2814-2924.mp4` | 26 | 买菜与做饭 | `korean_course_52_58_progress_53.md` |
| 54 | `media/korean_course/videos/ep5_lesson54_3624-3821.mp4` | 21 | 不想看见极光 | `korean_course_52_58_progress_54.md` |

- 🔄 **2026-09-10 视频已按台词起点重截（crf22）**：52/53/54 均改为「从第一句台词开始截」，跳过前面无台词过场，视频与台词天然对齐（第一句归零后≈0s）。
  - 52：新 key `ep5_lesson52_2555-2703.mp4`（69.03s，bt709）
  - 53：新 key `ep5_lesson53_2814-2924.mp4`（70.03s，bt709）
  - 54：新 key `ep5_lesson54_3624-3821.mp4`（117.03s，bt709）
  - 旧 key（2530/2813/3621）均保留未删。
- 三课视频均 1920×1080 / H.264 crf22 / 色彩 **bt709·bt709·bt709**，已上传 COS。
- 字幕来源：从源 MKV 远程提取韩语字幕轨（stream #0:4，全片 979 条）+ 中文轨参考（/tmp/ep5_comb_cn.srt）。
- 🔴 注意：52 课视频 0–25.5s 是 OST 过场（♪밤새 꿈속에…），已剔除，不计入台词；对白自 25.5s（주호진!）起。
- 🔴 体积偏大（52=116MB / 53=79MB / 54=126MB），因 crf18；如需减小可改 crf22 重编。
- ⏳ 待办：用户核对台词+时间戳 → 阶段2 注入（Claude Code）。
