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
    #from_time= from_time.strftime("%Y-%m-%d %H:%M:%S"), until_time=until_time.strftime("%Y-%m-%d %H:%M:%S"),
    from_time="2017-04-08 00:00:00", until_time="2017-04-09 00:00:00 UTC",
    # Collecting from Route View Singapore Collector and DC Collector
    collectors=["route-views.sg", "route-views.eqix"],
    # Filtering with only BGP updates
    record_type="updates",
    filter="prefix more 210.180.0.0/16"
)
