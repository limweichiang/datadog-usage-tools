import yaml
import json
import sys
import os

def set_dashboard_timeseries_widget(dashboard, section_name, widget_name, commit_value):
    for section_iter in dashboard['widgets']:
        #print(section_iter['definition']['title'])
        if section_iter['definition']['title'] != section_name:
            continue
        
        for widget_iter in section_iter['definition']['widgets']:
            #print(section_iter['definition']['title'], "-", widget_iter['definition']['title'], "-", widget_iter['definition']['type'])
            if not (widget_iter['definition']['title'] == widget_name and widget_iter['definition']['type'] == "timeseries"):
                continue

            for marker_iter in widget_iter['definition']['markers']:
                if marker_iter['label'] != "Committed":
                    continue

                #print(section_iter['definition']['title'], "-", widget_iter['definition']['title'], "-", widget_iter['definition']['type'], "-", section_iter['definition']['title'])
                marker_iter['value'] = "y = " + str(commit_value)
                
                # break marker_iter loop
                break
            
            # break widget_iter loop
            break
        
        # break section_iter loop
        break

# Main execution function
def main():
    # Read configurations
    try:
        with open("./conf.yaml", "r") as conf_file:
            conf_raw = conf_file.read()
            conf = yaml.safe_load(conf_raw)
    except Exception as e:
        sys.exit("Fatal Error: Could not load configuration file.")

    # Read dashboard templates
    try:
        with open("./templates/dashboard.json", "r") as dashboard_file: 
            dashboard = json.load(dashboard_file)
    except Exception as e:
        sys.exit("Fatal Error: Could not load dashboard template.")

    # Set dashboard meta information
    if "dashboard" in conf:
        try:
            dashboard['title'] = conf['dashboard']['title']
            dashboard['description'] = conf['dashboard']['description']
        except KeyError:
            print("Error configuring dashboard. Invalid dict key.")

    # Set marker values in Log widgets
    if "logs" in conf:
        set_dashboard_timeseries_widget(dashboard, "Log Analytics Estimated Usage", "Logs Ingested Bytes - Cumulative", conf['logs']['ingested-bytes']['commit'])
        set_dashboard_timeseries_widget(dashboard, "Log Analytics Estimated Usage", "Logs Indexed Events - Cumulative", conf['logs']['indexed-logs']['commit'])

    # Set marker values in Infra Host widgets
    if "infrastructure-hosts" in conf:
        set_dashboard_timeseries_widget(dashboard, "Infrastructure Estimated Usage", "Infrastructure Hosts", conf['infrastructure-hosts']['commit'])

    # Set marker values in APM widgets
    if "apm" in conf:
        set_dashboard_timeseries_widget(dashboard, "APM Estimated Usage", "APM Hosts", conf['apm']['hosts']['commit'])
        set_dashboard_timeseries_widget(dashboard, "APM Estimated Usage", "APM Ingested Bytes - Cumulative", conf['apm']['ingested-bytes']['commit'])
        set_dashboard_timeseries_widget(dashboard, "APM Estimated Usage", "APM Indexed Spans - Cumulative", conf['apm']['indexed-spans']['commit'])

    # Set marker values in Custom Metric widgets
    if "custom-metrics" in conf:
        set_dashboard_timeseries_widget(dashboard, "Custom Metrics Estimated Usage", "Custom Metrics", conf['custom-metrics']['custom-metrics']['commit'])
        set_dashboard_timeseries_widget(dashboard, "Custom Metrics Estimated Usage", "Custom Metrics Ingested", conf['custom-metrics']['custom-metrics-ingested']['commit'])
    
    # Set marker values in RUM widgets
    if "rum" in conf:
        set_dashboard_timeseries_widget(dashboard, "Real User Monitoring Estimated Usage", "Mobile RUM Sessions - Cumulative", conf['rum']['mobile-rum-sessions']['commit'])
        set_dashboard_timeseries_widget(dashboard, "Real User Monitoring Estimated Usage", "Browser RUM Sessions - Cumulative", conf['rum']['browser-rum-sessions']['commit'])
        set_dashboard_timeseries_widget(dashboard, "Real User Monitoring Estimated Usage", "Browser RUM with Replay Sessions - Cumulative", conf['rum']['browser-rum-replay-sessions']['commit'])

    # Write out updated dashboard
    try:
        os.makedirs("output", exist_ok=True)
        with open("./output/dashboard.json", "w") as output_dashboard_file:
            json.dump(dashboard, output_dashboard_file)
    except Exception as e:
        sys.exit("Fatal Error: Could not write dashboard to output file")


# Kickstart main() if called directly
if __name__ == "__main__":
    main()