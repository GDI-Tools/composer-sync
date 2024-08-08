# Composer Sync

### Description
- Simple script that use wp cli for synchronization between wordpress backend and composer json

### Requirements
- Python 3.x
- WP CLI

### Usage
- Put `sync_composer.py` on the same level where is your `composer.json` file
- In terminal run `python3 sync_composer.py`

### Autoupdate method: RECOMMENDED
- To not download this script every time just copy `Makefile` file in your projects and run `make` in terminal this will automaticaly download the last version of the script and synchronize your compose file

### Note
- The script will update Wordpress core and all plugins that found on Wordpress backend
- Plugins that are found in Wordpress backend and not in `composer.json` will be deleted from `composer.json`

### Recommendation 
- Backup your `composer.json` before run this script