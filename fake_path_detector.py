import os
import pybgpstream
from collections import defaultdict
import networkx as nx

class FakePathDetector:
    def __init__(self):
        self.graphs = defaultdict(nx.Graph)
        self.origin_as = defaultdict(int)

    def train(self, training_files):
        for file in training_files:
            with open(file, "r") as f:
                for line in f:
                    if '|' not in line:
                        continue
                    
                    prefix, path = line.strip().split("|")
                    path = tuple(map(int, path.split()))
                    origin = path[-1]

                    #update graph
                    self.graphs[prefix].add_edges_from(zip(path[:-1], path[1:]))

                    # update origin AS
                    self.origin_as[prefix] = origin

    def is_fake_path(self, path, prefix):
        graph = self.graphs[prefix]

        # check whether path is already connected in the graph
        for i in range(len(path) - 1):
            if not graph.has_edge(path[i], path[i + 1]):
                break
        else:
            return False

        # check if origin AS is the same
        return path[-1] == self.origin_as[prefix]

    def collect_bgp_data(self):
        # specify 
        stream = pybgpstream.BGPStream(
            from_time="2017-07-07 00:00:00",
            until_time="2017-07-08 00:00:00 UTC",
            collectors=["route-views.sg", "route-views.eqix"],
            filter="prefix more 210.0.0.0/08",
            record_type="updates",
        )

        # processing updates
        for elem in stream:
            # filter by announcement
            if elem.type == "A":
                # get prefix + path
                prefix = elem.fields["prefix"]
                path = tuple(map(int, elem.fields["as-path"].split()))

                # check if path is fake
                if self.is_fake_path(path, prefix):
                    print(f"Fake path detected for prefix {prefix}: {path}")


if __name__ == "__main__":
    training_files = [
        'training_data_12.txt', 'training_data_11.txt', 'training_data_10.txt'
    ]

    detector = FakePathDetector()
    detector.train(training_files)
    detector.collect_bgp_data()
