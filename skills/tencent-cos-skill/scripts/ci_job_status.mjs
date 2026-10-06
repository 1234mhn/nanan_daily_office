import { createRequire } from "module";
import { readFileSync, existsSync, writeFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
const require = createRequire(import.meta.url);
const COS = require("cos-nodejs-sdk-v5");
const __dirname = dirname(fileURLToPath(import.meta.url));
const envPath = resolve(__dirname, "..", ".env");
if (existsSync(envPath)) for (const line of readFileSync(envPath, "utf-8").split("\n")) {
  const t = line.trim(); if (!t || t.startsWith("#")) continue;
  const i = t.indexOf("="); if (i === -1) continue;
  let v = t.slice(i + 1).trim();
  if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) v = v.slice(1, -1);
  process.env[t.slice(0, i).trim()] = process.env[t.slice(0, i).trim()] || v;
}
const cos = new COS({ SecretId: process.env.TENCENT_COS_SECRET_ID, SecretKey: process.env.TENCENT_COS_SECRET_KEY, Token: process.env.TENCENT_COS_TOKEN });
const BUCKET = process.env.TENCENT_COS_BUCKET, REGION = process.env.TENCENT_COS_REGION || "ap-guangzhou";
const ciHost = `${BUCKET}.ci.${REGION}.myqcloud.com`;
const jobId = process.argv[2];
if (jobId) {
  cos.request({ Method: "GET", Url: `https://${ciHost}/jobs/${jobId}`, Key: `jobs/${jobId}` }, (err, data) => {
    if (err) { console.error("ERR", err.message); process.exit(1); }
    const d = data?.Response?.JobsDetail || {};
    console.log("JobId:", d.JobId, "State:", d.State, "Message:", d.Message);
    console.log("Output:", JSON.stringify(d.Operation?.Output));
    console.log("IsHdr2Sdr:", d.Operation?.Transcode?.TransConfig?.IsHdr2Sdr);
    console.log("Video:", JSON.stringify(d.Operation?.Transcode?.Video));
    writeFileSync("/tmp/ci_job_last.json", JSON.stringify(data.Response, null, 1));
  });
} else {
  cos.request({ Method: "GET", Url: `https://${ciHost}/jobs?tag=Transcode&size=10`, Key: "jobs" }, (err, data) => {
    if (err) { console.error("ERR", err.message); process.exit(1); }
    const jd = data?.Response?.JobsDetail;
    const arr = Array.isArray(jd) ? jd : (jd ? [jd] : []);
    for (const j of arr) console.log(j.JobId, j.State, j.Operation?.Output?.Object);
  });
}
