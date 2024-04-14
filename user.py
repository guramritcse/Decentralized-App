import random
# from dapp import DApp
import string

class User:
    def __init__(self, env, idx, voter_type, dapp):
        self.env = env
        self.idx = idx
        self.voter_type = voter_type
        self.dapp = dapp
        self.articles_voted = []

    def __str__(self):
        return f"Voter {self.idx} is of type {self.voter_type}"
    
    # Generating 1 with probability z and 0 otherwise
    def generate_RV(self, z):
        sample = random.random()
        if sample < z:
            return 1
        else:
            return 0

    def article_uploader(self):
        while True:
            yield self.env.timeout(120)
            print(f"Voter {self.idx} uploads an article")
            title = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))
            content = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(100))
            ground_truth = self.generate_RV(0.5)
            self.dapp.upload_contract(title, content, self.idx, ground_truth)

    def register_checker(self):
        self.dapp.register_checker(self.idx)
        
    def deregister_checker(self):   
        self.dapp.deregister_checker(self.idx)
            
    def vote(self):
        while True:
            yield self.env.timeout(123)
            all_contracts = self.dapp.get_contracts()
            for chosen_contract in all_contracts:
                if chosen_contract in self.articles_voted:
                    continue  
                if self.voter_type == 0:    # Malicious voter
                    vote = 1 - chosen_contract.ground_truth
                elif self.voter_type == 1:  # Trustworthy voter
                    vote = chosen_contract.ground_truth if self.generate_RV(0.7) else 1 - chosen_contract.ground_truth
                else:                       # Very trustworthy voter
                    vote = chosen_contract.ground_truth if self.generate_RV(0.9) else 1 - chosen_contract.ground_truth
                self.dapp.vote(self.idx, chosen_contract, vote)
                self.articles_voted.append(chosen_contract)
                print(f"Voter {self.idx} votes for the contract {chosen_contract} with vote {vote}")

    def get_result(self):
        while True:
            yield self.env.timeout(995)
            all_contracts = self.dapp.get_contracts()
            if len(all_contracts) == 0:
                continue
            chosen_contract = random.choice(all_contracts)
            print(f"Voter {self.idx} asks for the result of contract {chosen_contract}")
            result = self.dapp.get_result(chosen_contract)
            print(f"Result of the contract {chosen_contract} is {result}")

