import json
import os
import subprocess
import urllib.request

# Exclude plugins here, the value left empty, key should be plugin slug
EXCLUDE_PLUGINS = {
    "advanced-cache.php": ""
}


class SyncComposer:
    def __init__(self):
        self.wartung_api = 'https://wartung-api.grand-digital.de/api/custom-vendor/'
        self.composer_backup = None

    def backup_composer(self, composer_file_path):
        try:
            print("Backing up composer backup...")
            with open(composer_file_path, 'r') as file:
                composer = json.load(file)
                backup_composer_data = json.dumps(composer, indent=4)
                self.composer_backup = backup_composer_data
        except Exception as error:
            print(f"Failed to backup composer")
            raise Exception(f"Failed to backup composer with error: {error}")

    def get_all_vendors(self):
        try:
            print("Getting all vendors...")
            with urllib.request.urlopen(self.wartung_api) as response:
                data = response.read()
                vendors_data = json.loads(data.decode('utf-8'))
                return vendors_data

        except Exception as error:
            print(f"Can't get vendors from Wartung API")
            raise Exception(f"Can't get vendors from Wartung API with error {error}")

    def extract_custom_vendors(self, vendors):
        print("Extracting custom vendors...")
        vendors_dict_data = {vendor.get('slug'): vendor.get('name') for vendor in vendors}
        return vendors_dict_data

    def get_composer_file_path(self):
        print("Getting composer file path...")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        composer_file = os.path.join(current_dir, 'composer.json')

        if os.path.exists(composer_file):
            return composer_file
        else:
            print(f"Can't find composer.json in {current_dir}")
            raise Exception(f"Can't find composer.json in {current_dir}")

    def get_installed_plugins_wp(self):
        command = ["ddev", "wp", "plugin", "list", "--format=json"]

        try:
            print("Getting installed plugins from WordPress installation...")
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode == 0:
                output_json = result.stdout
                plugins = json.loads(output_json)
                filtered_plugins = [plugin for plugin in plugins if plugin.get('status') != 'must-use']
                return filtered_plugins
        except Exception as error:
            print(f"Can't get installed plugins from WP failed with error: {error}")
            exit(1)

    def clear_data(self):
        print("Clearing data...")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        composer_file = os.path.join(current_dir, 'sync_composer.py')
        if os.path.exists(composer_file):
            os.remove(composer_file)

    def get_wordpress_version(self):
        try:
            print("Getting WordPress version...")
            command = ["ddev", "wp", "core", "version"]
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                wp_version = result.stdout
                return wp_version
            else:
                raise Exception(f"Can't get wordpress version from WP failed with error: {result.stderr}")
        except Exception as error:
            print(f"Can't get wordpress version from WP failed")
            raise Exception(f"Can't get wordpress version from WP failed with error: {error}")

    def set_composer_require(self, composer_file_path, wp_plugins, vendors):
        try:
            print("Setting composer requirements...")
            with open(composer_file_path, 'r') as file:
                composer = json.load(file)

                if 'require' not in composer:
                    composer['require'] = {}

                current_requirements_data = set(composer['require'].keys())

                for plugin in wp_plugins:
                    name = plugin['name']
                    version = plugin['version']
                    status = plugin['status']

                    if status not in ['active', 'inactive']:
                        continue

                    if name in EXCLUDE_PLUGINS:
                        continue

                    if name in vendors:
                        vendor = vendors[name]
                        composer['require'][f'{vendor}/{name}'] = version
                    else:
                        vendor = 'wpackagist-plugin'
                        composer['require'][f'{vendor}/{name}'] = version

                installed_plugins = {f'{vendors[plugin["name"]]}/{plugin["name"]}' if plugin[ "name"] in vendors else f'wpackagist-plugin/{plugin["name"]}' for plugin in wp_plugins}
                wp_version = self.get_wordpress_version()
                composer['require']['roots/wordpress'] = wp_version.strip()

                plugins_to_remove = current_requirements_data - installed_plugins

                print("Synchronize composer requirements...")
                for plugin in plugins_to_remove:
                    if plugin.startswith('wpackagist-plugin/') or any(
                            plugin.startswith(f'{vendor}/') for vendor in vendors.values()):
                        del composer['require'][plugin]

            with open(composer_file_path, 'w') as file:
                json.dump(composer, file, indent=4)

        except Exception as err:
            print(f"Can't set requirement for {composer_file_path}")
            raise Exception(f"Can't set requirement for {composer_file_path} failed with error: {err}")

    def check_composer_installation(self, composer_file_path):
        print("Run composer in dry-run mode to check all plugins please wait...")
        command = ["ddev", "composer", "update", "--dry-run"]
        try:
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode != 0:
                with open(composer_file_path, 'w') as file:
                    file.write(self.composer_backup)
                print(f"Dry-run command failed. Rolled back to previous composer.json.\nError: {result.stderr}")
            else:
                print(f"Composer validation successfully.")
        except Exception as error:
            print("During execution composer in dry-run mode failed")

    def sync_composer(self):
        try:
            vendors = self.get_all_vendors()
            vendors_dict = self.extract_custom_vendors(vendors)
            composer_file = self.get_composer_file_path()
            self.backup_composer(composer_file)
            wp_installed_plugins = self.get_installed_plugins_wp()
            self.set_composer_require(composer_file, wp_installed_plugins, vendors_dict)
            self.check_composer_installation(composer_file)
            self.clear_data()
            print("Composer synced successfully.")

        except Exception as error:
            print(f"Can't get installed plugins from WP failed with error: {error}")
            self.clear_data()
            exit(1)

if __name__ == "__main__":
    sync_composer = SyncComposer()
    sync_composer.sync_composer()
