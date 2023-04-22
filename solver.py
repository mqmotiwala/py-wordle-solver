words_path = "words_list.txt"

words_list = []
with open(words_path, "r") as f:
    for word in f:
        words_list.append(word)

print(words_list)