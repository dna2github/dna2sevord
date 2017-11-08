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
