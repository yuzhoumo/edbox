<img src=".github/logo.svg" alt="edbox logo" />

[![GPLv3 License](https://img.shields.io/badge/License-GPLv3-green.svg)](https://choosealicense.com/licenses/gpl-3.0/)

EdBox is an archiver for Ed courses. Save posts and file attachments from
Ed and generate static sites for local viewing!

Built with Python and Alpine.js + Tailwind.

![screenshot](.github/screenshot.png)

## Features

- Archives course info and posts to json files
- Downloads file attachments and user profile photos
- Generates an offline, searchable webpage for each archived course
- Webpages display Ed's formatting options and math notations (LaTeX)
- Anonymous usernames are correctly generated (matches what's shown on Ed)
- Color-coded post categories and user profiles

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

## Development

If you would like to modify the web directory, please note that you may need
to regnerate the included tailwind.css file (see tailwind docs).

## Acknowledgements
- [smartspot2's Ed API](https://github.com/smartspot2/edapi)
