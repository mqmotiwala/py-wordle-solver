from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random

class mufsolver_server(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/ping":
            mufsolver = {
                "name": "mufsolver",
                "description": "ill amaze ya, in a good way... and bad",
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

            # create two lists
            ## 
            iterable_list = read_list(filtered_words)
            words_list = iterable_list.copy()
            
            # prepare guess
            try: 
                guess_results = game_state['guess_results']
                last_guess = guess_results[-1]['guess'] 
                last_result = guess_results[-1]['result']
                
                print("\nguess:", last_guess, "result:", last_result)
                # grey letters don't require position information so treat it as a set
                grey_letters = set()
                yellow_letters = {}
                green_letters = {}
                for i, letter in enumerate(last_guess):
                    if last_result[i] == 0:
                        grey_letters.add(letter)
                    elif last_result[i] == 1:
                        yellow_letters[letter]=i
                    else:
                        green_letters[letter]=i
                
                # check for grey
                if len(grey_letters):
                    for word in iterable_list:
                        for letter in word:
                            # need to add extra conditionals for yellow and green letters for words with duplicate letters
                            if letter in grey_letters and letter not in yellow_letters and letter not in green_letters:
                                words_list.remove(word)
                                # print(word, letter, "is grey")
                                break
                    update_list(words_list, filtered_words)
                    print("Grey check complete. Remaining words:", str(len(words_list)))

                # check for yellow
                if len(yellow_letters):
                    iterable_list = read_list(filtered_words)
                    words_list = iterable_list.copy()
                    for word in iterable_list:
                        for letter in yellow_letters:
                            # if yellow letter not in word
                            # or, if word has yellow letter in yellow spot
                            if letter not in word or word[yellow_letters[letter]] == letter:
                                words_list.remove(word)
                                # print(word, letter, "doesn't exist in word or is in pos", str(yellow_letters[letter]))
                                break
                    update_list(words_list, filtered_words)
                    print("Yellow check complete. Remaining words:", str(len(words_list)))

                # check for green
                if len(green_letters):
                    iterable_list = read_list(filtered_words)
                    words_list = iterable_list.copy()
                    for word in iterable_list:
                        for letter in green_letters:
                            if letter not in word or word[green_letters[letter]] != letter:
                                words_list.remove(word)
                                # print(word, letter, "is not in positition", str(green_letters[letter]))
                                break
                    update_list(words_list, filtered_words)
                    print("Green check complete. Remaining words:", str(len(words_list)))

                # pick a guess based on latest words_list
                guess = {'guess':random.choice(words_list)}

            except KeyError:
                # start of game, no results history
                guess = {'guess':random.choice(words_list)}

            # send guess
            guess = json.dumps(guess).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-length", len(guess))
            self.end_headers()
            self.wfile.write(guess)
        
        if self.path == "/results":
            content_length = int(self.headers['Content-Length'])
            game_results = self.rfile.read(content_length).decode('utf-8')
            game_results = json.loads(game_results)

            game_won = game_results['results']['players'][0]['games_played'][-1]['correct']
            answer = game_results['results']['games'][0]['answer']
            num_turns = len(game_results['results']['players'][0]['games_played'][-1])

            if game_won:
                print(f"You correctly guessed {answer} in {num_turns} turns!")
            else:
                print(f"You lost after {num_turns} turns. The answer was {answer}")
            
            # # update filtered list to full list for next game 
            # # # and reset variables 
            # update_list(read_list(all_words), filtered_words)
            # green_letters.clear()
            # yellow_letters.clear()
            # green_letters.clear()
            
def read_list(file):
    list = []
    with open(file, 'r') as f:
        for word in f:
            list.append(word.strip())
    
    return list

def update_list(list, file):
    with open(file, 'w') as f:
        for word in list:
            f.write(word + '\n')

all_words = "words_list.txt"
filtered_words = 'dynamic_list.txt'

# initiate filtered list as full list prior to game start
update_list(read_list(all_words), filtered_words)

PORT = 8080
server = HTTPServer(("", PORT), mufsolver_server)
server.quiet = True
server.serve_forever()