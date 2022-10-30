# Moved to https://git.getcryst.al/crystal/misc/localizer

# localizer
dashboard tool to help you keep track of what time it is for your friends

## Use case:
Large groups with people in different timezones. Perhaps you'd deploy this, and keep your browser homepage as the instance?

## Usage:
* Be on a linux system with `sudo`, `pip`, `python`, and `make`
* Review `sample.service` and `Makefile` to make sure you don't need to make any tweaks
* Finally, `make deploy`
* Set up nginx, apache, or some other web server to proxy to `http://127.0.0.1:8000`
    * If you'd like to change the gunicorn port to avoid a conflict, edit `sample.service` and change the `--bind` argument
## Remvoe:
`make undeploy`

## Update:
`make update`
