# Composer Sync

### Description
- Simple script that use wp cli for synchronization between WordPress backend and composer json

### Requirements
- Python 3.x
- WP CLI
- Bedrock installation
- Active internet connection

### Note
- Script will get all custom vendors from Wartung API, please add your custom vendors to [wartung.grand-didital.de](wartung.grand-didital.de)

### Usage
- Put `sync_composer.py` on the same level where is your `composer.json` file
- In terminal run `python3 sync_composer.py`

### Autoupdate method: RECOMMENDED
- To not download this script every time just copy `Makefile` file in your projects and run `make` in terminal this 
will automatically download the last version of the script and synchronize your composer file, script will remove itself after sync

### Note
- The script will update WordPress core and all plugins that found on WordPress backend
- Plugins that are found in WordPress backend and not in `composer.json` will be deleted from `composer.json`
