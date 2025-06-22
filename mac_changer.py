import subprocess
import optparse
import random
import re
import sys
import shutil

def generate_random_mac():
    mac = [0x02, 0x00, 0x00,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ':'.join(map(lambda x: f"{x:02x}", mac))

def change_mac_ip(interface, new_mac):
    subprocess.call(f"ip link set {interface} down", shell=True)
    subprocess.call(f"ip link set {interface} address {new_mac}", shell=True)
    subprocess.call(f"ip link set {interface} up", shell=True)

def get_current_mac(interface):
    try:
        result = subprocess.check_output(f"ip link show {interface}", shell=True).decode()
        mac_search = re.search(r"link/ether ([0-9a-f:]{17})", result)
        if mac_search:
            return mac_search.group(1)
        else:
            return None
    except:
        return None

def is_ip_installed():
    return shutil.which("ip") is not None

parser = optparse.OptionParser()
parser.add_option("-i", dest="network_interface", help="Network interface to change MAC")
parser.add_option("-m", dest="new_mac", help="New MAC address (or use --random)")
parser.add_option("--random", action="store_true", dest="random_mac", help="Generate a random MAC address")

(options, arguments) = parser.parse_args()

if not options.network_interface:
    parser.error("[!] Please specify a network interface, use --help for more info")

# Handle MAC address input
if options.random_mac:
    new_mac = generate_random_mac()
elif options.new_mac:
    new_mac = options.new_mac
else:
    parser.error("[!] Please provide a new MAC address with -m or use --random")

# Check if 'ip' tool exists
if not is_ip_installed():
    print("[!] 'ip' command not found. Please install 'iproute2' package.")
    sys.exit(1)

# Change MAC
print(f"[+] Changing MAC address for {options.network_interface} to {new_mac}")
change_mac_ip(options.network_interface, new_mac)

# Verify result
current_mac = get_current_mac(options.network_interface)

if current_mac == new_mac.lower():
    print("[+] MAC address changed successfully!")
else:
    print("[-] Something went wrong...")
    print(f"[DEBUG] Current MAC: {current_mac}, Expected: {new_mac}")
