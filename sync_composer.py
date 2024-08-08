import json
import os
import subprocess

# Define your custom vendors here
CUSTOM_VENDORS = {
    "advanced-custom-fields-pro": "wpengine",
    "wp-migrate-db-pro": "deliciousbrains-plugin",
    "borlabs-cookie": "borlabs",
    "wp-seopress-pro": "seopress",
    "gd-accordion-block": "grand-digital",
    # Add other custom plugins and their vendors as needed
}

# Exclude plugins here, the value left empty, key should be plugin slug
EXCLUDE_PLUGINS = {
    "advanced-cache.php": ""
}

current_dir = os.path.dirname(os.path.abspath(__file__))
composer_file = os.path.join(current_dir, 'composer.json')

command = ["ddev", "wp", "plugin", "list", "--format=json"]
# Run the command
result = subprocess.run(command, capture_output=True, text=True)

# Check if the command was successful
if result.returncode == 0:
    # Store the output in a variable
    output_json = result.stdout

    # Parse the JSON output
    plugins = json.loads(output_json)

# Load the existing composer.json
with open(composer_file, 'r') as file:
    composer = json.load(file)

# Ensure the 'require' section exists
if 'require' not in composer:
    composer['require'] = {}

# Extract currently required plugins from composer.json
current_requirements = set(composer['require'].keys())

# Add/update plugins in the 'require' section
for plugin in plugins:
    name = plugin['name']
    version = plugin['version']
    status = plugin['status']

    if status not in ['active', 'inactive']:
        continue

    # Check if plugin is excluded
    if name in EXCLUDE_PLUGINS:
        continue

    # Determine the vendor
    if name in CUSTOM_VENDORS:
        vendor = CUSTOM_VENDORS[name]
        composer['require'][f'{vendor}/{name}'] = version
    else:
        vendor = 'wpackagist-plugin'
        composer['require'][f'wpackagist-plugin/{name}'] = version

# Determine the plugins that should be kept based on the current plugin list
installed_plugins = {f'{CUSTOM_VENDORS[plugin["name"]]}/{plugin["name"]}' if plugin["name"] in CUSTOM_VENDORS else f'wpackagist-plugin/{plugin["name"]}' for plugin in plugins}

# Get wordpress version
command = ["ddev", "wp", "core", "version"]
# Run the command
result = subprocess.run(command, capture_output=True, text=True)

# Check if the command was successful
if result.returncode == 0:
    # Store the output in a variable
    wp_version = result.stdout

composer['require']['roots/wordpress'] = wp_version.strip()

# Remove plugins from composer.json that are no longer installed
plugins_to_remove = current_requirements - installed_plugins
for plugin in plugins_to_remove:
    if plugin.startswith('wpackagist-plugin/') or any(plugin.startswith(f'{vendor}/') for vendor in CUSTOM_VENDORS.values()):
        del composer['require'][plugin]

# Save the updated composer.json
with open(composer_file, 'w') as file:
    json.dump(composer, file, indent=4)

print("composer.json has been updated.")
