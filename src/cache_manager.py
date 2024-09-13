from os import path, makedirs
from pickle import dump, load

def save_results(key, data, folder):
    if not path.exists(f'data/cache/{folder}'):
        makedirs(f'data/cache/{folder}')
    with open(f'data/cache/{folder}/{key}.pkl', 'wb') as f:
        dump(data, f)

def load_results(key,folder):
    try:
        with open(f'data/cache/{folder}/{key}.pkl', 'rb') as f:
            return load(f)
    except FileNotFoundError:
        return None