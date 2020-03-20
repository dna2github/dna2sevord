const i_fs = require('fs');
const i_path = require('path');
const i_crypto = require('crypto');
const i_exec = require('child_process').exec;
const i_es = require('@elastic/elasticsearch');

const base = i_path.resolve(process.argv[2] || '.');
const ignore = process.argv[3]?process.argv[3].split(','):[];

const BIN_CTAGS = process.env.ES_CTAGS;
const BIN_SHA256 = process.env.ES_SHA256 || '/usr/bin/sha256sum';
const BIN_ENRY = process.env.ES_ENRY;

async function main() {
   const startTime = new Date();
   console.log(startTime.toISOString());
   const client = new i_es.Client({
      node: 'http://127.0.0.1:9200',
      maxRetries: 5,
      requestTimeout: 60000,
      sniffOnStart: true
   });
   await createOrTouchIndexes(client);
   const projectList = await getFileList(base, (item) => item.stat.isDirectory());
   for (let i = 0, n = projectList.length; i < n; i++) {
      const item = projectList[i];
      console.log('[P]', item.name);
      await processDirectory(client, item.name, i_path.join(base, item.name));
   }
   await client.close();
   const endTime = new Date();
   console.log(endTime.toISOString());
}

function getFileStat(filename) {
   return i_fs.lstatSync(filename);
}

async function sh(command) {
   return new Promise((r, e) => {
      i_exec(command, (err, stdout, stderr) => {
         if (err) return e(err);
         r({ stdout, stderr });
      });
   });
}

async function getFileLanguage(filename) {
   let lang = '';
   if (BIN_ENRY) {
      const langRaw = await sh(`${BIN_ENRY} -json '${filename}'`);
      try {
         const obj = JSON.parse(langRaw.stdout);
         if (obj.type === 'Text') {
            lnag = obj.language && obj.language.toLowerCase();
         } else if (obj.type) {
            lang = obj.type.toLowerCase();
         }
      } catch(err) {}
   }
   if (!lang) lang = guessFileLanguage(filename);
   return lang;

   function guessFileLanguage(filename) {
      switch(i_path.extname(filename).toLowerCase()) {
         case '.bazel': return 'python';
         case '.bzl': return 'python';
         case '.sc': return 'python';
         case '.vmodl': return 'java';
         case '.py': return 'python';
         case '.js': return 'javascript';
         case '.ts': return 'typescript';
         case '.sql': return 'sql';
         case '.go': return 'golang';
         case '.cpp': case '.hpp': case '.cc': case '.hh' :return 'c++';
         case '.c': case '.h': return 'c';
         case '.mm': case '.m': return 'objective-c/c++';
         case '.rb': return 'ruby';
         case '.css': return 'css';
         case '.html': return 'html';
         case '.cs': return 'c#';
         case '.pl': return 'perl';
         case '.sh': return 'shell';
         case '.php': return 'php';
         case '.s': return 'asm';
         case '.xml': return 'xml';
         case '.json': return 'json';
         case '.yml': case '.yaml': return 'yaml';
         case '.ini': return 'ini';
      }
      return '';
   }
}

async function getFileHash(filename) {
   const hashRaw = await sh(`${BIN_SHA256} '${filename}'`);
   if (!hashRaw.stdout) return '';
   return hashRaw.stdout.split(' ')[0];
}

async function getFileSymbols(filename) {
   const cmd = `${BIN_CTAGS} --extras=-fq --file-scope=yes --excmd=mix --fields=Klns --output-format=json --sort=no '${filename}'`;
   let symbolRaw = null;
   try {
      symbolRaw = await sh(cmd);
   } catch(err) {
      return [];
   }
   const symbolList = symbolRaw.stdout.split('\n').map((line) => {
      if (!line) return null;
      try {
         return JSON.parse(line);
      } catch(err) {
         return null;
      }
   }).filter((x) => !!x);

   const lines = i_fs.readFileSync(filename).toString().split('\n');
   for (let i = 0, n = symbolList.length; i < n; i++) {
      const item = symbolList[i];
      const line = lines[item.line - 1];
      let pattern = item.pattern.substring(2, item.pattern.length - 2);
      pattern = pattern = pattern.replace(/\\\\/g, '\\');
      pattern = pattern.replace(/\\[/]/g, '/');
      const offset = pattern.split(item.name)[0].length;
      const column = line.split(pattern)[0].length + offset;
      item.metadata = { lineNumber: item.line, column: column, kind: item.kind, language: item.language, scope: item.scope || '' };
      symbolList[i] = { symbol: item.name, metadata: item.metadata };
   }
   return symbolList;
}

async function getFileList(dirpath, filterFn) {
   return new Promise((r, e) => {
      i_fs.readdir(dirpath, (err, list) => {
         if (err) return e(err);
         list = list.map((x) => ({ name: x, stat: i_fs.lstatSync(i_path.join(dirpath, x)), base: dirpath }));
         list = list.filter((item) => !ignore.includes(item.name));
         if (filterFn) list = list.filter(filterFn);
         r(list);
      });
   });
}

async function indexCreateOrUpdate(client, id, index, body) {
   let hid = idHash(id);
   let r, i = 0, exists = false;
   try {
      r = await client.get({
         id: hid, index: index, _source: ['path'],
      });
      while(true) { // wow, infinite
         if (r.body._source.path === id) {
            exists = true;
            break;
         }
         hid = `${id}+${i}`;
         r = await client.get({
            id: hid, index: index, _source: ['path'],
         });
         i ++;
      }
   } catch(err) {
      if (err.meta && err.meta.status === 404) {
         exists = false;
      } else {
         console.log('[e]', id);
         throw err;
      }
   }
   if (exists) {
      await client.update({
         id: hid,
         index: index,
         _source: false,
         refresh: true,
         body: { doc: body }
      });
   } else {
      await client.create({
         id: hid,
         index: index,
         refresh: true,
         body: body
      });
   }

   function idHash(id) {
      return i_crypto.createHash('sha256').update(id, 'utf8').digest('hex');
   }
}

async function indexFile(client, project, item) {
   const filename = i_path.join(item.base, item.name);
   const relative_filename = filename.substring(base.length);
   const hash = await getFileHash(filename);
   let text = '';
   let lang = '';
   if (await isBinaryFile(item)) {
      console.log('[B]', filename);
      lang = 'binary';
   } else {
      console.log('[F]', filename);
      text = i_fs.readFileSync(filename).toString();
      lang = await getFileLanguage(filename);
   }
   console.log(`    Hash=${hash} Language=${lang}`);
   await indexCreateOrUpdate(client, relative_filename, 'vcode_file', {
      hash: hash,
      lang: lang,
      project: project,
      path: relative_filename,
      text: text
   });
}

async function indexSymbols(client, project, item) {
   const filename = i_path.join(item.base, item.name);
   const relative_filename = filename.substring(base.length);
   const symbolList = await getFileSymbols(filename);
   for (let i = 0, n = symbolList.length; i < n; i++) {
      const symbolItem = symbolList[i];
      symbolItem.metadata.proejct = project;
      symbolItem.metadata.filepath = relative_filename;
      await indexCreateOrUpdate(client, `${relative_filename}|${symbolItem.symbol}${symbolItem.metadata.lineNumber}${symbolItem.metadata.column}`, 'vcode_symbol', {
         project: project,
         path: relative_filename,
         metadata: symbolItem.metadata,
         symbol: symbolItem.symbol,
      });
   }
}

async function processDirectory(client, project, dirpath) {
   console.log('[D]', project, dirpath);
   const list = await getFileList(dirpath);
   for (let i = 0, n = list.length; i < n; i++) {
      const item = list[i];
      const filename = i_path.join(item.base, item.name);
      if (item.stat.isDirectory()) {
         await processDirectory(client, project, filename);
      } else if (item.stat.isFile()) {
         await indexFile(client, project, item);
         if (BIN_CTAGS) await indexSymbols(client, project, item);
      } else if (item.stat.isSymbolicLink()) {
         console.log('[L]', filename);
      } else {
         console.log('[U]', filename);
      }
   }
}

async function isBinaryFile(item) {
   return new Promise((r, e) => {
      const filename = i_path.join(item.base, item.name);
      i_fs.open(filename, 'r', (err, fd) => {
         if (err) return e(err);
         const buf = Buffer.alloc(4 * 1024 * 1024);
         i_fs.read(fd, buf, 0, buf.length, 0, (err, n, buf) => {
            i_fs.close(fd, (err) => {
               const i = buf.indexOf(0);
               r(i < n); // read first 4MB; if contains \0, binary file
            });
         });
      });
   });
}

async function createOrTouchIndexes(client) {
   const indexes = await client.cat.indices({
      format: 'json',
      bytes: 'b',
   });
   await createOrTouchSymbolIndex();
   await createOrTouchFileIndex();

   async function createOrTouchSymbolIndex() {
      const symbolIndex = indexes.body.filter((item) => item.index === 'vcode_symbol')[0];
      if (!symbolIndex) {
         const r = await client.indices.create({
            index: 'vcode_symbol',
            body: {
               settings: {
                  index: {
                     analysis: {
                        analyzer: { 'vcode-3gram': { tokenizer: 'vcode-3gram-t' } },
                        tokenizer: { 'vcode-3gram-t': { type: 'ngram', min_gram: 1, max_gram: 3 } },
                     },
                     max_ngram_diff: 2,
                  },
               },
               mappings: {
                  properties: {
                     project: { type: 'keyword', index: true, },
                     path: { type: 'keyword', index: true, },
                     metadata: { type: 'object', enabled: false, },
                     symbol: { type: 'text', analyzer: 'vcode-3gram' },
                  },
               },
            }
         });
      }
   }
   async function createOrTouchFileIndex() {
      const fileIndex = indexes.body.filter((item) => item.index === 'vcode_file')[0];
      if (!fileIndex) {
         const r = await client.indices.create({
            index: 'vcode_file',
            body: {
               settings: {
                  index: {
                     analysis: {
                        analyzer: { 'vcode-3gram': { tokenizer: 'vcode-3gram-t' } },
                        tokenizer: { 'vcode-3gram-t': { type: 'ngram', min_gram: 1, max_gram: 3 } },
                     },
                     max_ngram_diff: 2,
                  },
               },
               mappings: {
                  _source: {
                     excludes: ['text'],
                  },
                  properties: {
                     hash: { type: 'text', index: false, },
                     project: { type: 'keyword', index: true, },
                     path: { type: 'text', analyzer: 'vcode-3gram', },
                     lang: { type: 'keyword', index: true, },
                     text: { type: 'text', analyzer: 'vcode-3gram', },
                  },
               },
            }
         });
      }
   }
}

main().then(() => console.log('Done')).catch((err) => console.error(err, err && err.meta && JSON.stringify(err.meta.body, null, 3) || 'unknown'));
