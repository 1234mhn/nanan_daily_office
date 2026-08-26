const fs = require('fs');
const env = fs.readFileSync('/root/.openclaw/workspace/skills/tencent-cos-skill/.env','utf8');
env.split('\n').forEach(l=>{const m=l.match(/^([A-Z0-9_]+)=(.*)$/);if(m){process.env[m[1]]=m[2].replace(/^['\"]|['\"]$/g,'')}});
const COS = require('/root/.openclaw/workspace/skills/tencent-cos-skill/node_modules/cos-nodejs-sdk-v5');
const cos = new COS({ SecretId: process.env.TENCENT_COS_SECRET_ID, SecretKey: process.env.TENCENT_COS_SECRET_KEY });
const Bucket = 'korean-video-1433876150';
const Region = 'ap-guangzhou';
const Key = "爱情怎么翻译全集/Can This Love Be Translated？ S01E05 - 第 5 集 - 2160p WEB-DL HDR10 H265 DDP 5.1 Atmos.mkv";
cos.getObjectUrl({ Bucket, Region, Key, Expires: 7200, Sign: true }, (err, data) => {
  if (err) { console.error('ERR:', err.message || err); process.exit(1); }
  fs.writeFileSync('/tmp/ep5_signed_url.txt', data.Url);
  console.log('Saved URL length:', data.Url.length);
});
