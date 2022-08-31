import os, subprocess

text = open("new.service").read()
text = text.replace(
    "GCPATH",
    subprocess.check_output(["/usr/bin/bash", "-c", "which gunicorn"])
    .decode("utf-8")
    .strip(),
)
text = text.replace("PATH", os.getcwd())

os.remove("new.service")
with open("new.service", "w") as f:
    f.write(text)
