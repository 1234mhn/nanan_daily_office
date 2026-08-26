#!/usr/bin/env node
const fs = require('fs');
const env = fs.readFileSync('/root/.openclaw/workspace/skills/tencent-cos-skill/.env','utf8');
env.split('\n').forEach(l=>{const m=l.match(/^([A-Z0-9_]+)=(.*)$/);if(m){process.env[m[1]]=m[2].replace(/^['\"]|['\"]$/g,'')}});
const COS = require('/root/.openclaw/workspace/skills/tencent-cos-skill/node_modules/cos-nodejs-sdk-v5');
const cos = new COS({ SecretId: process.env.TENCENT_COS_SECRET_ID, SecretKey: process.env.TENCENT_COS_SECRET_KEY });
const Bucket = 'korean-video-1433876150';
const Region = 'ap-guangzhou';
const Key = "爱情怎么翻译全集/Can This Love Be Translated？ S01E05 - 第 5 集 - 2160p WEB-DL HDR10 H265 DDP 5.1 Atmos.mkv";
console.log('Testing getObjectUrl...');
cos.getObjectUrl({ Bucket, Region, Key, Expires: 7200, Sign: true }, (err, data) => {
  if (err) { console.error('ERR:', err.message || err); process.exit(1); }
  const url = data.Url;
  console.log('URL:', url);
  // immediately test head via http
  const { execSync } = require('child_process');
  try {
    const out = execSync(`curl -s -o /dev/null -w "%{http_code}" -r 0-1023 "${url}"`, { timeout: 30000 }).toString();
    console.log('CURL HTTP:', out);
  } catch (e) { console.error('curl fail:', e.message); }
});
