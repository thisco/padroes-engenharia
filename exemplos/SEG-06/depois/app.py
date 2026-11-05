import subprocess
import sys

# A lista de argumentos não passa pelo shell: o nome do arquivo é só um argumento.
subprocess.run(["wc", "-l", sys.argv[1]], check=True)
