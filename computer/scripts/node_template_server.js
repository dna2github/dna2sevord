// get ip
let ip = null;
if (req.headers['x-forwarded-for']) {
    ip = req.headers['x-forwarded-for'].split(",")[0];
} else if (req.connection && req.connection.remoteAddress) {
    ip = req.connection.remoteAddress;
} else {
    ip = req.ip;
}
console.log("client IP is *********************" + ip);


const http = require('http');
const url = require('url');
const path = require('path');
const fs = require('fs');

function route(req, res) {
   let r = url.parse(req.url);
   let f = router;
   let path = r.pathname.split('/');
   let query = {};
   r.query && r.query.split('&').forEach((one) => {
      let key, val;
      let i = one.indexOf('=');
      if (i < 0) {
         key = one;
         val = '';
      } else {
         key = one.substring(0, i);
         val = one.substring(i+1);
      }
      if (key in query) {
         if(Array.isArray(query[key])) {
            query[key].push(val);
         } else {
            query[key] = [query[key], val];
         }
      } else {
         query[key] = val;
      }
   });
   path.shift();
   while (path.length > 0) {
      let key = path.shift();
      f = f[key];
      if (!f) break;
      if (typeof(f) === 'function') {
         return f(req, res, {
            path: path,
            query: query
         });
      }
   }
   router.code(req, res, 404, 'Not Found');
   // if want to serve static files: router.static(req, res, r.pathname);
}

const static_cache = {};
const router = {
   test: (req, res, options) => {
      res.end('hello');
   },
   static: (req, res, filename) => {
      if (!filename || filename === '/') {
         filename = 'index.html';
      }
      filename = filename.split('/');
      if (!filename[0]) filename.shift();
      if (filename.length === 0 || filename.indexOf('..') >= 0) {
         return router.code(req, res, 404, 'Not Found');
      }
      filename = path.join(__dirname, 'static', ...filename);
      if (!fs.existsSync(filename)) {
         return router.code(req, res, 404, 'Not Found');
      }
      res.setHeader('Content-Type', mime_lookup(filename));
      // TODO: try...catch...
      let buf = fs.readFileSync(filename);
      res.end(buf, 'binary');
   }
   code: (req, res, code, text) => {
      res.writeHead(code || 404, text || '');
      res.end();
   }
};

const server = http.createServer((req, res) => {
   route(req, res);
});

const server_port = 8080;
const server_host = '127.0.0.1';

const instance = server.listen(server_port, server_host, () => {
   console.log(`Service is listening at ${server_host}:${server_port}`);
});
