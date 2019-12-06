

1. 

ERROR: unsatisfiable constraints:
  libgcj (missing):
    required by: world[libgcj]
  libssl (missing):
    required by: world[libssl]
  so:libgcj.so.17 (missing):
    required by: pdftk-2.02-r1[so:libgcj.so.17]
The command '/bin/sh -c apk add --no-cache libgcj libssl pdftk' returned a non-zero code: 4
Makefile:5: recipe for target 'build' failed


2. 

Collecting Flask==0.12.4
  Downloading https://files.pythonhosted.org/packages/2e/48/f1936dadac2326b3d73f2fe0a964a87d16be16eb9d7fc56f09c1bea3d17c/Flask-0.12.4-py2.py3-none-any.whl (81kB)
ERROR: Could not find a version that satisfies the requirement ItsDangerous==1.0.0 (from -r src/requirements.txt (line 3)) (from versions: 0.9, 0.9.1, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.21, 0.22, 0.23, 0.24, 1.1.0)
ERROR: No matching distribution found for ItsDangerous==1.0.0 (from -r src/requirements.txt (line 3))
The command '/bin/sh -c pip install -r src/requirements.txt' returned a non-zero code: 1
Makefile:5: recipe for target 'build' failed


