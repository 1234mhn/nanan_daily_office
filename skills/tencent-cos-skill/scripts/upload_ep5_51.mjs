#!/usr/bin/env node
// Upload EP5 lesson51 clip via COS sliceUploadFile (stable for large files)
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const fs = require('fs');
const env = fs.readFileSync('/root/.openclaw/workspace/skills/tencent-cos-skill/.env','utf8');
env.split('\n').forEach(l=>{const m=l.match(/^([A-Z0-9_]+)=(.*)$/);if(m){process.env[m[1]]=m[2].replace(/^['\"]|['\"]$/g,'')}});
const COS = require('/root/.openclaw/workspace/skills/tencent-cos-skill/node_modules/cos-nodejs-sdk-v5');
const cos = new COS({ SecretId: process.env.TENCENT_COS_SECRET_ID, SecretKey: process.env.TENCENT_COS_SECRET_KEY });
const local = '/tmp/ep5_lesson51_2339-2521_clean.mp4';
const key = 'media/korean_course/videos/ep5_lesson51_2339-2521.mp4';
console.log('Starting slice upload...', key, fs.statSync(local).size, 'bytes');
cos.sliceUploadFile({
  Bucket: 'korean-video-1433876150',
  Region: 'ap-guangzhou',
  Key: key,
  FilePath: local,
  SliceSize: 1024*1024*4, // 4MB slices
}, (err) => {
  if (err) { console.error('UPLOAD ERROR:', JSON.stringify(err&&err.message?err.message:err)); process.exit(1); }
  const url = 'https://korean-video-1433876150.cos.ap-guangzhou.myqcloud.com/' + encodeURI(key.replace(/\s/g,'~')).replace(/%2F/g,'/');
  // simpler canonical
  console.log('PUBLIC URL: https://korean-video-1433876150.cos.ap-guangzhou.myqcloud.com/media/korean_course/videos/ep5_lesson51_2339-2521.mp4');
  process.exit(0);
});
