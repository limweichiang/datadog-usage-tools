import json
import requests
import sys
import os
import re
import argparse

# Main execution function
def main():
    
    # Collect CLI opts for connecting to Datadog account
    parser = argparse.ArgumentParser(description="Datadog monitor definition extractor")
    parser.add_argument("--api-key", required=True, help="Datadog account API Key")
    parser.add_argument("--app-key", required=True, help="Datadog account Application Key")
    args = parser.parse_args()
    AUTH_HEADERS = {'Accept': 'application/json', 'DD-APPLICATION-KEY': args.app_key.strip(), 'DD-API-KEY': args.api_key.strip()}

    # Calling API to search for monitors
    monitor_search_params = {'query':'tag:"estimated_usage"'}
    monitor_search_result = requests.get("https://api.datadoghq.com/api/v1/monitor/search", params=monitor_search_params, headers=AUTH_HEADERS)
    
    if (monitor_search_result.status_code != 200):
        sys.exit("Received status code " + str(monitor_search_result.status_code) + " \"" + monitor_search_result.reason + "\"" + " when listing monitors.")

    monitor_search = monitor_search_result.json()
    monitor_ids = []
    if "monitors" in monitor_search:
        for monitor_iter in monitor_search["monitors"]:
            monitor_ids.append(monitor_iter["id"])

    # Iterate through monitors. Scrub and save as files.
    for monitor_id_iter in monitor_ids:
        monitor_result = requests.get("https://api.datadoghq.com/api/v1/monitor/" + str(monitor_id_iter), headers=AUTH_HEADERS)
        if (monitor_result.status_code != 200):
            sys.exit("Received status code " + str(monitor_result.status_code) + " \"" + monitor_result.reason + "\"" + " when extracting monitor ID " + monitor_id_iter + ".")
 
        # Scrub organization related details
        monitor_definition = monitor_result.json()
        del monitor_definition['org_id']
        del monitor_definition['created_at']
        del monitor_definition['created']
        del monitor_definition['modified']
        del monitor_definition['deleted']
        del monitor_definition['overall_state_modified']
        del monitor_definition['overall_state']
        del monitor_definition['creator']
        del monitor_definition['id']

        # Set "estimated_usage" tag to get monitor displayed on Estimated Usage dashboard.
        monitor_definition['tags'] = ["estimated_usage"]

        # Clean up query value, replacing with jinja format placeholder.
        monitor_definition['query'] = re.sub('\S+$', '{{critical_threshold_placeholder}}', monitor_definition['query'])
        
        # Craft monitor definition template file
        outfile_name = monitor_definition['name']
        outfile_name = outfile_name.lower()
        outfile_name = outfile_name.replace(' ', '_')
        outfile_name = outfile_name + ".json"

        # Write out monitor template
        try:
            os.makedirs("templates", exist_ok=True)
            with open("./templates/" + outfile_name, "w") as outfile:
                json.dump(monitor_definition, outfile)
        except Exception as e:
            sys.exit("Fatal Error: Could not write " + monitor_definition['name'] + "to template file")

# Kickstart main() if called directly
if __name__ == "__main__":
    main()
