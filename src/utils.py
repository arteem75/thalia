import random
import string
import os
import sys



def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def read_lines(path):
    lines = []
    with open(path, 'r') as f:
        for line in f:
            lines.append(line.rstrip('\n'))
    return lines


def mkdir(directory_name):
    """Safe mkdir
    """
    try:
        os.mkdir(directory_name)
    except Exception as e:
        print(e)
        sys.exit(0)


class RandomUtils(object):

    resource_path = os.path.join(os.path.split(__file__)[0], "resources")

    WORDS = read_lines(os.path.join(resource_path, 'words'))

    def __init__(self, seed=None):
        self.r = random.Random(seed)

    def bool(self):
        return self.r.choice([True, False])

    def word(self):
        return self.r.choice(self.WORDS)

    def integer(self, min_int=0, max_int=10):
        return self.r.randint(min_int, max_int)

    def char(self):
        return self.r.choice(string.ascii_letters + string.digits)

    def choice(self, choices):
        return self.r.choice(choices)

    def str(self, length=5):
        return ''.join(self.r.sample(
            string.ascii_letters + string.digits, length))


random = RandomUtils()
