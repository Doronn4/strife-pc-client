import subprocess
import sys


def install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except Exception:
        pass


if __name__ == '__main__':
    install('pycryptodomex')
    install('wxpython')
    install('rsa')
    install('pypubsub')
