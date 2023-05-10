import yaml
import json
import sys
import os
from jinja2 import Template

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

def set_monitor(template_pathname, commit_threshold, warning_threshold = None, notify_contact = None):
    # Open monitor template, load as JSON
    try:
        with open(template_pathname, "r") as template_file:
            template = json.load(template_file)
    except Exception as e:
        sys.exit("Fatal Error: Could not load template " + template_pathname + ".")

    # Set Commit / Alert threshold
    template['options']['thresholds']['critical'] = commit_threshold
    query_template = Template(template['query'])
    template['query'] = query_template.render(critical_threshold_placeholder=commit_threshold)

    # Set Warning threshold if configured, else remove it.
    if(warning_threshold is None):
        del template['options']['thresholds']['warning']
    else:
        template['options']['thresholds']['warning'] = warning_threshold

    # Set contact for alert/warning notification, if provided.
    if(notify_contact is not None):
        template['message'] = template['message'] + "\n" + notify_contact

    # Craft monitor definition template file
    outfile_name = template['name']
    outfile_name = outfile_name.lower()
    outfile_name = outfile_name.replace(' ', '_')
    outfile_name = outfile_name + ".json"

    # Write out updated monitor
    try:
        os.makedirs("output", exist_ok=True)
        with open("./output/" + outfile_name, "w") as outfile:
            json.dump(template, outfile)
    except Exception as e:
        sys.exit("Fatal Error: Could not write monitor \"" + template['name'] + "\" to output file \"" + outfile_name + "\".")
    

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
        set_monitor("./templates/datadog_estimated_usage_-_logs_ingested_bytes.json", conf['logs']['ingested-bytes']['commit'], conf['logs']['ingested-bytes']['warning'], conf['monitors']['notify'])
        set_monitor("./templates/datadog_estimated_usage_-_logs_indexed_events.json", conf['logs']['indexed-logs']['commit'], conf['logs']['indexed-logs']['warning'], conf['monitors']['notify'])

    # Set marker values in Infra Host widgets
    if "infrastructure-hosts" in conf:
        set_dashboard_timeseries_widget(dashboard, "Infrastructure Estimated Usage", "Infrastructure Hosts", conf['infrastructure-hosts']['commit'])
        set_monitor("./templates/datadog_estimated_usage_-_infrastructure_host_count.json", conf['infrastructure-hosts']['commit'], conf['infrastructure-hosts']['warning'], conf['monitors']['notify'])

    # Set marker values in APM widgets
    if "apm" in conf:
        set_dashboard_timeseries_widget(dashboard, "APM Estimated Usage", "APM Hosts", conf['apm']['hosts']['commit'])
        set_dashboard_timeseries_widget(dashboard, "APM Estimated Usage", "APM Ingested Bytes - Cumulative", conf['apm']['ingested-bytes']['commit'])
        set_dashboard_timeseries_widget(dashboard, "APM Estimated Usage", "APM Indexed Spans - Cumulative", conf['apm']['indexed-spans']['commit'])
        set_monitor("./templates/datadog_estimated_usage_-_apm_host_count.json", conf['apm']['hosts']['commit'], conf['apm']['hosts']['warning'], conf['monitors']['notify'])
        set_monitor("./templates/datadog_estimated_usage_-_apm_ingested_bytes.json", conf['apm']['ingested-bytes']['commit'], conf['apm']['ingested-bytes']['warning'], conf['monitors']['notify'])
        set_monitor("./templates/datadog_estimated_usage_-_apm_indexed_spans.json", conf['apm']['indexed-spans']['commit'], conf['apm']['indexed-spans']['warning'], conf['monitors']['notify'])

    # Set marker values in Custom Metric widgets
    if "custom-metrics" in conf:
        set_dashboard_timeseries_widget(dashboard, "Custom Metrics Estimated Usage", "Custom Metrics", conf['custom-metrics']['custom-metrics']['commit'])
        set_dashboard_timeseries_widget(dashboard, "Custom Metrics Estimated Usage", "Custom Metrics Ingested", conf['custom-metrics']['custom-metrics-ingested']['commit'])
        set_monitor("./templates/datadog_estimated_usage_-_custom_metrics.json", conf['custom-metrics']['custom-metrics']['commit'], conf['custom-metrics']['custom-metrics']['warning'], conf['monitors']['notify'])
        set_monitor("./templates/datadog_estimated_usage_-_custom_metrics_ingested.json", conf['custom-metrics']['custom-metrics-ingested']['commit'], conf['custom-metrics']['custom-metrics-ingested']['warning'], conf['monitors']['notify'])
    
    # Set marker values in RUM widgets
    if "rum" in conf:
        set_dashboard_timeseries_widget(dashboard, "Real User Monitoring Estimated Usage", "Mobile RUM Sessions - Cumulative", conf['rum']['mobile-rum-sessions']['commit'])
        set_dashboard_timeseries_widget(dashboard, "Real User Monitoring Estimated Usage", "Browser RUM Sessions - Cumulative", conf['rum']['browser-rum-sessions']['commit'])
        set_dashboard_timeseries_widget(dashboard, "Real User Monitoring Estimated Usage", "Browser RUM with Replay Sessions - Cumulative", conf['rum']['browser-rum-replay-sessions']['commit'])
        set_monitor("./templates/datadog_estimated_usage_-_mobile_rum_sessions.json", conf['rum']['mobile-rum-sessions']['commit'], conf['rum']['mobile-rum-sessions']['warning'], conf['monitors']['notify'])
        set_monitor("./templates/datadog_estimated_usage_-_browser_rum_sessions.json", conf['rum']['browser-rum-sessions']['commit'], conf['rum']['browser-rum-sessions']['warning'], conf['monitors']['notify'])
        set_monitor("./templates/datadog_estimated_usage_-_browser_rum_with_replay_sessions.json", conf['rum']['browser-rum-replay-sessions']['commit'], conf['rum']['browser-rum-replay-sessions']['warning'], conf['monitors']['notify'])

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