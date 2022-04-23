import psutil


addrs = psutil.net_if_addrs()
for name, data in addrs.items():
    for item in data:
        if item.address.startswith("192.168"):
            print('IP-address:', item.address)
            print('Netmask:', item.netmask)
            exit(0)
