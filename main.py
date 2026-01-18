from skyfield import *
import requests 

url = "https://celestrak.org/NORAD/elements/stations.txt"
data = requests.get(url).text.splitlines()

name = data[0]
line1 = data[1]
line2 = data[2]

from skyfield.api import load
ts=load.tmescale()
sat = EarthSatellite(line1, line2, name, ts)

t = ts.now()
