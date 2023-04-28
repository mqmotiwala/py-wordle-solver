from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random
import logging
import datetime as dt
import os

# logging preferences
current_time = dt.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
verbose_format = logging.Formatter("%(asctime)s: %(levelname)s - %(message)s")
preferred_format = logging.Formatter("%(message)s")
log_file = f"logs/{current_time}-game.log"
if not os.path.exists("logs"): os.makedirs("logs")

# file handler
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(preferred_format)
file_handler.setLevel(logging.INFO) # level=DEBUG will also print the 

# stream handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(preferred_format)
stream_handler.setLevel(logging.WARNING)

# logger settings
logger = logging.getLogger()
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)

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
        # grey letters don't require position information so treat it as a set
        global words_dict
        grey_letters = set()
        yellow_letters = {}
        green_letters = {}
        
        if self.path == "/guess":
            # read game state
            content_length = int(self.headers['Content-Length'])
            game_state = self.rfile.read(content_length).decode('utf-8')
            game_state = json.loads(game_state)

            # review results
            if 'guess_results' in game_state:
                guess_results = game_state['guess_results']
                num_guesses = len(guess_results)
                last_guess = guess_results[-1]['guess']
                last_result = guess_results[-1]['result']
                
                logger.info(f"\nguess #{num_guesses}: {last_guess} - result: {last_result}")
                for i, letter in enumerate(last_guess):
                    if last_result[i] == 0:
                        grey_letters.add(letter)
                    elif last_result[i] == 1:
                        yellow_letters[letter]=i
                    else:
                        green_letters[letter]=i
                
                # check for grey
                if len(grey_letters):
                    for word in words_dict.copy().keys():
                        for letter in word:
                            # need to add extra conditionals for yellow and green letters for words with duplicate letters
                            if letter in grey_letters and letter not in yellow_letters and letter not in green_letters:
                                words_dict.pop(word)
                                logger.debug(f"{letter} in {word} is grey")
                                break
                    logger.info(f"Grey check complete. Remaining words: {str(len(words_dict))}")

                # check for yellow
                if len(yellow_letters):
                    for word in words_dict.copy().keys():
                        for letter in yellow_letters:
                            # if yellow letter not in word
                            # or, if word has yellow letter in yellow spot
                            if letter not in word or word[yellow_letters[letter]] == letter:
                                words_dict.pop(word)
                                logger.debug(f"{letter} does not exist in {word} or is in position {str(yellow_letters[letter])}")
                                break
                    logger.info(f"Yellow check complete. Remaining words: {str(len(words_dict))}")

                # check for green
                if len(green_letters):
                    for word in words_dict.copy().keys():
                        for letter in green_letters:
                            if letter not in word or word[green_letters[letter]] != letter:
                                words_dict.pop(word)
                                logger.debug(f"{letter} is not in position {str(green_letters[letter])}")
                                break
                    logger.info(f"Green check complete. Remaining words: {str(len(words_dict))}")

            else: 
                # start of game, no results history
                # build words_dict with the full set of words
                words_dict = build_dict(words_list_file)
                grey_letters.clear()
                yellow_letters.clear()
                green_letters.clear()
            
            # pick a guess based on latest words_list
            guess_word = get_guess(words_dict)
            guess = {'guess':guess_word}

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

            last_game = game_results['results']['players'][0]['games_played'][-1]
            if 'correct' in last_game:
                game_won = last_game['correct'] # should be true
            else:
                game_won = False

            answer = game_results['results']['games'][0]['answer']
            num_turns = len(game_results['results']['players'][0]['games_played'][-1]['guess_results'])
            
            logger.info("\n-----------------------------------------\n")
            if game_won:
                logger.warning(f"You correctly guessed '{answer}' in {num_turns} turns!")
            else:
                logger.warning(f"You lost after {num_turns} turns. The answer was '{answer}'.")

def get_guess(words_dict):
    # build a set of words with the maximum number of unique letters in remaining set
    max_unique = max(words_dict.values())
    best_guesses = {k for k,v in words_dict.items() if v == max_unique}
    
    logger.info(f"max_unique = {max_unique}. Remaining words: {len(best_guesses)}")
    logger.info(best_guesses)
    return random.choice(list(best_guesses))

def build_dict(words_list_file):
    with open(words_list_file, 'r') as f:
        word_dict = {}
        for word in f:
            word = word.strip()
            word_dict[word] = len(set(word))
        
    return word_dict

# initiate words_dict for the game
words_list_file = "words_list.txt"
words_dict = build_dict(words_list_file)

PORT = 8080
server = HTTPServer(("", PORT), mufsolver_server)
server.quiet = True
server.serve_forever()