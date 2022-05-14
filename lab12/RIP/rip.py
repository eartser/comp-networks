INF = 15


class Router:
    def __init__(self, ip, neighbours):
        self.ip = ip
        self.neighbours = neighbours
        self.dv = {neighbour: 1 for neighbour in neighbours}
        self.next = {neighbour: neighbour for neighbour in neighbours}

    def __eq__(self, other):
        return self.ip == other.ip

    def __str__(self):
        res = f'{"[Source IP]":20} {"[Destination IP]":25} {"[Next Hop]":20} {"Metric":20}\n'
        for router in self.dv:
            res = res + f'{self.ip:20} {router:25} {self.next[router]:20} {self.dv[router]:6}\n'
        return res

    def update(self, dest, dval, next_hop):
        if dval < self.dv.get(dest, INF):
            self.dv[dest] = dval
            self.next[dest] = next_hop
            return True
        return False


def run_rip(routers, simulation):
    step = 0
    changed = True

    while changed:
        step += 1
        changed = False

        for src_router in routers:
            for dest_router in routers:
                if src_router == dest_router:
                    continue
                for next_router_ip in src_router.neighbours:
                    res = src_router.update(dest_router.ip, dest_router.dv.get(next_router_ip, INF) + 1, next_router_ip)
                    changed = changed or res

            if simulation:
                print(f'Simulation step {step} of router {src_router.ip}:')
                print(src_router)

    for router in routers:
        print(f'Final state of router {router.ip}:')
        print(router)
