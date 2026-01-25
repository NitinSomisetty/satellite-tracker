from skyfield.api import load
import logging


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
