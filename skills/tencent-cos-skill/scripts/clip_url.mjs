#!/usr/bin/env node
// Clip a lesson from COS via signed URL (HTTP Range seek) - robust vs pipe truncation.
// Usage: node clip_url.mjs <urlFile> <outLabel> <startHH:MM:SS> <durSeconds>
import { spawn } from 'child_process';
import { readFileSync } from 'fs';

const urlFile = process.argv[2];
const label = process.argv[3];
const start = process.argv[4];
const dur = process.argv[5];
const url = readFileSync(urlFile, 'utf8').trim();
const out = `/tmp/${label}.mp4`;

console.log(`[${label}] url-seek start=${start} dur=${dur}s -> ${out}`);

const ff = spawn('ffmpeg', [
  '-threads', '2',
  '-ss', start,
  '-i', url,
  '-t', dur,
  '-map', '0:v:0',
  '-map', '0:a:0',
  '-vf', 'zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,scale=1920:1080',
  '-c:v', 'libx264', '-crf', '22', '-preset', 'ultrafast', '-threads', '3',
  '-c:a', 'aac', '-b:a', '192k',
  out,
  '-y',
], { stdio: ['ignore', 'inherit', 'inherit'] });

ff.on('exit', (code) => { console.log(`[${label}] ffmpeg exited ${code}`); process.exit(code || 0); });
