import json

def main():
    book_path = "books/frankenstein.txt"
    text = get_book_text(book_path)
    print(text)


def get_book_text(path):
    with open(path) as f:
        return f.read()

def count_words(path) :
    words = get_book_text(path).split()
    print(len(words))
    print(type(words))

def count_alphabets(path) :
    words = get_book_text(path).lower()
    alphabets = {}
    for i in "abcdefghijklmnopqrstuvwxyz" :
        alphabets[i] = 0
    for i in "abcdefghijklmnopqrstuvwxyz" :
        count = 0
        for j in words :
            if j==i :
                count = count + 1
        alphabets[i] = count
    print(alphabets)
    return alphabets

def sort_on(dict) :
    return dict["num"]

# main()

count_alphabets("books/frankenstein.txt")
dict = count_alphabets("books/frankenstein.txt")
slist = []
for ch in dict :
    slist.append({"char" : ch, "num" : dict[ch]})
for i in slist :
    print(i)
slist.sort(reverse=True, key=sort_on)
print(slist)
print('--- Begin report of books/frankenstein.txt ---')
print(f'{count_words("books/frankenstein.txt")}words found in the document')
for i in slist :
    print(f"The '{i['char']}' character was found {i['num']} times")
    # for j in i :
    #     print(i[j])
print('--- End report ---')

