# Importing pybgpstream to collect BGP updates
# from various route collectors
import pybgpstream as bgp

# Setting the time interval for the BGP data
from datetime import datetime, timedelta
now = datetime.now()

# Collecting roughly 15 days of data
# to identify the true origin of prefixes
from_time = now - timedelta(days=1)
until_time = now - timedelta(days=15)

# Creating a BGP instance
stream = bgp.BGPStream(
    # from_time= from_time.strftime("%Y-%m-%d %H:%M:%S"), until_time=until_time.strftime("%Y-%m-%d %H:%M:%S"),
    from_time="2017-04-08 00:00:00", until_time="2017-04-09 00:00:00 UTC",
    # Collecting from Route View Singapore Collector and DC Collector
    collectors=["route-views.sg", "route-views.eqix"],
    # Filtering with only BGP updates
    record_type="updates",
    filter="prefix more 210.180.0.0/16"
)


# Creating a dictionary
# to store the AS paths and origins
as_paths = {}

# Looping through each element in the stream
for elem in stream:

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

    # Printing the information
    print('Update to AS {0} from AS {1} for prefix {2} at {3}:'.format(
        peer_as, origin_as, prefix, timestamp))
    print('AS Path: {0}'.format(as_path))
    print('')

    # Printing the AS paths for each prefix
    for prefix, paths in as_paths.items():
        print(f'Prefix: {prefix}')
        print(f'Total AS paths: {len(paths)}')
        for path in paths:
            print(f'AS path: {" -> ".join(path)}')
            print('')
