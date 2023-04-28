import re
import pybgpstream as bgp

class FakePathDetector:
    def __init__(self, collectors, time_from, time_to, record_type, filter):
        # Dictionary to store the prefixes with multiple origin ASes
        self.prefixes = {}
        self.stream = bgp.BGPStream(
            # from_time= from_time.strftime("%Y-%m-%d %H:%M:%S"), until_time=until_time.strftime("%Y-%m-%d %H:%M:%S"),
            from_time=time_from, until_time=time_to,
            # Collecting from Route View Singapore Collector and DC Collector
            collectors=collectors,
            # Filtering with only BGP updates
            record_type=record_type,
            filter=filter
        )
        as_paths = {}
        print("first trace")

        # Looping through each element in the stream
        for elem in self.stream:

            print("second trace")
            self.detect_fake_as_paths(elem)
            print("fourth trace")
            # Extracting the as-path
            """
            try:
                as_path = elem.fields['as-path'].split(' ')
            
            except KeyError:
            # Ignore elements that don't have prefix or AS path fields
                continue
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
                    print('') """


    def detect_fake_as_paths(self, elem):
        

        fake_as_pattern = r"\b(0+|65534|65535|([2-9]|[1-9][0-9]|[1-9][0-9][0-9]|[1-9][0-9][0-9][0-9]|[1-9][0-9][0-9][0-9][0-9]|1[0-1][0-9][0-9][0-9]|12[0-8][0-9][0-9])[ \t]*)+\b"

        
        
        # Loop through each element in the BGP stream
        try:
            prefix = elem.fields["prefix"]
            as_path = elem.fields["as-path"]
            origin_as = as_path.split()[-1]
            
            
            # If the prefix is already in the dictionary, check if this is a fake path
            if prefix in self.prefixes:
                
                # If the origin AS is different from the previously recorded origin ASes, check for fake AS path
                if origin_as not in self.prefixes[prefix]:
                    print("third trace")
                    # Check if the AS path matches the fake pattern
                    if fake_as_pattern.match(as_path):
                        print(f"Fake AS path detected for prefix {prefix}: {as_path}")
            
            # Add the origin AS to the dictionary for this prefix
            self.prefixes.setdefault(prefix, set()).add(origin_as)
        
        except KeyError:
            # Ignore elements that don't have prefix or AS path fields
            print("Ignoring element with missing field(s)")
            print(elem.fields)
            pass


fake = FakePathDetector(
    collectors = ["route-views.sg", "route-views.eqix"],
    time_from = "2017-04-08 00:00:00",
    time_to = "2017-04-10 00:00:00 UTC",
    record_type="updates",
    filter="prefix more 210.0.0.0/16"
)

