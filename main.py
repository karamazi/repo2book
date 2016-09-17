from book_generator import BookGenerator
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--repository', help="Git repository URL to convert to latex. "
                                                "Uses 'repo' dir if not provided")



REPO_DIR = 'repo'

def _clone_repo(repo_url):
    subprocess.call(["rm", "-rf", REPO_DIR])
    err_code = subprocess.call(["git", "clone", repo_url, REPO_DIR])
    if err_code:
        raise Exception("Unable to clone git repository! Exit code: {0}".format(err_code))

def main():
    args = parser.parse_args()
    if args.repository:
        _clone_repo(args.repository)
    gen = BookGenerator(REPO_DIR)
    gen.run()

if __name__ == '__main__':
    main()
