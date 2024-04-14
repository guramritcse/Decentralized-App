import argparse
import simpy
import os

from simulator import Simulator

def main():
    # Creating ArgumentParser object
    parser = argparse.ArgumentParser(description='Simulation of a Decentralized App using Blockchain')

    # Adding arguments
    parser.add_argument('--info', action="store_true", help='Generate info')
    parser.add_argument('--N', type=int, default=50, help='Number of peers in the network')
    parser.add_argument('--q', type=int, default=20, help='Fraction of malicious voters')
    parser.add_argument('--p', type=int, default=50, help='Fraction of very trust worthy voters')
    parser.add_argument('--T_sim', type=int, default=400, help='Simulation time (in ms)')
    parser.add_argument('--output_dir', type=str, default="output", help='Output directory')
    # note I is in secs

    # Parse the command-line arguments
    args = parser.parse_args()

    # Sanity checks
    if args.p < 0 or args.p > 100:
        print("Percentage of very trust worthy voters should be between 0 and 100")
        exit(1)
    if args.q < 0 or args.q > 100:
        print("Percentage of malicious voters should be between 0 and 100")
        exit(1)
    if args.p + args.q > 100:
        print("Sum of the percentage of very trust worthy voters and malicious voters should be at most 100")
        exit(1)
    if args.N < 1:
        print("Number of users in the network should be at least 1")
        exit(1)

    # env = simpy.Environment(factor=0.001)
    env = simpy.Environment()

    # Simulating the network
    sim = Simulator(args.N, args.q, args.p, args.T_sim, env)
    
    # Setting simulation entities
    sim.start_simulation()

    # Starting simulation
    env.run(until=args.T_sim)

    print("Simulation finished")

    # Make output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # Generating voters' info and simulation's parameters
    if args.info:
        sim.generate_info(args.output_dir)

if __name__ == "__main__":
    main()
