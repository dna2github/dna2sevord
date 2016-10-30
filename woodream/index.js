var express = require('express'),
    app = express();

app.get('/', (req, res) => {
   res.write('Hello World!');
   res.send();
});


var server_host = '127.0.0.1',
    server_port = 8080;

app.listen(server_port, server_host, () => {
   console.log(
      'Woodream is running and listening at ' +
      server_host + ':' + server_port
   );
});
