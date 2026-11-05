import subprocess
import sys

# O nome do arquivo vem de quem chama: com shell=True, "; rm -rf ~" vira comando.
subprocess.run(f"wc -l {sys.argv[1]}", shell=True, check=True)
