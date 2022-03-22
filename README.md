![https://www.visiomode.org](./resources/banner.png)

---

 [![Build Status](https://github.com/celefthe/visiomode/workflows/build/badge.svg)](https://github.com/celefthe/visiomode/actions)
[![codecov](https://codecov.io/gh/celefthe/visiomode/branch/master/graph/badge.svg?token=1O1WDTTHOH)](https://codecov.io/gh/celefthe/visiomode)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


Visiomode is an open-source platform for rodent touchscreen-based visuomotor tasks. It has been designed to promote the use of touchscreens as an accessible option for implementing a variety of visual task paradigms, with low-cost and ease-of-use as a priority. Visiomode is implemented on the popular Raspberry Pi computer, and provides the user with an intuitive web interface to design and manage experiments. It can be deployed as a stand-alone cognitive testing solution in both freely-moving and head-restrained environments.


**Visiomode is currently work in progress. Things will break. Run at your own risk.**

## Installation


### Raspberry Pi OS

#### Raspberry Pi OS image (recommended)

The most straight-forward way to get Visiomode up and running is to download the latest Visiomode image file from <https://github.com/DuguidLab/visiomode/releases> (`visiomode-X.X.X_raspios-buster.img`) and burn it to a Raspberry Pi SD card using the Raspberry Pi imager (<https://www.raspberrypi.com/software/>). The image comes with the latest version of Visiomode installed, and is set up for the e
rectangular (480x800) Hyperpixel 4.0 display (<https://shop.pimoroni.com/products/hyperpixel-4?variant=12569539706963>).

The password for the default `pi` user is `visiomode`.

Visiomode currently ships on a Raspberry Pi OS Buster image (<https://www.raspberrypi.com/software/operating-systems/#raspberry-pi-os-legacy>), as the Hyperpixel 4.0 display does not yet support the latest Bullseye version (see <https://github.com/pimoroni/hyperpixel4/issues/155>).

#### Via pip / pipx

If you already have a Raspberry Pi set up, or you'd rather burn your own image, you can install Visiomode using `pipx` (<https://pypa.github.io/pipx/>). `pipx` will create an isolated python environment from which Visiomode will run, leaving the system python alone.

First, make sure that your Raspberry Pi OS is up-to-date.

```bash
sudo apt update && sudo apt upgrade
```

Visiomode runs on SDL 2.0. To make sure all system dependencies are present, run

```bash
sudo apt install libsdl2-mixer-2.0-0 libsdl2-image-2.0-0 libsdl2-2.0-0 libsdl2-ttf-2.0-0
```

Install `pipx` using

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

And finally, install Visiomode using `pipx`:

```bash
pipx install visiomode
```


### Linux / MacOS

While Visiomode primarily targets the Raspberry Pi OS, it can be installed on any Linux or MacOS machine, which can be useful for trying out the software before deployment, or for testing. Please note that only the Raspberry Pi OS is officially supported - your milage with any other Linux distribution or MacOS in production may vary.

The recommended way to install Visiomode is via `pipx` (<https://pypa.github.io/pipx/>).

```bash
pipx install visiomode
```

## Usage

To launch Visiomode, open a terminal and run

```bash
visiomode
```

If running over `ssh`, you will need to prepend `DISPLAY=:0` to the `visiomode` command to run the behaviour window on the primary display.

```bash
DISPLAY=:0 visiomode
```


## Upgrading

Use `pipx` to upgrade visiomode:

```bash
pipx upgrade visiomode
```

## Contributing

Visiomode is currently closed to PRs, except bugfixes.


## Funders

<p align="left">
  <img width="250" src="./resources/sidb.jpg"  alt="logo"/>
</p>
