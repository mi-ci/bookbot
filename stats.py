
def make_custom_list(path):
    custom_list =[{"char":k, "num" :v} for k, v in get_char_dic(path).items()]
    custom_list.sort(key=lambda x: x["num"], reverse=True)
    for i in custom_list :
        if i["char"].isalpha():
            print(f"{i["char"]}: {i["num"]}")

def get_char_dic(path):
    chars = {}
    for c in get_book_text(path):
        lowered = c.lower()
        if lowered in chars:
            chars[lowered] +=1
        else:
            chars[lowered] = 1
    return chars

        

def get_num_words(path):
    num_words = len(get_book_text(path).split())
    return num_words

def get_book_text(path):
    with open(path) as f:
        return f.read()