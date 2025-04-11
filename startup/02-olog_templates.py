from datetime import datetime as datetime
########### OLOG CUSTOMIZATION #############
# Time scans
# scan_time description template
scan_time_desc_template ="""
Scan ID: {{start.scan_id}}
Date and Time: {{ datetime.fromtimestamp( int(start.time)).strftime('%Y/%m/%d %H:%M:%S' ) }}

Scan name: {{start.scan_name}}
Scan type: {{start.scan_type}}
Plan name: {{ start.plan_name}}
X axis: {{ start.plot_Xaxis }}, {{start.num}} points with {{delay}} second delay
Plotted Y axis: {{ start.plot_Yaxis }}
Detectors: {{ start.detectors }}

ADDITIONAL INFO:
Unique ID (UID): {{start.uid}}

"""


# 1D scans
# scan_1D description template
scan_1D_desc_template ="""
Scan ID: {{start.scan_id}}
Date and Time: {{ datetime.fromtimestamp( int(start.time)).strftime('%Y/%m/%d %H:%M:%S' ) }}

Scan name: {{start.scan_name}}
Scan type: {{start.scan_type}}
Plan name: {{ start.plan_name}}
X axis: {{ start.plot_Xaxis }}, from {{start.start}} to {{start.stop}} every {{start.delta}}
Plotted Y axis: {{ start.plot_Yaxis }}
Detectors: {{ start.detectors }}

ADDITIONAL INFO:
Unique ID (UID): {{start.uid}}

"""

#2D scans

# scan_multi_1D description template
scan_multi_1D_desc_template ="""
Scan ID: {{start.scan_id}}
Date and Time: {{ datetime.fromtimestamp( int(start.time)).strftime('%Y/%m/%d %H:%M:%S' ) }}
Scan No: {{start.multi_pos}} of {{start.multi_num}} (1st scan in series is ID: str( int({{start.scan_id}})-int( {{start.multi_pos}}) ) ) 

Scan name: {{start.scan_name}}
Scan type: {{start.scan_type}}
Plan name: {{ start.plan_name}}
X axis: {{ start.scan_X_axis }}, from {{start.start}} to {{start.stop}} every {{start.delta}}
multi axis: {{ start.multi_axis }}, from {{start.multi_start}} to {{start.multi_stop}} every {{start.multi_delta}}
Plotted Y axis: {{ start.plot_Yaxis }}
Detectors: {{ start.detectors }}

ADDITIONAL INFO:
Unique ID (UID): {{start.uid}}

"""

# scan_2D description template
scan_2D_desc_template ="""
Scan ID: {{start.scan_id}}
Date and Time: {{ datetime.fromtimestamp( int(start.time)).strftime('%Y/%m/%d %H:%M:%S' ) }}

Scan name: {{start.scan_name}}
Scan type: {{start.scan_type}}
Plan name: {{ start.plan_name}}
Plotted X axis: {{ start.plot_Xaxis }}, from {{start.X_start}} to {{start.X_stop}} every {{start.X_delta}}
Plotted Y axis: {{ start.plot_Yaxis }}, from {{start.Y_start}} to {{start.Y_stop}} every {{start.Y_delta}}
Plotted Z axis: {{ start.plot_Zaxis }}
Detectors: {{ start.detectors }}

ADDITIONAL INFO:
Unique ID (UID): {{start.uid}}

"""

#Create dictionary to map the olog template to the plan_name value.
  #For description templates.
desc_templates = {'scan_time' : scan_time_desc_template,
                  'scan_1D' : scan_1D_desc_template,
                  'scan_multi_1D' : scan_multi_1D_desc_template,
                  'scan_2D' : scan_2D_desc_template}


