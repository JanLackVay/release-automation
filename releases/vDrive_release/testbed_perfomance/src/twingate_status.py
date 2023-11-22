import psutil


def is_twingate_running():
    for process in psutil.process_iter(['pid', 'name']):
        if 'twingate' in process.info['name'].lower():
            return True
    return False

if is_twingate_running():
    print("Twingate is running.")
else:
    print("Twingate is not running.")