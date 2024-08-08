SCRIPT_URL = https://raw.githubusercontent.com/GDI-Tools/composer-sync/main/sync_composer.py
SCRIPT_FILE = sync_composer.py

update_script:
	curl -o $(SCRIPT_FILE) $(SCRIPT_URL)

sync_composer: update_script
	python3 sync_composer.py

.DEFAULT_GOAL := sync_composer