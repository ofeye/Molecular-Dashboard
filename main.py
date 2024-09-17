import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.getcwd())

from app_2 import get_app

if __name__ == '__main__':
    get_app(False,False).run_server(debug=False)