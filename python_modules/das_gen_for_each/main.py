import sys
from os import path

if __name__ == '__main__':
    sys.path += [
        path.join(path.dirname(__file__), '..'),
        path.join(path.dirname(__file__), '..',
            '..', 'dasShared', 'python_modules'),
    ]
    from gen_for_each import GenForEach
    GenForEach(argv=sys.argv).run()
