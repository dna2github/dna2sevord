const a = require('./a');
const b = require('./b');
const c = require('./c');

c.test = 1;
a.act();
b.act();
console.log('in main, c.test =', c.test)

