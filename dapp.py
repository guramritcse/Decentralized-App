from contract import SmartContract

class DApp:
    def __init__(self, env):
        self.registered_voters = dict()
        self.contracts = []
        self.trust_worthiness = dict()
        self.env = env

    def update_trust_worthiness(self):
        for voter in self.registered_voters:
            correct_votes = 0
            incorrect_votes = 0
            for contract in self.contracts:
                if voter in contract.voted:
                    if contract.result() == contract.voted[voter]:
                        correct_votes += 1
                    else:
                        incorrect_votes += 1
            self.trust_worthiness[voter] = self.calculate_trust_worthiness(correct_votes, incorrect_votes)

        for contract in self.contracts: 
            contract.update_trust_worthiness(self.trust_worthiness)

        # print(f"Trustworthiness updated at time {self.env.now} and trustworthiness is {self.trust_worthiness}")
    
    def upload_contract(self, category, title, content, author, truth):
        if category < 1 or category > 10:
            print("Invalid category")
            return
        contract = SmartContract(category, title, content, author, truth, self.trust_worthiness)
        self.contracts.append(contract)
        return contract
    
    def get_contracts(self):
        return self.contracts
    
    def register_checker(self, voter):
        # User was/is already registered
        if voter in self.registered_voters:
            if self.registered_voters[voter] == 0:
                self.registered_voters[voter] = 1
            else:
                print(f"User {voter} is already registered")
        # New voter
        else:
            self.registered_voters[voter] = 1

    def deregister_checker(self, voter):
        # User is registered
        if voter in self.registered_voters and self.registered_voters[voter] == 1:
            self.registered_voters[voter] = 0
        # User is alreday deregistered
        else:
            print(f"User {voter} is not registered")

    def vote(self, voter, contract, vote):
        # Check if voter is registered
        if voter not in self.registered_voters:
            print(f"User {voter} is not registered")
            return
        voted_now = contract.vote(voter, vote)
        # Voting was successful i.e. voter has not voted before for this contract
        if voted_now == 0:
            self.update_trust_worthiness()

    def get_result(self, contract):
        return contract.result()
  
    def get_info(self):
        info = dict()
        for voter in self.registered_voters:
            actual_correct_votes = 0
            actual_incorrect_votes = 0
            correct_votes = 0
            incorrect_votes = 0
            for contract in self.contracts:
                if voter in contract.voted:
                    if contract.ground_truth == contract.voted[voter]:
                        actual_correct_votes += 1
                    else:
                        actual_incorrect_votes += 1
                    if contract.result() == contract.voted[voter]:
                        correct_votes += 1
                    else:
                        incorrect_votes += 1
            trust_worthiness = self.calculate_trust_worthiness(correct_votes, incorrect_votes)
            actual_trust_worthiness = self.calculate_trust_worthiness(actual_correct_votes, actual_incorrect_votes)
            info[voter] = [correct_votes, incorrect_votes, trust_worthiness, actual_correct_votes, actual_incorrect_votes, actual_trust_worthiness]
        return info
    
    def get_trust_worthiness_stats(self, interval):
        trust_worthiness_stats = dict()
        for voter in self.trust_worthiness:
            trust_worthiness_stats[voter] = [[1, 0, 0]]
            correct_votes = 0
            incorrect_votes = 0
            for i, contract in enumerate(self.contracts):
                if voter in contract.voted:
                    if contract.result() == contract.voted[voter]:
                        correct_votes += 1
                    else:
                        incorrect_votes += 1
                if (i+1) % interval == 0:
                    trust_worthiness_stats[voter].append([self.calculate_trust_worthiness(correct_votes, incorrect_votes), correct_votes, incorrect_votes])
        return trust_worthiness_stats
    
    def calculate_trust_worthiness(self, correct_votes, incorrect_votes):
        return correct_votes / (correct_votes + incorrect_votes) if correct_votes + incorrect_votes != 0 else 1