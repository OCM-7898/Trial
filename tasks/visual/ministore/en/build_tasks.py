import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from visual_logic import write

if __name__ == "__main__":
    write("en", HERE)
