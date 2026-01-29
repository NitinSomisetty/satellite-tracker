from skyfield.api import *


def get_satellite_state(satellite):
    """
    Get current position and velocity of a satellite.
    
    Returns: dict with lat, lon, altitude, velocity, name, norad_id
    """
    ts = load.timescale()
    t = ts.now() #create a time object for NOW, yes like rn
    
    geocentric = satellite.at(t)  # where is it at time t, wrt earth's centre
    subpoint = wgs84.subpoint(geocentric)  # subpoint is a line drawn so that we get The point on Earth directly underneath the satellite
    # wgs84 is a mathematical model of the earth, its a standard global reference system
    
    velocity = geocentric.velocity.km_per_s
    
    return {
        "name": satellite.name,
        "norad_id": satellite.model.satnum,  # the norad catalog number
        "latitude": subpoint.latitude.degrees,
        "longitude": subpoint.longitude.degrees,
        "altitude": subpoint.elevation.km,
        "velocity": (velocity[0]**2 + velocity[1]**2 + velocity[2]**2) ** 0.5 #speed in scalar
    }


def get_observer_view(satellite, observer_lat, observer_lon):
    """
    Get satellite position relative to an observer.(anywhere with cords)
    Returns: dict with altitude, azimuth, distance
    """
    ts = load.timescale()
    t = ts.now()
    
    observer = wgs84.latlon(observer_lat, observer_lon)
    
    # - Observer-based quantities 
    observer_at_t = observer.at(t)
    difference = (satellite.at(t)) - observer_at_t  # we create a vector pointing from observer to satellite
    
    alt, az, distance = difference.altaz()  # az is azimuth, compass direction
    # store seperate vector values in these 3 
    
    return {
        "altitude": alt.degrees,
        "azimuth": az.degrees,
        "distance": distance.km
    }


def generate_ground_track(satellite, minutes_ahead=90, step_seconds=30):
    """
    Generate ground track for satellite over time period.
    Returns: list of (lat, lon) tuples
    """
    ts = load.timescale()
    
    # ---- Ground-track generation (next 90 minutes) ----
    minutes_ahead = minutes_ahead  # usual Low Earth orbit satellites orbit earth in 90 mins
    step_seconds = step_seconds
    
    t0 = ts.now()  # update real time again now with ts a timescale object
    times = ts.utc(  # to handle overflow of seconds and convert to mins:secs
        t0.utc.year, t0.utc.month, t0.utc.day,
        t0.utc.hour, t0.utc.minute,
        range(int(t0.utc.second), int(t0.utc.second) + minutes_ahead * 60, step_seconds)
    )  # [0, 30, 60, 90, 120, ... 5400]
    
    # times is a vecotr of 180 moments now, 90 minutes adn twice every min
    positions = satellite.at(times)
    subpoints = wgs84.subpoint(positions)  # it gives 3 arrays , for lat and lon and alt
    # subpoints is an object of GeographicPosition through 'observer', it stores lats lons and altitude 
    ground_track = []
    for lat, lon in zip(subpoints.latitude.degrees, subpoints.longitude.degrees):
        ground_track.append((lat, lon))  # tuple 
    
    return ground_track
