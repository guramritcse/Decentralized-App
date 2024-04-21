import hashlib
import random
import datetime

class SmartContract:
    def __init__(self, category, title, content, author, ground_truth, trust_worthiness):
        self.category = category
        self.title = title
        self.content = content
        self.author = author
        self.ground_truth = ground_truth
        self.trust_worthiness = trust_worthiness
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        article_data = f"{self.author} publishes {self.title} with content as {self.content}" + str(random.randint(1000000000, 9999999999))+ f"{self.timestamp}"
        self.contract_ID = hashlib.sha256(str(self.category).encode()).hexdigest() + hashlib.sha256(article_data.encode()).hexdigest()
        self.voted = {}

    def __str__(self):
        return f"Title: {self.title}\nContent: {self.content}\nAuthor: {self.author}\nTimestamp: {self.timestamp}\nContract ID: {self.contract_ID}\nGround Truth: {self.ground_truth}\n"

    def vote(self, voter, vote):
        # Check if voter has already voted
        if voter not in self.voted:
            self.voted[voter] = vote
            return 0
        else:
            print(f"User {voter} has already voted")
            return -1

    def update_trust_worthiness(self, trust_worthiness):
        self.trust_worthiness = trust_worthiness

    def result(self):
        if len(self.voted) == 0:
            return -1
        else:
            # Calculate the result based on the votes
            positive, negative = 0, 0
            for voter in self.trust_worthiness:
                if voter in self.voted:
                    if self.voted[voter] == 1:
                        positive += self.trust_worthiness[voter]
                    else:
                        negative += self.trust_worthiness[voter]
            return 1 if positive > negative else 0


        