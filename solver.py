from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class mufsolver_server(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/ping":
            mufsolver = {
                "name": "mufsolver",
                "description": "late to the party",
                "concurrent_connection_limit": 10,
                "colour": "#7e0391"}

            mufsolver = json.dumps(mufsolver).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-length", len(mufsolver))
            self.end_headers()
            self.wfile.write(mufsolver)
    
    def do_POST(self):
        if self.path == "/guess":
            guess = {
                "guess": "rumba",
                "shout": "why is everybody shouting"}

            guess = json.dumps(guess).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-length", len(guess))
            self.end_headers()
            self.wfile.write(guess)

PORT = 8080
server = HTTPServer(("", PORT), mufsolver_server)
server.serve_forever()

words_path = "mufs-solver/words_list.txt"
words_list = []
with open(words_path, "r") as f:
    for word in f:
        words_list.append(word.strip())