import http.server

port = 8000
server_address = ("",port)
handler_class = http.server.CGIHTTPRequestHandler

server = http.server.HTTPServer(server_address, handler_class)
print("Server listening to localhost:"+str(port))
print("Please access http://localhost:"+str(port))
server.serve_forever()
