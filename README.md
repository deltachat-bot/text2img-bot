<img height="180" width="180" src="https://github.com/deltachat-bot/text2img-bot/raw/main/avatar.jpeg">

# Text To Image Bot

[![Latest Release](https://img.shields.io/pypi/v/text2img-bot.svg)](https://pypi.org/project/text2img-bot)
[![CI](https://github.com/deltachat-bot/text2img-bot/actions/workflows/python-ci.yml/badge.svg)](https://github.com/deltachat-bot/text2img-bot/actions/workflows/python-ci.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A text-to-image generator bot for Delta Chat. Generate images from any text prompt.

## Install

```sh
pip install -U text2img-bot
```

## Usage

To configure the bot:

```sh
text2img-bot init bot@example.org SuperHardPassword
```

**(Optional)** To customize the bot name, avatar and status/signature:

```sh
text2img-bot config selfavatar "/path/to/avatar.png"
text2img-bot config displayname "Text To Image"
text2img-bot config selfstatus "Hi, send me some text message to generate an image"
```

Finally you can start the bot with:

```sh
text2img-bot serve
```

To see the available options, run in the command line:

```
text2img-bot --help
```
