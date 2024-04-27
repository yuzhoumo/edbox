# edbox

[![GPLv3 License](https://img.shields.io/badge/License-GPLv3-green.svg)](https://choosealicense.com/licenses/gpl-3.0/)

EdBox is an archiver for Ed courses. Save posts and file attachments from
Ed and generate static sites for local viewing!

🚧 Work in progress 🚧

## Installation

```sh
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

## Usage

- Generate an Ed API token [here](https://edstem.org/us/settings/api-tokens).
- Save `ED_API_TOKEN=YOUR_API_TOKEN_HERE` to a `.env` file (see `.env.template`).
- Run `python3 edbox.py` and choose Ed courses to archive.

If EdBox fails due to network errors or is otherwise interrupted while
archiving, restart the program and it will pick up where it left off.

## Acknowledgements
- [smartspot2's Ed API](https://github.com/smartspot2/edapi)
