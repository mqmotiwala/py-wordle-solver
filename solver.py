from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random
import time

class mufsolver_server(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

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
            # print(game_state)

            # prepare guess
            try: 
                results = game_state['guess_results']
                last_guess = results[-1]['guess'] 
                last_result = results[-1]['result']
                
                print(last_guess, last_result)
                grey_letters = {}
                yellow_letters = {}
                green_letters = {}
                for i, letter in enumerate(last_guess):
                    if last_result[i] == 0:
                        # grey letters don't require position information
                        grey_letters[letter]=True
                    elif last_result[i] == 1:
                        yellow_letters[letter]=i
                    else:
                        green_letters[letter]=i
                
                # check for grey
                iterable_words_list = read_list_from_file()
                words_list = iterable_words_list.copy()
                print("starting round, words_list length is: ", str(len(words_list)))
                for word in iterable_words_list:
                    for letter in word:
                        if letter in grey_letters:
                            words_list.remove(word)
                            # print(word, letter, "is grey")
                            break
                
                write_list_to_file(words_list)

                print("purged greys, words list size is now: ", str(len(words_list)))

                # check for green
                iterable_words_list = read_list_from_file()
                words_list = iterable_words_list.copy()
                for word in iterable_words_list:
                    for letter in green_letters:
                        if letter not in word or word[green_letters[letter]] != letter:
                            words_list.remove(word)
                            # print(word, letter, "is not in positition", str(green_letters[letter]))
                            break
                
                write_list_to_file(words_list)
                
                # pick a guess based on latest words_list
                print("forced greens, words list size is now: ", str(len(words_list)))
                guess = {'guess':random.choice(words_list)}

            except KeyError:
                # start of game, no results history
                # print("keyerror")
                guess = {'guess':'audio'}

            # send guess
            guess = json.dumps(guess).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-length", len(guess))
            self.end_headers()
            self.wfile.write(guess)

def write_list_to_file(list):
    with open('iwl.txt', 'w') as f:
        for word in list:
            f.write(word + '\n')
    
    time.sleep(10)

def read_list_from_file():
    list = []
    with open('iwl.txt', 'r') as f:
        for word in f:
            list.append(word.strip())
    
    return list

words_path = "mufs-solver/words_list.txt"
iterable_words_list = []
with open(words_path, "r") as f:
    for word in f:
        iterable_words_list.append(word.strip())

write_list_to_file(iterable_words_list)

PORT = 8080
server = HTTPServer(("", PORT), mufsolver_server)
server.quiet = True
server.serve_forever()