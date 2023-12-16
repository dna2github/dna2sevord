const c = require('./c');

module.exports = {
   act: function () {
      c.test ++;
      console.log('in b, c.test =', c.test);
   }
};
