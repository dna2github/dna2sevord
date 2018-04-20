const c = require('./c');

module.exports = {
   act: function () {
      c.test ++;
      console.log('in a, c.test =', c.test);
   }
};
