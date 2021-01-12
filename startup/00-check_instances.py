import os
import sys
cmd = "ps -aux | grep -i bsui | wc -l"
max_instances = 5
num_instances = int(os.popen(cmd).read()) - 1

assert num_instances <= max_instances, "Max number of instances exceeded"

print(str(num_instances) + " instances of bsui currently running")

