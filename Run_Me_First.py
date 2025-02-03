import os
import sys

def add_cwd_to_path():
    cwd = os.getcwd()
    if cwd not in os.environ['PATH']:
        os.environ['PATH'] += os.pathsep + cwd
        print(f"Current working directory added to PATH: {cwd}")
    else:
        print(f"Current working directory already in PATH: {cwd}")

if __name__ == "__main__":
    add_cwd_to_path()
