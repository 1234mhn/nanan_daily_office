#!/usr/bin/env node
// Combined-pass: stream EP5 once (549-821s), extract KR orig(t4=global 0:4) + CN orig(t6=global 0:6)
import { spawn } from 'child_process';
import { createRequire } from 'module';
import { writeFileSync } from 'fs';
const require = createRequire(import.meta.url);
const fs = require('fs');
const env = fs.readFileSync('/root/.openclaw/workspace/skills/tencent-cos-skill/.env','utf8');
env.split('\n').forEach(l=>{const m=l.match(/^([A-Z0-9_]+)=(.*)$/);if(m){process.env[m[1]]=m[2].replace(/^['\"]|['\"]$/g,'')}});
const COS = require('/root/.openclaw/workspace/skills/tencent-cos-skill/node_modules/cos-nodejs-sdk-v5');
const cos = new COS({ SecretId: process.env.TENCENT_COS_SECRET_ID, SecretKey: process.env.TENCENT_COS_SECRET_KEY });
const key = "爱情怎么翻译全集/Can This Love Be Translated？ S01E05 - 第 5 集 - 2160p WEB-DL HDR10 H265 DDP 5.1 Atmos.mkv";
const bucket = 'korean-video-1433876150';
const region = 'ap-guangzhou';

const OUT = { kr: '/tmp/ep5_comb_kr.srt', cn: '/tmp/ep5_comb_cn.srt' };
console.log(`One-pass extract KR(t4)/CN(t6) 549-821 -> ${JSON.stringify(OUT)}`);
const stream = cos.getObjectStream({ Bucket: bucket, Region: region, Key: key });
let nb = 0; const t0 = Date.now();
stream.on('data', c => { nb += c.length; if (nb % (300*1024*1024) < 200000) console.error(`  read ${(nb/1048576).toFixed(0)}MB in ${((Date.now()-t0)/1000).toFixed(0)}s`); });

const ff = spawn('ffmpeg', [
  '-i','pipe:0','-ss','540','-to','825',
  '-map','0:4','-c:s','srt',OUT.kr,
  '-map','0:6','-c:s','srt',OUT.cn,
  '-y'
], { stdio: ['pipe','ignore','inherit'] });
stream.pipe(ff.stdin);
ff.on('close',(code)=>{
  console.log(`CLOSE code=${code} bytesRead=${(nb/1048576).toFixed(0)}MB elapsed=${((Date.now()-t0)/1000).toFixed(0)}s`);
});
