#!/usr/bin/env node
/**
 * CI 视频截取 + HDR→SDR 转码 (服务端，省本地CPU)
 */
import { createRequire } from "module";
import { readFileSync, existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const require = createRequire(import.meta.url);
const COS = require("cos-nodejs-sdk-v5");
const __dirname = dirname(fileURLToPath(import.meta.url));

function loadEnv() {
  const envPath = resolve(__dirname, "..", ".env");
  if (existsSync(envPath)) {
    for (const line of readFileSync(envPath, "utf-8").split("\n")) {
      const t = line.trim();
      if (!t || t.startsWith("#")) continue;
      const i = t.indexOf("="); if (i === -1) continue;
      let v = t.slice(i + 1).trim();
      if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) v = v.slice(1, -1);
      process.env[t.slice(0, i).trim()] = process.env[t.slice(0, i).trim()] || v;
    }
  }
}
loadEnv();

const SECRET_ID = process.env.TENCENT_COS_SECRET_ID;
const SECRET_KEY = process.env.TENCENT_COS_SECRET_KEY;
const TOKEN = process.env.TENCENT_COS_TOKEN;
const REGION = process.env.TENCENT_COS_REGION || "ap-guangzhou";
const BUCKET = process.env.TENCENT_COS_BUCKET;

const cos = new COS({ SecretId: SECRET_ID, SecretKey: SECRET_KEY, Token: TOKEN });

const SRC_KEY = "爱情怎么翻译全集/Can This Love Be Translated？ S01E07 - 第 7 集 - 2160p WEB-DL HDR10 H265 DDP 5.1 Atmos.mkv";
// 输出到 _clip/ 前缀，最后阶段2再决定上传/改名
const OUT_KEY = "爱情怎么翻译全集/_tmp_clip/ep07_l61_ci_test.mp4";
const START = "10";
const DURATION = "73";

const ciHost = `${BUCKET}.ci.${REGION}.myqcloud.com`;

const bodyXml = `<?xml version="1.0" encoding="UTF-8"?>
<Request>
  <Tag>Transcode</Tag>
  <Input>
    <Object>${SRC_KEY}</Object>
  </Input>
  <Operation>
    <Transcode>
      <Container><Format>mp4</Format></Container>
      <Video>
        <Codec>H.264</Codec>
        <Width>1920</Width>
        <Height>1080</Height>
        <Fps>24</Fps>
        <Bitrate>3000</Bitrate>
        <Crf>22</Crf>
        <Preset>medium</Preset>
      </Video>
      <Audio>
        <Codec>AAC</Codec>
        <Samplerate>44100</Samplerate>
        <Bitrate>192</Bitrate>
        <Channels>2</Channels>
      </Audio>
      <TimeInterval>
        <Start>${START}</Start>
        <Duration>${DURATION}</Duration>
      </TimeInterval>
      <TransConfig>
        <TransMode>OnEvent</TransMode>
        <IsHdr2Sdr>true</IsHdr2Sdr>
      </TransConfig>
    </Transcode>
    <Output>
      <Bucket>${BUCKET}</Bucket>
      <Region>${REGION}</Region>
      <Object>${OUT_KEY}</Object>
    </Output>
  </Operation>
</Request>`;

console.log("提交 CI 转码任务...");
console.log("源:", SRC_KEY);
console.log("区间:", START, "+", DURATION);
console.log("输出:", OUT_KEY);

cos.request({
  Method: "POST",
  Url: `https://${ciHost}/jobs`,
  Key: "jobs",
  Body: bodyXml,
  ContentType: "application/xml",
  headers: { "Content-Type": "application/xml" },
}, (err, data) => {
  if (err) { console.error("ERR:", err.message || JSON.stringify(err)); process.exit(1); }
  console.log("statusCode:", data.statusCode);
  console.log("body:", typeof data.body === "string" ? data.body : JSON.stringify(data.body));
  const m = (typeof data.body === "string" ? data.body : "").match(/<JobId>([^<]+)<\/JobId>/);
  if (m) {
    console.log("JOBID=" + m[1]);
  }
});
