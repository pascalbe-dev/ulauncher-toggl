# Ulauncher Toggl

> [ulauncher](https://ulauncher.io/) Extension to access your [Toggl](https://track.toggl.com/timer) timer.

## Demo

https://github.com/pascalbe-dev/ulauncher-toggl/assets/26909176/0c39b4cc-45af-4ebc-ad8d-526055d97746

## Features

- view the current time entry
- stop the current time entry
- start a new time entry (without project)
- restart a time entry from your history

## Requirements

- [ulauncher 5](https://ulauncher.io/)
- Python > 3

## Installation

Open ulauncher preferences window -> extensions -> add extension and paste the following url:

`https://github.com/pascalbe-dev/ulauncher-toggl.git`

## Configuration

- Before usage you need to configure your Toggl API token in plugin preferences. Find your API token [here](https://track.toggl.com/profile#api-token-label).

## Contribution

Please refer to [the contribution guidelines](./CONTRIBUTING.md)

## Local development

### Requirements

- `less` package installed
- `inotify-tools` package installed

### Steps

1. Clone the repo `git clone https://github.com/pascalbe-dev/ulauncher-toggl.git`
2. Cd into the folder `cd ulauncher-toggl`
3. Watch and deploy your extension for simple developing and testing in parallel `./watch-and-deploy.sh` (this will restart ulauncher without extensions and deploy this extension at the beginning and each time a file in this directory changes)
4. Check the extension log `less /tmp/ulauncher-extension.log +F`
5. Check ulauncher dev log `less /tmp/ulauncher.log +F`
