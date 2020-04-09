// program | node logwrapper.js <NAME> <LOG_DIR> <LOGINSIGHT_URL> <FROM_TAG?
// e.g.                         app    /tmp/logs https://127.0.0.1:20200/api/v1/events/ingest/0 vcode
if (!process.argv[2] || !process.argv[3]) {
   console.log(`Usage: node logwrapper.js <NAME> <LOG_DIR> <?LOGINSIGHT_URL ?FROM_TAG>`);
   process.exit(0);
}

process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

const i_path = require('path');
const i_fs = require('fs');
const i_url = require('url');
const i_http = {};

const FLAME_NAME = process.argv[2];
const FLAME_LOCAL_LOG_DIR = i_path.resolve(process.argv[3]);
const FLAME_LOGINSIGHT_URL = process.argv[4] || '';
const FLAME_LOGINSIGHT_TAG = process.argv[5] || '';
let FLAME_LOGINSIGHT = null;
if (FLAME_LOGINSIGHT_URL) {
   FLAME_LOGINSIGHT = i_url.parse(FLAME_LOGINSIGHT_URL);
   if (FLAME_LOGINSIGHT.protocol === 'https:') {
      i_http.lib = require('https');
      FLAME_LOGINSIGHT.port = FLAME_LOGINSIGHT.port || '443';
   } else {
      i_http.lib = require('http');
      FLAME_LOGINSIGHT.port = FLAME_LOGINSIGHT.port || '80';
   }
}
const FLAME_ROTATE_SIZE = 1024 * 1024 * (parseInt(process.env.LOG_ROTATE_SIZE || '100')); // 100 MB

const env = {
   heartbeat: true,
   currentLogFilename: null,
   currentFd: -1,
   currentSize: 0,
   buffer: [],
   netbuf: [],
   processing: false,
   netprocessing: 0,
   lastLine: '',
};

const helper = {
   fs: {
      open: async (filename, flags) => new Promise((r, e) => {
         i_fs.open(filename, flags, (err, fd) => {
            if (err) return e(err);
            r(fd);
         });
      }),
      create: async (filename) => {
         const fd = await helper.fs.open(filename, 'w+');
         await helper.fs.close(fd);
      },
      lstat: async (filename) => new Promise((r, e) => {
         i_fs.lstat(filename, (err, stat) => {
            if (err) return e(err);
            r(stat);
         });
      }),
      close: async (fd) => new Promise((r, e) => {
         i_fs.close(fd, (err, fd) => {
            if (err) return e(err);
            r();
         });
      }),
      write: async (fd, buf) => new Promise((r, e) => {
         i_fs.write(fd, buf, (err, n) => {
            if (err) return e(err);
            r(n);
         });
      })
   }
};

function newLogName() {
   const d = new Date();
   return `${FLAME_NAME}-${d.getUTCFullYear()}-${d.getUTCMonth()}-${d.getUTCDate()}-${d.getUTCHours()}-${d.getUTCMinutes()}-${d.getUTCSeconds()}.log`;
}

async function getLogSize(filename) {
   const stat = await helper.fs.lstat(filename);
   return stat.size;
}

async function processNextLine() {
   if (!env.buffer.length) return;
   if (env.processing) return;
   env.processing = true;
   const line = env.buffer.shift();
   try {
      await processLogToLocalFile(line);
   } catch (err) {
      console.log(`[Ff]< [${new Date().toISOString()}] ${line}`);
   }
   // TOOD: how we deal with the case when there are too many lines
   if (line && FLAME_LOGINSIGHT) {
      env.netbuf.push(line);
      processNextLineToLogInsight();
   }
   env.processing = false;
   processNextLine();
}

async function processNextLineToLogInsight() {
   if (!env.netbuf.length) return;
   if (env.netprocessing > 20) return;
   env.netprocessing ++;
   const line = env.netbuf.shift();
   try {
      await processLogToLogInsight(line);
   } catch (err) {
      console.log(`[Fn]< [${new Date().toISOString()}] ${line}`);
   }
   env.netprocessing --;
   processNextLineToLogInsight();
}

async function processLogToLocalFile(line) {
   // console.log(new Date().getTime(), 'local', line);
   if (env.currentFd < 0) {
      const filename = i_path.join(FLAME_LOCAL_LOG_DIR, newLogName());
      if (!i_fs.existsSync(filename)) await helper.fs.create(filename);
      env.currentSize = await getLogSize(filename);
      env.currentFd = await helper.fs.open(filename, 'a');
   }
   const buf = Buffer.from(line + '\n');
   await helper.fs.write(env.currentFd, buf);
   env.currentSize += buf.length;
   if (env.currentSize > FLAME_ROTATE_SIZE) {
      await helper.fs.close(env.currentFd);
      env.currentFd = -1;
   }
}

async function processLogToLogInsight(line) {
   return new Promise((r, e) => {
      const timestamp = ~~(new Date().getTime() / 1000);
      const obj = {
         events: [{
            text: line,
            timestamp,
         }]
      };
      if (FLAME_LOGINSIGHT_TAG) {
         obj.events[0].fields = [{ name: 'src', content: FLAME_LOGINSIGHT_TAG }];
      }
      const buf = Buffer.from(JSON.stringify(obj));
      const req = i_http.lib.request({
         hostname: FLAME_LOGINSIGHT.host,
         port: FLAME_LOGINSIGHT.port,
         method: 'POST',
         path: FLAME_LOGINSIGHT.path,
         headers: {
            'Content-Type': 'application/json',
            'Content-Length': buf.length
         }
      }, (res) => {
         const stype = ~~(res.statusCode / 100);
         if (stype === 2) {
            r();
         } else {
            e(res);
         }
      });
      req.on('error', (err) => { e(err); });
      req.write(buf);
      req.end();
   });
}

process.stdin.on('data', (chunk) => {
   const lines = chunk.toString().split('\n');
   lines[0] += env.lastLine;
   env.lastLine = lines.pop();
   lines.forEach((line) => env.buffer.push(line));
   processNextLine();
});

process.stdin.on('close', () => {
   if (env.lastLine) {
      env.buffer.push(env.lastLine);
      processNextLine();
   }
   env.heartbeat = false;
   console.log('stdin over ...');
});

process.stdin.on('readable', () => {
   process.stdin.read();
});

process.stdin.setEncoding('utf-8');
process.stdin.resume();

function beat() {
   if (!env.heartbeat) return;
   setTimeout(beat, 1000);
}
beat();
