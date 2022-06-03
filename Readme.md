# secure-squash-root
## Build a signed efi binary which mounts a verified squashfs image as root

### [Install](#install) - [Configuration](#configuration) - [Usage](#usage) - [Development](#development)

This library provides an easy way to create a signed efi binary which mounts a
verified squashfs image as root.

## Install

There are no installation packages at the moment.
You can clone the repository, see [Development](development)

## Configuration

HOOKS=(base systemd autodetect secure-squash-root modconf block filesystems keyboard)
setup efibootmgr , systemd-boot

## Usage

/mnt/root: mount before first setup

Under construction.

## Development

Setup a python3 virtual environment:

```shell
git clone git@github.com:brandsimon/secure-squash-root.git
python3 -m venv .venv
.venv/bin/pip install -e . --no-deps
```

Run unit tests:

```shell
.venv/bin/python -m unittest tests/unit/tests.py
```

## Known issues

Known issues
autodetect hook: error, but irrelevant

500 MB efi parition


squashfs-tools

shellcheck, flake8
python static analysis

add integration test for mkinitcpio presets



Test mount handler via bwrap and set -x
/proc/cmdline is just a file
