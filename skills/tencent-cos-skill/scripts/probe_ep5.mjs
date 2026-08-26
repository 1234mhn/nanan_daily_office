#!/usr/bin/env node
// Probe EP5 subtitle tracks via COS stream (no full download)
import { spawn } from 'child_process';
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const fs = require('fs');
const env = fs.readFileSync('/root/.openclaw/workspace/skills/tencent-cos-skill/.env','utf8');
env.split('\n').forEach(l=>{const m=l.match(/^([A-Z0-9_]+)=(.*)$/);if(m){process.env[m[1]]=m[2].replace(/^['\"]|['\"]$/g,'')}});
const COS = require('/root/.openclaw/workspace/skills/tencent-cos-skill/node_modules/cos-nodejs-sdk-v5');
const cos = new COS({
  SecretId: process.env.TENCENT_COS_SECRET_ID,
  SecretKey: process.env.TENCENT_COS_SECRET_KEY
});
const key = "爱情怎么翻译全集/Can This Love Be Translated？ S01E05 - 第 5 集 - 2160p WEB-DL HDR10 H265 DDP 5.1 Atmos.mkv";
const bucket = 'korean-video-1433876150';
const region = 'ap-guangzhou';

const stream = cos.getObjectStream({ Bucket: bucket, Region: region, Key: key, Range: 'bytes=0-8000000' });
const ff = spawn('ffmpeg', ['-i', 'pipe:0', '-f', 'null', '-'], { stdio: ['pipe', 'pipe', 'pipe'] });
stream.pipe(ff.stdin);
let err = '';
ff.stderr.on('data', c => { err += c; });
ff.on('exit', () => {
  const lines = err.split('\n').filter(l => /Subtitle/i.test(l));
  console.log(lines.join('\n'));
});
setTimeout(() => { ff.kill(); }, 45000);
