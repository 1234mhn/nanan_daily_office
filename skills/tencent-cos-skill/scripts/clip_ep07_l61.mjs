import { spawn } from 'child_process';
import { createRequire } from 'module';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { readFileSync, unlinkSync } from 'fs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const COS = require('cos-nodejs-sdk-v5');

const creds = JSON.parse(readFileSync('/root/.tccli/default.credential', 'utf8'));
const cos = new COS({ SecretId: creds.secretId, SecretKey: creds.secretKey });

const key = "爱情怎么翻译全集/Can This Love Be Translated？ S01E07 - 第 7 集 - 2160p WEB-DL HDR10 H265 DDP 5.1 Atmos.mkv";
const bucket = 'korean-video-1433876150';
const region = 'ap-guangzhou';

const RAW = '/tmp/ep07_raw_segment.mkv';

async function run() {
  console.log('Step 1: Stream segment with -c copy (seek 10s, dur 73s)...');
  const stream = cos.getObjectStream({ Bucket: bucket, Region: region, Key: key });

  const ff1 = spawn('ffmpeg', [
    '-ss', '10', '-i', 'pipe:0',
    '-t', '73',
    '-c', 'copy',
    '-map', '0:v:0', '-map', '0:a:0',
    RAW, '-y'
  ], { stdio: ['pipe', 'inherit', 'inherit'] });

  stream.pipe(ff1.stdin);

  const code1 = await new Promise((resolve) => {
    ff1.on('exit', resolve);
    stream.on('error', (err) => { console.error('Stream error:', err.message); ff1.kill(); resolve(1); });
  });
  console.log('Step 1 completed, code:', code1);
  try { stream.destroy(); } catch (e) {}

  if (code1 !== 0) {
    console.error('Step 1 failed.');
    process.exit(1);
  }

  console.log('Step 2: HDR->SDR tonemap + 1080p H264 AAC...');
  const ff2 = spawn('ffmpeg', [
    '-v', 'error',
    '-i', RAW,
    '-map', '0:v:0', '-map', '0:a:0',
    '-vf', 'zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709:r=tv,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,scale=1920:1080,format=yuv420p',
    '-c:v', 'libx264', '-crf', '22', '-preset', 'medium',
    '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
    '-c:a', 'aac', '-b:a', '192k', '-ac', '2', '-movflags', '+faststart',
    '/tmp/爱情怎么翻译 07-61.mp4', '-y'
  ], { stdio: 'inherit' });

  ff2.on('exit', (code) => {
    console.log('Step 2 exited with code', code);
    try { unlinkSync(RAW); } catch (e) {}
    process.exit(code || 0);
  });
}

run().catch(err => { console.error(err); process.exit(1); });
