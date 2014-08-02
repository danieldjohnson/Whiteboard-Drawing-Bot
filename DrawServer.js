var net = require('net');

var noop = function(){};
function sendCommand(cmd, callback){
	callback = callback || noop;
	var conn = net.createConnection({path:'./drawbot_uds_socket'});
	conn.on('connect', function() {
	    console.log('Connected to drawbot unix socket server');
	    console.log('Sending data');
	    conn.write(cmd, null, function(){
	    	console.log('- Data processed by server');
	    	callback();
	    });
	    conn.end();
	    console.log('Ending connection')
	});
	conn.on('end', function(){
		console.log("- Disconnected.")
	});
}

var http = require('http'),
	querystring = require('querystring');
http.createServer(function (req, res) {
	console.log('Got web request.');
	switch(req.url) {
	    case '/':
	      console.log("[501] " + req.method + " to " + req.url);
	      res.writeHead(501, "Not implemented", {'Content-Type': 'text/html'});
	      res.end('<html><head><title>501 - Not implemented</title></head><body><h1>Not implemented!</h1></body></html>');
	      break;
	    case '/runcmd':
		    if (req.method == 'POST') {
			    console.log("[200] " + req.method + " to " + req.url);
			    var fullBody = '';

			    req.on('data', function(chunk) {
			      console.log("Received body data:");
			      console.log(chunk.toString());
			      fullBody += chunk.toString();
			    });
			    
			    req.on('end', function() {
      				var decodedBody = querystring.parse(fullBody);
			      	var cmd = decodedBody['cmd'];
			    	console.log('Received command ',cmd);
			  		res.writeHead(200, {'Content-Type': 'text/plain'});
			  		res.write('Received command '+cmd+'\n');
			  		sendCommand(cmd, function(){
			  			res.end('Command is running.')
			  		});
			    });
		    
			} else {
				console.log("[405] " + req.method + " to " + req.url);
				res.writeHead(405, "Method not supported", {'Content-Type': 'text/html'});
				res.end('<html><head><title>405 - Method not supported</title></head><body><h1>Method not supported.</h1></body></html>');
			}
	      break;
	    default:
	      res.writeHead(404, "Not found", {'Content-Type': 'text/html'});
	      res.end('<html><head><title>404 - Not found</title></head><body><h1>Not found.</h1></body></html>');
	      console.log("[404] " + req.method + " to " + req.url);
  };
}).listen(1337, '0.0.0.0');
console.log('Server running at http://0.0.0.0:1337/');