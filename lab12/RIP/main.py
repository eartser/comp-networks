import argparse
import json
from rip import Router, run_rip


parser = argparse.ArgumentParser()
parser.add_argument('filename', type=str)
parser.add_argument('--mode', type=str, help='Possible modes: "final", "simulation"', default='final')
args = parser.parse_args()

simulation = args.mode == 'simulation'

with open(args.filename, 'r') as f:
    graph = json.load(f)

routers = [Router(ip, graph[ip]) for ip in graph]
run_rip(routers, simulation)
