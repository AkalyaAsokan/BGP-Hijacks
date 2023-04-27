import pybgpstream as bgp

class sub_MoAS:
    
    def __init__(self, project, record_type, filter):
        self.as_paths = {}
        self.stream = bgp.BGPStream(
            project=project,
            # Filtering with only given BGP updates
            record_type=record_type,
            # Filter based on prefix and MoAS
            filter=filter
        )
    
    def sub_moas(self, prefix, as_path):
        if prefix in self.as_paths:
            for existing_as_path in self.as_paths[prefix]:
                # If the existing AS path is a sub-path of the new AS path, then it is a sub-MoAS
                if existing_as_path != as_path and existing_as_path[:-1] == as_path[:-1]:
                    print(f"Sub-MoAS detected for prefix {prefix} with AS path {as_path}")
        else:
            self.as_paths[prefix] = [as_path]
    
    def run(self):
        for elem in self.stream:
            if elem.type == 'A':
                prefix = elem.fields['prefix']
                as_path = elem.fields['as-path'].split(' ')
                self.sub_moas(prefix, as_path)
