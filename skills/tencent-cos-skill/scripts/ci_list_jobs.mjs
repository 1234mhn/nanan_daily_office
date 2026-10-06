import { createRequire } from "module";
import { readFileSync, existsSync } from "fs";
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
// list jobs
cos.request({ Method: "GET", Url: `https://${ciHost}/jobs?tag=Transcode&size=10`, Key: "jobs" }, (err, data) => {
  if (err) { console.error("ERR", err.message); process.exit(1); }
  const body = typeof data.body === "string" ? data.body : JSON.stringify(data.body?.Response || data.body || data);
  console.log("statusCode", data.statusCode);
  console.log("KEYS", Object.keys(data));
  console.log("TYPEOF body", typeof data.body);
  // print job ids + states
  const ids = [];
  const states = [];
  const objs = [];
  console.log(JSON.stringify({ ids, states, objs }, null, 1));
  console.log("RAW:", body.slice(0, 1500));
});
