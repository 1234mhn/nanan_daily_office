#!/usr/bin/env node
// Extract EP5 subtitles for lessons 48,49,50 via COS full stream (reliable, no HTTP seek)
import { spawn } from 'child_process';
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const fs = require('fs');
const env = fs.readFileSync('/root/.openclaw/workspace/skills/tencent-cos-skill/.env','utf8');
env.split('\n').forEach(l=>{const m=l.match(/^([A-Z0-9_]+)=(.*)$/);if(m){process.env[m[1]]=m[2].replace(/^['\"]|['\"]$/g,'')}});
const COS = require('/root/.openclaw/workspace/skills/tencent-cos-skill/node_modules/cos-nodejs-sdk-v5');
const cos = new COS({ SecretId: process.env.TENCENT_COS_SECRET_ID, SecretKey: process.env.TENCENT_COS_SECRET_KEY });
const key = "爱情怎么翻译全集/Can This Love Be Translated？ S01E05 - 第 5 集 - 2160p WEB-DL HDR10 H265 DDP 5.1 Atmos.mkv";
const bucket = 'korean-video-1433876150';
const region = 'ap-guangzhou';

// filter range in full-episode seconds (with margin so we can slice later)
const FROM = 930, TO = 1215;

async function extract(trackAbsIndex, outputFile, label) {
  console.log(`Extracting ABS track ${trackAbsIndex} (${label}), range ${FROM}s-${TO}s ...`);
  const stream = cos.getObjectStream({ Bucket: bucket, Region: region, Key: key });
  return new Promise((resolve) => {
    // no -ss on input (unreliable over HTTP); stream whole, filter stime AFTER via ffmpeg copy
    const ff = spawn('ffmpeg', [
      '-i','pipe:0','-vn','-an',
      '-map',`0:${trackAbsIndex}`,
      '-c:s','srt','-f','srt',
      'pipe:1','-y'
    ], { stdio:['pipe','pipe','inherit'] });
    stream.pipe(ff.stdin);
    const chunks=[];
    ff.stdout.on('data',c=>chunks.push(c));
    ff.stdout.on('end',()=>{ fs.writeFileSync(outputFile,Buffer.concat(chunks)); console.log(`  Done: ${outputFile} (${Buffer.concat(chunks).length} bytes)`); resolve(); });
    ff.on('exit',(c)=>{ if(!ff.stdout.readableEnded){ fs.writeFileSync(outputFile,Buffer.concat(chunks)); console.log(`  Exit(${c}): ${outputFile} (${Buffer.concat(chunks).length} bytes)`); resolve(); } });
    ff.stderr.on('data',d=>process.stderr.write(d));
  });
}

async function main(){
  await extract(4, '/tmp/ep5_full4850_KOR_all.srt', 'Korean-t4');   // abs index 4 = pure Korean
  await extract(6, '/tmp/ep5_full4850_CHI_all.srt', 'ChineseSimplified-t6'); // abs index 6 = chi Simplified
  console.log('\\n=== DONE ===');
}
main().catch(e=>{console.error('Fatal:',e.message);process.exit(1);});
