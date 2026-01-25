from skyfield.api import *
import time
# from skyfield.api import load
#trying logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s"
)


def fetch_tle(filename='stations.tle', days_valid=7):
    url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle"

    try:
        if not load.exists(filename) or load.days_old(filename) >= days_valid:
            logging.info("Downloading fresh TLE data")
            load.download(url, filename=filename)
        else:
            logging.info("Using cached TLE data")

    except Exception as e:
        logging.error("Failed to download or access TLE file")
        logging.error(str(e))
        exit(1)

    return filename


# print(''.join(lines[0]))  # Show the first satellite (likely ISS)

def parse_tle_file(filename):
    print("Parsing TLE data now")
    satellites = load.tle_file(filename)
    print(f'Loaded {len(satellites)} satellites')
    return satellites



if __name__ == "__main__":
    tle_file = fetch_tle()
    satellites = parse_tle_file(tle_file)
    
        
    ts= load.timescale()
    # t=ts.now()
    print("List of trackable satellites ")

    for i in range (0, len(satellites)):
        print(f'{i} -> {satellites[i]}')
    
    choice = int(input("\n Select a satellite by index : "))
    
    if choice < 0 or choice >= len(satellites):
        print("Invalid satellite index.")
        exit()
    else:
        t=ts.now()
        geocentric=satellites[choice].at(t) #where is it at time t, wrt earth's centre
        subpoint = wgs84.subpoint(geocentric) # subpoint is a line drawn so that we get The point on Earth directly underneath the satellite
        #wgs84 is a mathematical model of the earth, its a standard global reference system
        print(f" Satellite: {satellites[choice].name}")
        print(f" Norad catalog number {satellites[choice].model.satnum}")#the norad catalog number
        
        observer = wgs84.latlon(12.9716, 77.5946)
        velocity=geocentric.velocity.km_per_s

        print(f"    Speed is {(velocity[0]**2 + velocity[1]**2 + velocity[2]**2) ** 0.5} km/s")
        print(f"    Latitude: {subpoint.latitude.degrees:.4f}°")
        print(f"    Longitude: {subpoint.longitude.degrees:.4f}°")
        print(f"    Altitude: {subpoint.elevation.km:.2f} km\n")
                # - Observer-based quantities 
        observer_at_t = observer.at(t)        
        difference = (satellites[choice].at(t)) - observer_at_t # we create a vector pointing from observer to satellite
        
        alt, az, distance = difference.altaz() #az is azimuth, compass direction
        # store seperate vector values in these 3 
        
        print(f"    Observer Altitude: {alt.degrees:.2f}°")
        print(f"    Observer Azimuth : {az.degrees:.2f}°")
        print(f"    Observer Distance: {distance.km:.1f} km\n")


    observer = wgs84.latlon(12.9716, 77.5946) #for bangalore
        # ---- Ground-track generation (next 90 minutes) ----
    sat = satellites[choice]

    minutes_ahead = 90 #usual Low Earth orbit satellites orbit earth in 90 mins
    step_seconds = 30

    t0 = ts.now() # update real time again now with ts a timescale object
    times = ts.utc( # to handle overflow of seconds and convert to mins:secs
        t0.utc.year, t0.utc.month, t0.utc.day,
        t0.utc.hour, t0.utc.minute,
        range(int(t0.utc.second), int(t0.utc.second) + minutes_ahead * 60, step_seconds)
    ) #[0, 30, 60, 90, 120, ... 5400]

    #times is a vecotr of 180 moments now, 90 minutes adn twice every min
    positions = sat.at(times)
    subpoints = wgs84.subpoint(positions) # it gives 3 arrays , for lat and lon and alt
    #subpoints is an object of GeographicPosition through 'observer', it stores lats lons and altitude 
    ground_track = []
    for lat, lon in zip(subpoints.latitude.degrees, subpoints.longitude.degrees): ground_track.append((lat, lon)) #tuple 

    print(f"Generated {len(ground_track)} ground-track points to track")

        # ---- Continuous tracking ----
    print("\n Live tracking (Ctrl+C to stop):")
    #live dashboard since satellites momve at ~7.5km/s
    while True:
        t = ts.now()
        geocentric = sat.at(t) #3d pos relative to earth's centre
        subpoint = wgs84.subpoint(geocentric) #directly below point 
        observer_at_t = observer.at(t)
        #* "Since the Earth is rotating, your house in Bangalore is actually moving through space. This line calculates where you are located in the universe at time t."
        difference = sat.at(t) - observer_at_t
        alt, az, distance = difference.altaz()

        print(
            f"{t.utc_strftime('%H:%M:%S')} | "
            f"{subpoint.latitude.degrees:.2f}, "
            f"{subpoint.longitude.degrees:.2f} | "
            f"{subpoint.elevation.km:.1f} km | "
            f"Alt {alt.degrees:.1f}°"
        )

        time.sleep(1)



        
