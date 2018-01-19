from os import environ, pathsep

def _remove_python3_from_PATH(path):
    return pathsep.join(x for x in path.split(pathsep) if 'miniconda' not in x and 'venv/bin' not in x and 'python3' not in x)


ENVIRON = {
    'PATH': _remove_python3_from_PATH(environ.get('PATH', '')),
    }
ENVIRON = {**environ, **ENVIRON}
