import os, subprocess, getpass

# Feel free to edit this file, but note that `make deploy` expects the service file to be output as `new.service`
# It, of course, is renamed to `localizer.service` as it's moved to `/etc/systemd/system/`

text = open("new.service").read()
text = text.replace(
    "GCPATH",
    subprocess.check_output(["/usr/bin/bash", "-c", "which gunicorn"])
    .decode("utf-8")
    .strip(),
)
text = text.replace("PATH", os.getcwd())
text = text.replace("WHO", getpass.getuser())

os.remove("new.service")
with open("new.service", "w") as f:
    f.write(text)
