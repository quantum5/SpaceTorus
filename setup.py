from distutils.core import setup
import py2exe
from glob import glob
import sys
import os

sys.argv.append("py2exe")

data = []

parent = os.path.dirname(__file__)
join = os.path.join

resources = [(r"space_torus\assets\textures", ["*.*"]),
             (r"space_torus\assets\models\asteroids", ["*.obj", "*.mtl"]),
             # (r"space_torus\assets\music", ["*.*"]),
             (r"space_torus", ["*.py", "*.json"])]

for res in resources:
    dir, patterns = res
    for pattern in patterns:
        for file in glob(join(dir, pattern)):
            print "Packaging", join(parent, file), "->", dir
            data.append((dir, [join(parent, file)]))

setup(
    windows=["bootloader.py"],
    data_files=data,
    options={
                "py2exe": {
                        "unbuffered": True,
                        "optimize": 2,
                        "dist_dir": "bin",
                        "excludes": ['_ssl', 'unittest', 'doctest', 'difflib', 'inspect']
                }
        }
)

os.chdir("bin")
try:
    os.unlink('Space Torus.exe')
except OSError:
    pass
os.rename('bootloader.exe', 'Space Torus.exe')