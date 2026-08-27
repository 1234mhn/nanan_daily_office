#!/usr/bin/env node
// Upload EP5 lesson45 video via COS sliceUploadFile (stable for large files)
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const fs = require('fs');
const env = fs.readFileSync('/root/.openclaw/workspace/skills/tencent-cos-skill/.env','utf8');
env.split('\n').forEach(l=>{const m=l.match(/^([A-Z0-9_]+)=(.*)$/);if(m){process.env[m[1]]=m[2].replace(/^['\"]|['\"]$/g,'')}});
const COS = require('/root/.openclaw/workspace/skills/tencent-cos-skill/node_modules/cos-nodejs-sdk-v5');
const cos = new COS({ SecretId: process.env.TENCENT_COS_SECRET_ID, SecretKey: process.env.TENCENT_COS_SECRET_KEY });
const local = '/tmp/ep5_lesson45_1223-1341.mp4';
const key = 'media/korean_course/videos/ep5_lesson45_1223-1341.mp4';
console.log('Starting slice upload...', local, fs.statSync(local).size, 'bytes');
cos.sliceUploadFile({
  Bucket: 'korean-video-1433876150',
  Region: 'ap-guangzhou',
  Key: key,
  FilePath: local,
  SliceSize: 1024*1024*2, // 2MB slices
}, (err, data) => {
  if (err) { console.error('UPLOAD ERROR:', JSON.stringify(err)); process.exit(1); }
  console.log('UPLOAD OK:', data.Location, data.ETag || '');
  // print permanent URL
  console.log('PUBLIC URL: https://' + data.Location);
  process.exit(0);
});
