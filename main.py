from skyfield.api import *
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
    t=ts.now()
    print("List of trackable satellites ")

    for i in range (0, len(satellites)):
        print(f'{i} -> {satellites[i]}')
    
    choice = int(input("\n Select a satellite by index : "))
    if choice < 0 or choice >= len(satellites):
        print("Invalid satellite index.")
        exit()
    else:
        geocentric=satellites[choice].at(t) #where is it at time t, wrt earth's centre
        subpoint = wgs84.subpoint(geocentric) # subpoint is a line drawn so that we get The point on Earth directly underneath the satellite
        #wgs84 is a mathematical model of the earth, its a standard global reference system
        print(f" Satellite: {satellites[choice].name}")
        print(f" Norad catalog number {satellites[choice].model.satnum}")#the norad catalog number
        velocity=geocentric.velocity.km_per_s
        print(f"    Speed is {(velocity[0]**2 + velocity[1]**2 + velocity[2]**2) ** 0.5} km/s")
        print(f"    Latitude: {subpoint.latitude.degrees:.4f}°")
        print(f"    Longitude: {subpoint.longitude.degrees:.4f}°")
        print(f"    Altitude: {subpoint.elevation.km:.2f} km\n")
 


        
