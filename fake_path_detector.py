import os
import re
import pybgpstream as bgp

class FakePathDetector:
    def __init__(self, collectors, time_from, time_to, record_type, filter, training_files):
        # Dictionary to store the prefixes with multiple origin ASes
        self.prefixes = {}
        self.established_paths = self.read_training_data(training_files)

        self.stream = bgp.BGPStream(
            from_time=time_from, until_time=time_to,
            collectors=collectors,
            record_type=record_type,
            filter=filter
        )

        # Looping through each element in the stream
        for elem in self.stream:
            self.detect_fake_as_paths(elem)

    def read_training_data(self, training_files):
      established_paths = {}

      for file in training_files:
          with open(file, 'r') as f:
              lines = f.readlines()
              for line in lines:
                  if "AS Path:" in line:
                      prefix_line = lines[lines.index(line) - 1]
                      prefix = re.search(r'for prefix (.+?) at', prefix_line).group(1)

                      as_path_match = re.search(r'\[(.*)\]', line)
                      if as_path_match:
                          as_path = as_path_match.group(1).split(', ')
                      else:
                          continue

                      if prefix not in established_paths:
                          established_paths[prefix] = []

                      established_paths[prefix].append(as_path)

      return established_paths

    def detect_fake_as_paths(self, elem):
        try:
            prefix = elem.fields["prefix"]
            as_path = elem.fields["as-path"].split()

            # If the prefix is not in the established paths, it's a new prefix
            if prefix not in self.established_paths:
                print(f"New prefix detected: {prefix}")
                return

            # If the AS path is not in the established paths for this prefix, it's a fake path
            if as_path not in self.established_paths[prefix]:
                print(f"Fake AS path detected for prefix {prefix}: {as_path}")

        except KeyError:
            # Ignore elements that don't have prefix or AS path fields
            pass

training_files = ["training_data_01 .txt", "training_data_02.txt", "training_data_03.txt", "training_data_04.txt", "training_data_05.txt", "training_data_06.txt"] 

fake = FakePathDetector(
    collectors=["route-views.sg", "route-views.eqix"],
    time_from="2017-04-08 00:00:00",
    time_to="2017-04-15 00:00:00 UTC",
    record_type="updates",
    filter="prefix more 210.0.0.0/16",
    training_files=training_files
)



