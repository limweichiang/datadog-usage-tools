# Overview

This project is intended to easily create Datadog dashboards and monitors definitions with customized thresholds.

# Prerequisites / Environment

This tool was developed and tested on MacOS 13.4, using an M1 (ARM achitecture) laptop. 

# Getting Started

1) Clone the code from this repository into your working environment.
```
% git clone https://github.com/limweichiang/datadog-usage-tools
```

2) Change into the project directory.
```
% cd datadog-usage-tools
```

3) Here we assume the Python virtual environment (venv) module exists on your system. If not, you should install and use it, for the safety of your system (you don't want broken system dependencies) and so that you can follow the instructions going forward from here. If you prefer not to use venv, skip forward to step (5).
```
% python3 -m venv venv
```

4) Activate the virtual environment.
```
% source venv/bin/activate 
```

5) Install the Python depedencies needed for this tool to work.
```
(venv) % pip install -r requirements.txt 
```

6) Edit the conf.yaml file to configure the parameters that will be used to build the dashboard.

7) Run the build.
```
% python3 build.py 
```

8) Assuming all goes well, you should see an output/ file now created, containing the definition of the Datadog Estimated Usage dashboard (dashboard.json), as well as a number of files starting with 'datadog-estimated-usage-...' which are monitor JSON definitions.
