var test = true;

setInterval(function () {
  if (test) {
    console.log('Hello World');
  } else {
    console.log('Bye-bye');
    process.exit();
  }
}, 1000);

/*
NodeJS Inject:
   node test.js
   ps -ef | grep node
   node debug -p <pid>
   > sb('test.js', 4);
   > c
   > repl
   >>> test = false;
   >>> ^C
   > c
*/
