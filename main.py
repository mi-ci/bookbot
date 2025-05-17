from stats import get_num_words, make_custom_list
import sys

def main():
    if len(sys.argv)<2 :
        print("Usage: python3 main.py <path_to_book>")
        sys.exit(1)
    print(f"Found {get_num_words(sys.argv[1])} total words")
    make_custom_list(sys.argv[1])


main()