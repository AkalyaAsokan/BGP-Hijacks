# Importing pybgpstream to collect BGP updates 
# from various route collectors
import pybgpstream as bgp

# Setting the time interval for the BGP data
from datetime import datetime, timedelta
now = datetime.now()

# Collecting roughly 15 days of data 
# to identify the true origin of prefixes
from_time = now - timedelta(days=15)
until_time = now - timedelta(days=1)

# Opening a file
##### Each group member collected multiple files from different collectors 
# for the same prefixes individually and then combined to reduce time taken to gather training data #####
f = open('training_data_01.txt', 'w')

# Creating a BGP instance
stream = bgp.BGPStream(
    from_time= from_time.strftime("%Y-%m-%d %H:%M:%S"), until_time=until_time.strftime("%Y-%m-%d %H:%M:%S"),
    # Collecting from atleast one Route Collector from each continent 
    # and a few more from bigger continents to get diverse data
    collectors=["route-views.sydney",
                "route-views.sg",
                "route-views2.routeviews.org"],
    # Filtering with only BGP updates
    record_type="updates",
    # Filtering using an arbitrary prefix to reduce the amount of data obtained
    filter="prefix more 210.180.0.0/16"
)

# Creating a dictionary 
# to store the AS paths and origins
as_paths = {}

# Looping through each element in the stream
for elem in stream:
    try:
        # Extracting the as-path
        as_path = elem.fields['as-path'].split(' ')
        # Extracting the origin AS
        origin_as = as_path[-1]
        # Extracting the peer AS
        peer_as = elem.peer_asn
        # Extracting the prefix
        prefix = elem.fields['prefix']
        # Extract the timestamp
        timestamp = elem.time

        # Updating the AS paths dictionary
        if prefix in as_paths:
            as_paths[prefix].append(as_path)
        else:
            as_paths[prefix] = [as_path]

        # Write the output to the file
        f.write('Update to AS {0} from AS {1} for prefix {2} at {3}\n'.format(peer_as, origin_as, prefix, timestamp))
        f.write('AS Path: {0}\n'.format(as_path))
        f.write('\n')

    except:
        continue

# Printing the AS paths for each prefix
for prefix, paths in as_paths.items():
    f.write(f'Prefix: {prefix}\n')
    f.write(f'Total AS paths: {len(paths)}\n')
    for path in paths:
        f.write(f'AS path: {" -> ".join(path)}\n')
    f.write('\n')
