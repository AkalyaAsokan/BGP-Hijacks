class MoasDetector:
    """
    MOAS Detector class that keeps track of multiple origin AS (MOAS) events
    """

    def __init__(self):
        # Dictionary to store the prefixes with multiple origin ASes
        self.moas_prefixes = {}

    def process_update(self, prefix, origin_as):
        """
        Process an update for a given prefix and origin AS
        """
        # Check if the prefix is already in the MOAS dictionary
        if prefix in self.moas_prefixes:
            # If the prefix is already in the dictionary, check if the origin AS is new
            if origin_as not in self.moas_prefixes[prefix]:
                # If the origin AS is new, add it to the MOAS dictionary for this prefix
                self.moas_prefixes[prefix].append(origin_as)
                # If there are now two or more origin ASes for this prefix, print a MOAS event
                if len(self.moas_prefixes[prefix]) >= 2:
                    print(f"MOAS detected for prefix {prefix}: {', '.join(self.moas_prefixes[prefix])}")
        else:
            # If the prefix is not yet in the MOAS dictionary, add it with the first origin AS
            self.moas_prefixes[prefix] = [origin_as]
