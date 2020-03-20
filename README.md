# Jumbef's Minecraft-Discord-sender

## Requirements

* discord-webhook==0.7.1
* watchdog==0.10.2

`pip install -r requirements.txt`

## Usage

`python3 main.py`

Enter the require informations:

* Your minecraft directory (if not default location
* A Discord webhook (ask your discord admin)

Then click Test/Save button and look at on Discord for the test message.

Once in game, all your new screenshots (F2) will be sent to Discord ans you can prefix a chat line by `::msg ` to send it too.

## Background behavior

The script look at your 'screenshots' folder and 'latest.log' file then react on new '.png' files and new '::msg' matching lines.

It also look at you 'launcher-settings.json' file to use your Minecraft display name to title the Discord messages and filter logs

Your Minecraft/Mojang account remains safely private.
