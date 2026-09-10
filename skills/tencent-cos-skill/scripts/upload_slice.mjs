#!/usr/bin/env node
// Robust upload with sliceUploadFile + small slices, logging progress.
// Usage: node upload_slice.mjs <localPath> <cosKey>
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const fs = require('fs');
const env = fs.readFileSync('/root/.openclaw/workspace/skills/tencent-cos-skill/.env', 'utf8');
env.split('\n').forEach((l) => {
  const m = l.match(/^([A-Z0-9_]+)=(.*)$/);
  if (m) process.env[m[1]] = m[2].replace(/^['"]|['"]$/g, '');
});
const COS = require('/root/.openclaw/workspace/skills/tencent-cos-skill/node_modules/cos-nodejs-sdk-v5');
const cos = new COS({
  SecretId: process.env.TENCENT_COS_SECRET_ID,
  SecretKey: process.env.TENCENT_COS_SECRET_KEY,
  Timeout: 180000,
  RetryTimes: 5,
});

const local = process.argv[2];
const key = process.argv[3];
const size = fs.statSync(local).size;
console.log(`upload slice ${local} (${size} B) -> ${key}`);
let last = 0;
cos.sliceUploadFile({
  Bucket: 'korean-video-1433876150',
  Region: 'ap-guangzhou',
  Key: key,
  FilePath: local,
  SliceSize: 1024 * 1024 * 2,
  onProgress: (p) => {
    const pct = Math.round((p.loaded / p.total) * 100);
    if (pct >= last + 10) { last = pct; console.log(`progress ${pct}% (${p.loaded}/${p.total})`); }
  },
}, (err, data) => {
  if (err) { console.error('UPLOAD ERROR:', err.statusCode || err.message || JSON.stringify(err)); process.exit(1); }
  console.log('UPLOAD OK:', JSON.stringify(data.Location || data));
  process.exit(0);
});
