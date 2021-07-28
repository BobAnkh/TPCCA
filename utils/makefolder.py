import os

def makefolder(*args):
    dir = os.path.join(*args)
    if not os.path.exists(dir):
        os.makedirs(dir)
