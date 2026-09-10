#!/usr/bin/env node
// Upload a local clip to COS at the given key (slice upload).
// Usage: node upload_v2.mjs <localPath> <cosKey>
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const fs = require('fs');
const env = fs.readFileSync('/root/.openclaw/workspace/skills/tencent-cos-skill/.env', 'utf8');
env.split('\n').forEach((l) => {
  const m = l.match(/^([A-Z0-9_]+)=(.*)$/);
  if (m) process.env[m[1]] = m[2].replace(/^['"]|['"]$/g, '');
});
const COS = require('/root/.openclaw/workspace/skills/tencent-cos-skill/node_modules/cos-nodejs-sdk-v5');
const cos = new COS({ SecretId: process.env.TENCENT_COS_SECRET_ID, SecretKey: process.env.TENCENT_COS_SECRET_KEY });

const local = process.argv[2];
const key = process.argv[3];
console.log('Uploading', local, fs.statSync(local).size, 'bytes ->', key);
cos.sliceUploadFile({
  Bucket: 'korean-video-1433876150',
  Region: 'ap-guangzhou',
  Key: key,
  FilePath: local,
  SliceSize: 1024 * 1024 * 4,
}, (err, data) => {
  if (err) { console.error('UPLOAD ERROR:', err && err.message ? err.message : JSON.stringify(err)); process.exit(1); }
  console.log('UPLOAD OK:', JSON.stringify(data && data.Location ? data.Location : data));
  process.exit(0);
});
