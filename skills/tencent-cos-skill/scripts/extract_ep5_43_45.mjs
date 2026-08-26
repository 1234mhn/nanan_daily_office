#!/usr/bin/env node
// Extract EP5 subtitles for lessons 43, 44, 45 via COS stream (no full download)
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

// segments: lesson -> [start, end] in full-episode seconds
const segs = { 43: [549,576], 44: [691,732], 45: [743,821] };

async function extractSub(startSec, endSec, mapIdx, outputFile, label) {
  console.log(`Extracting ${label} t${mapIdx} (${startSec}-${endSec})...`);
  const stream = cos.getObjectStream({ Bucket: bucket, Region: region, Key: key });
  return new Promise((resolve) => {
    const ff = spawn('ffmpeg', [
      '-i', 'pipe:0',
      '-ss', String(startSec),
      '-to', String(endSec),
      '-map', `0:s:${mapIdx}`,
      '-c:s', 'srt',
      '-f', 'srt',
      'pipe:1',
      '-y'
    ], { stdio: ['pipe', 'pipe', 'inherit'] });
    stream.pipe(ff.stdin);
    const chunks = [];
    ff.stdout.on('data', c => chunks.push(c));
    ff.stdout.on('end', () => {
      fs.writeFileSync(outputFile, Buffer.concat(chunks));
      console.log(`  Done: ${outputFile}`);
      resolve();
    });
    ff.on('exit', (code) => {
      if (!ff.stdout.readableEnded) {
        fs.writeFileSync(outputFile, Buffer.concat(chunks));
        console.log(`  Exit(${code}): ${outputFile}`);
        resolve();
      }
    });
  });
}

async function main() {
  for (const [lesson, [s, e]] of Object.entries(segs)) {
    await extractSub(s, e, 1, `/tmp/ep5_lesson${lesson}_kr.srt`, 'lesson'+lesson+' KR(orig t4)');
    await extractSub(s, e, 3, `/tmp/ep5_lesson${lesson}_cn.srt`, 'lesson'+lesson+' CN(orig t6)');
  }
  console.log('\n=== RESULT FILES ===');
  for (const f of ['ep5_lesson43_kr','ep5_lesson43_cn','ep5_lesson44_kr','ep5_lesson44_cn','ep5_lesson45_kr','ep5_lesson45_cn']) {
    const p = `/tmp/${f}.srt`;
    const sz = fs.existsSync(p) ? fs.statSync(p).size : 0;
    console.log(`${p} (${sz} bytes)`);
  }
}
main().catch(err => { console.error('Fatal:', err.message); process.exit(1); });
