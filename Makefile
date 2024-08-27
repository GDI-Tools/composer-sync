SCRIPT_URL = https://raw.githubusercontent.com/GDI-Tools/composer-sync/main/sync_composer.py
SCRIPT_FILE = sync_composer.py

project_state:
	@plugins=$$(ddev wp plugin list --format=json); \
	active_theme=$$(ddev wp theme list --status=active --field=name); \
	echo "{\"plugins\": $$plugins, \"active-theme\": \"$$active_theme\"}" > project-state.json


update_script:
	curl -o $(SCRIPT_FILE) $(SCRIPT_URL)

sync_composer: update_script project_state
	python3 sync_composer.py
	rm $(SCRIPT_FILE)

.DEFAULT_GOAL := sync_composer