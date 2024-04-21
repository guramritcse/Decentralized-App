import random
from user import User
from dapp import DApp
import matplotlib.pyplot as plt

class Simulator:
    def __init__(self, N, p, q, A, T_sim, I, env):
        # Initial parameters
        self.N = N
        self.p = p
        self.q = q
        self.A = A
        self.T_sim = T_sim
        self.I = I
        self.env = env

        self.voter_dict = {}
        self.dapp = DApp(self.env)
        for idx in range(1, self.N+1):
            # Creating a voter object
            is_malicious = self.generate_RV(self.q/100)
            if is_malicious:
                self.voter_dict[idx] = User(self.env, idx, 0, self.dapp) # Type 0 is malicious
            else:
                is_very_trustworthy = self.generate_RV(self.p/100)
                if is_very_trustworthy:
                    self.voter_dict[idx] = User(self.env, idx, 2, self.dapp) # Type 2 is very trustworthy
                else:
                    self.voter_dict[idx] = User(self.env, idx, 1, self.dapp) # Type 1 is trustworthy but not very trustworthy

        print("Simulator constructed")

    # Generating 1 with probability z and 0 otherwise
    def generate_RV(self, z):
        sample = random.random()
        if sample < z:
            return 1
        else:
            return 0

    def my_timer(self):
        while True:
            print("Current time is :", self.env.now)
            yield self.env.timeout(10)
    
    def start_simulation(self):
        # Starting the simulation
        for idx in range(1, self.N+1):
            self.voter_dict[idx].register_checker()
            self.env.process((self.voter_dict[idx]).article_uploader(idx, self.T_sim//self.A))
            self.env.process((self.voter_dict[idx]).vote(0, 1))
            self.env.process((self.voter_dict[idx]).get_result(self.T_sim-10, 50))
        
        self.env.process(self.my_timer())

    # This function would generate info about voters, simulation's parameters and write it to a file
    def generate_info(self, output_dir):
        print(f"Writing simulation's parameters")
        num_contracts = len(self.dapp.get_contracts())
        info = self.dapp.get_info()
        stats = self.dapp.get_trust_worthiness_stats(self.I)
        with open(f"{output_dir}/info.txt", "w") as f:
            f.write(f"Simulation time (in ms): {self.T_sim}\n")
            f.write(f"Number of voters in the network (N): {self.N}\n")
            f.write(f"Percentage of very trust worthy voters (p): {self.p}\n")
            f.write(f"Percentage of trustworthy voters (100-p-q): {100-self.p-self.q}\n")
            f.write(f"Percentage of malicious voters (q): {self.q}\n")
            f.write(f"Number of articles published for voting: {num_contracts}\n")
            f.write("==============================================\n")
            f.flush()
            print(f"Generating voter info")
            f.write("ID,Type,Votes,Correct Votes,Incorrect Votes,Trustworthiness,Actual Correct Votes,Actual Incorrect Votes,Actual Trustworthiness\n")
            for voter in info:
                f.write(f"{voter},{self.voter_dict[voter].voter_type},{info[voter][0]+info[voter][1]},{info[voter][0]},{info[voter][1]},{info[voter][2]:.4f},{info[voter][3]},{info[voter][4]},{info[voter][5]:.4f}\n")
                f.flush()
            f.write("==============================================\n")
            f.write("Statistics\n")
            f.write("==============================================\n")
            total_ticks = len(stats[list(stats.keys())[0]])
            mean_trustworthiness = [[0 for _ in range(total_ticks)] for _ in range(3)]
            mean_correct_votes = [[0 for _ in range(total_ticks)] for _ in range(3)]
            mean_incorrect_votes = [[0 for _ in range(total_ticks)] for _ in range(3)]
            type_count = [0, 0, 0]
            for voter in stats:
                type_count[self.voter_dict[voter].voter_type] += 1
                for tick in range(total_ticks):
                    mean_trustworthiness[self.voter_dict[voter].voter_type][tick] += stats[voter][tick][0]
                    mean_correct_votes[self.voter_dict[voter].voter_type][tick] += stats[voter][tick][1]
                    mean_incorrect_votes[self.voter_dict[voter].voter_type][tick] += stats[voter][tick][2]
            f.write("Type,Number of Voters\n")
            for i in range(3):
                f.write(f"{i},{type_count[i]}\n")
            f.write("==============================================\n")
            f.write("Type,Article's Count,Mean Trustworthiness,Mean Correct Votes,Mean Incorrect Votes\n")
            for i in range(3):
                if type_count[i] != 0:
                    for tick in range(total_ticks):
                        mean_trustworthiness[i][tick] /= type_count[i]
                        mean_correct_votes[i][tick] /= type_count[i]
                        mean_incorrect_votes[i][tick] /= type_count[i]
                        f.write(f"{i},{tick*50},{mean_trustworthiness[i][tick]:.4f},{mean_correct_votes[i][tick]},{mean_incorrect_votes[i][tick]}\n")
                        f.flush()
                else:
                    for tick in range(total_ticks):
                        f.write(f"{i},{tick*50},NA,0,0\n")
            
            f.write("==============================================\n")
            f.write("End of simulation\n")

            print(f"Generating plots")
            x_ticks = [self.I * tick for tick in range(total_ticks)]
            if type_count[0] != 0:
                plt.plot(x_ticks, mean_trustworthiness[0], marker = '*', ls = ':', lw = 1, c = 'r', ms = 7, mec = 'g', mfc = 'hotpink', label = 'malicious')
            if type_count[1] != 0:
                plt.plot(x_ticks, mean_trustworthiness[1], marker = 'o', ls = '--', lw = 1, c = 'b', ms = 5, mec = 'r', mfc = 'skyblue', label = 'trustworthy')
            if type_count[2] != 0:
                plt.plot(x_ticks, mean_trustworthiness[2], marker = 's', ls = '-.', lw = 1, c = 'g', ms = 5, mec = 'b', mfc = 'lightgreen', label = 'very_trustworthy')
            plt.xlabel('Number of Articles considered for calculating Trustworthiness')
            plt.ylabel('Mean Trustworthiness')
            plt.title(f'Trustworthiness of Voters, p = {self.p}, q = {self.q}')
            plt.xticks(x_ticks)
            plt.yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
            plt.legend()
            plt.grid(axis='y', color='gray', ls='--', lw=1)
            plt.savefig(f"{output_dir}/trustworthiness.png")

            