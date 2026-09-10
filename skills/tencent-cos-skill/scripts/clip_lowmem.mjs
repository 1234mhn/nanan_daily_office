#!/usr/bin/env node
// Re-clip a lesson from COS S01E05 starting at first dialogue line (low-memory variant).
// Usage: node clip_lowmem.mjs <outLabel> <startHH:MM:SS> <durSeconds>
import { spawn } from 'child_process';
import { createRequire } from 'module';
import { readFileSync } from 'fs';

const require = createRequire(import.meta.url);
const COS = require('/root/.openclaw/workspace/skills/tencent-cos-skill/node_modules/cos-nodejs-sdk-v5');

const env = readFileSync('/root/.openclaw/workspace/skills/tencent-cos-skill/.env', 'utf8');
env.split('\n').forEach((l) => {
  const m = l.match(/^([A-Z0-9_]+)=(.*)$/);
  if (m) process.env[m[1]] = m[2].replace(/^['"]|['"]$/g, '');
});

const cos = new COS({
  SecretId: process.env.TENCENT_COS_SECRET_ID,
  SecretKey: process.env.TENCENT_COS_SECRET_KEY,
});

const key = '爱情怎么翻译全集/Can This Love Be Translated？ S01E05 - 第 5 集 - 2160p WEB-DL HDR10 H265 DDP 5.1 Atmos.mkv';
const label = process.argv[2];
const start = process.argv[3];
const dur = process.argv[4];
const out = `/tmp/${label}.mp4`;

console.log(`[${label}] streaming, start=${start} dur=${dur}s -> ${out}`);
const stream = cos.getObjectStream({ Bucket: 'korean-video-1433876150', Region: 'ap-guangzhou', Key: key });

const ff = spawn('ffmpeg', [
  '-threads', '2',
  '-i', 'pipe:0',
  '-ss', start,
  '-t', dur,
  '-map', '0:v:0',
  '-map', '0:a:0',
  '-vf', 'zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,scale=1920:1080',
  '-c:v', 'libx264', '-crf', '22', '-preset', 'ultrafast', '-threads', '3',
  '-c:a', 'aac', '-b:a', '192k',
  out,
  '-y',
], { stdio: ['pipe', 'inherit', 'inherit'] });

stream.pipe(ff.stdin);
ff.on('exit', (code) => { console.log(`[${label}] ffmpeg exited ${code}`); process.exit(code || 0); });
stream.on('error', (err) => { console.error(`[${label}] stream error:`, err && err.message); ff.kill(); process.exit(1); });
