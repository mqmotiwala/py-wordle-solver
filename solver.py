from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random

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
            # read game state
            content_length = int(self.headers['Content-Length'])
            game_state = self.rfile.read(content_length).decode('utf-8')
            game_state = json.loads(game_state)
            print(game_state)

            # prepare guess
            try: 
                results = game_state['guess_results']
                last_guess = results[-1]['guess'] 
                last_result = results[-1]['result']
                
                print(last_guess, last_result)
                grey_letters = []
                yellow_letters = []
                green_letters = []
                for i, letter in enumerate(last_guess):
                    if last_result[i] == 0:
                        grey_letters.append(letter)
                    elif last_result[i] == 1:
                        yellow_letters.append((i, letter))
                    else:
                        green_letters.append((i, letter))
                
                backup_list = words_list
                for word in words_list:
                    for letter in green_letters:
                        if word[letter[0]] != letter[1]:
                            print(word, word[letter[0]], " is not equal to ", letter[1])
                            backup_list.remove(word)

                print(backup_list)

            except KeyError:
                # start of game, no results history
                print("keyerror")

            guess = {}
            guess['guess'] = random.choice(words_list)

            # send guess
            guess = json.dumps(guess).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-length", len(guess))
            self.end_headers()
            self.wfile.write(guess)

words_path = "mufs-solver/words_list.txt"
words_list = []
with open(words_path, "r") as f:
    for word in f:
        words_list.append(word.strip())

PORT = 8080
server = HTTPServer(("", PORT), mufsolver_server)
server.serve_forever()