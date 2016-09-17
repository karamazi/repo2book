from book_generator import BookGenerator
import argparse

ROOT_DIR = 'sgs'


def main():
    gen = BookGenerator(ROOT_DIR)
    gen.run()

if __name__ == '__main__':
    pass
    #main()
