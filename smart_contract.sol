// SPDX-License-Identifier: GPL-3.0
pragma solidity ^ 0.8.0;

contract DApp {
    // Total number of fact-checkers
    uint factCheckersCount;

    // Array to store the mean trustworthiness score for each category
    uint[10] meanTrustworthinessScore;

    // Minimum deposit required to register as a fact-checker
    uint constant minimumDeposit = 0.001 ether;

    // Minimum deposit required to view voting results for an article
    uint constant minimumViewDeposit = 0.00001 ether;

    // Mapping to store indexed fact-checkers
    mapping(uint => address) private indexedFactCheckers;

    // Mapping to store registered fact-checkers
    mapping(address => FactChecker) private factCheckers;

    // Mapping of category to articles
    mapping(uint => bytes32[]) private articles;
    
    // Mapping to store article votes
    mapping(bytes32 => UserVote[]) private articleVotes;

    // Mapping to store articleID to Description
    mapping(bytes32 => string) private articleDescription;

    // Mapping to store articleID to truth value
    mapping(bytes32 => bool) private articleTruthValue;

    // Structure to represent a vote
    struct UserVote {
        address user;
        bool vote;
    }

    // Structure to represent a registered fact-checker
    struct FactChecker {
        address publicKey; // Public key of the fact-checker
        uint deposit; // Amount of ETH deposited by the fact-checker
        bool previousRegister; // Previous registration status of the fact-checker
        bool registrationStatus; // Registration status of the fact-checker
        mapping(bytes32 => bool) voted; // Mapping to track articles voted on by the fact-checker
        mapping(bytes32 => bool) positiveVote; // Mapping to track positive votes by the fact-checker
        mapping(uint => uint) votes; // Mapping to store votes by the fact-checker for each category
        mapping(uint => uint) trustworthiness; // Mapping to store trustworthiness score in percentage for each category
        mapping(uint => bool) allowed; // Mapping to store allowed categories for the fact-checker
        mapping(uint => uint) stake; // Mapping to store stake for each category
    }

    constructor() {
        // Initialize the contract with the mean trustworthiness score for each category
        for (uint i = 0; i < 10; i++) {
            meanTrustworthinessScore[i] = 100;
        }
        // Initialize the total number of fact-checkers to 0
        factCheckersCount = 0;
    }
    
    // Function to register as a fact-checker
    function register() external payable {
        // Ensure sender is not already registered
        require(!factCheckers[msg.sender].registrationStatus, "Already registered");
        // Ensure sender has deposited the minimum required amount
        require(msg.value >= minimumDeposit, "Insufficient deposit amount");

        // Create a new FactChecker instance if the sender was not previously registered
        if (!factCheckers[msg.sender].previousRegister) {
            factCheckers[msg.sender].publicKey = msg.sender;
            factCheckers[msg.sender].deposit = msg.value;
            factCheckers[msg.sender].previousRegister = true;
            factCheckers[msg.sender].registrationStatus = true;
            // Set allowed categories for the fact-checker to all categories (0-9)
            // and initialize the stake and trustworthiness score for each category
            for (uint i = 0; i < 10; i++) {
                factCheckers[msg.sender].allowed[i] = true;
                factCheckers[msg.sender].stake[i] = 0;
                factCheckers[msg.sender].trustworthiness[i] = meanTrustworthinessScore[i];
            }
        }
        else{
            // Update the deposit amount for the sender
            factCheckers[msg.sender].deposit = msg.value;
            // Update the registration status for the sender
            factCheckers[msg.sender].registrationStatus = true;
        }
        indexedFactCheckers[factCheckersCount] = msg.sender;
        factCheckersCount++;
    }

    // Function to request de-registration
    function deRegister() external {
        // Ensure sender is registered
        require(factCheckers[msg.sender].registrationStatus, "Not registered");

        // Refund deposit to the sender
        payable(msg.sender).transfer(factCheckers[msg.sender].deposit);
        
        // Reset fact-checker details
        factCheckers[msg.sender].deposit = 0;
        factCheckers[msg.sender].registrationStatus = false;
        for(uint i = 0; i < factCheckersCount; i++){
            if(indexedFactCheckers[i] == msg.sender){
                for(uint j = i; j < factCheckersCount - 1; j++){
                    indexedFactCheckers[j] = indexedFactCheckers[j + 1];
                }
                break;
            }
        }
        factCheckersCount--;
    }
    
    // Function to vote on an article
    function vote(bytes32 articleID, uint category, bool voteValue) external {
        // Ensure sender is registered for the category
        require(factCheckers[msg.sender].registrationStatus, "Not registered as fact-checker");
        // Ensure sender is allowed to vote on the category
        require(factCheckers[msg.sender].allowed[category], "Not allowed to vote on category");
        // Ensure article has not been voted on before
        require(!factCheckers[msg.sender].voted[articleID], "Article already voted on");
        
        // Check if articleID belongs to the category
        bool articleExists = false;
        for (uint i = 0; i < articles[category].length; i++) {
            if (articles[category][i] == articleID) {
                articleExists = true;
                break;
            }
        }
        require(articleExists, "Article does not belong to the category");

        // Update the vote count for the fact-checker
        factCheckers[msg.sender].votes[category]++;
        // Update the stake for the category
        uint totalVotes = 0;
        for (uint i = 0; i < 10; i++) {
            totalVotes += factCheckers[msg.sender].votes[i];
        }
        for (uint i = 0; i < 10; i++) {
            factCheckers[msg.sender].stake[i] = factCheckers[msg.sender].votes[i] * factCheckers[msg.sender].deposit / totalVotes;
        }
        // Update articleVotes mapping with the user's vote
        articleVotes[articleID].push(UserVote(msg.sender, voteValue));
        // Mark article as voted on
        factCheckers[msg.sender].voted[articleID] = true;
        // Update the positiveVote mapping for the fact-checker
        factCheckers[msg.sender].positiveVote[articleID] = voteValue;
        // Update result of the vote
        updateTruthValue(articleID, category);
        // Update trustworthiness score for each category
        for (uint i = 0; i < 10; i++) {
            updateTrustworthiness(i);
        }
    }
    
    // Function to submit an article for fact-checking
    function submitArticle(bytes32 articleID, uint category, string memory description) external {
        // Ensure articleID is concatenation of hash of category and hash of description
        require(keccak256(abi.encodePacked(category, description)) == articleID, "Invalid article ID");
        
        // Ensure that the article has not been submitted before
        bool articleExists = false;
        for (uint i = 0; i < articles[category].length; i++) {
            if (articles[category][i] == articleID) {
                articleExists = true;
                break;
            }
        }
        require(!articleExists, "Article already submitted");
        // Add the article to the specified category
        articles[category].push(articleID);
        // Store the description of the article
        articleDescription[articleID] = description;
        // Initialize the truth value of the article to 1
        articleTruthValue[articleID] = true;
    }

    // Function to get available articles for fact-checking and their descriptions
    function getArticles(uint category) external view returns (bytes32[] memory, string[] memory) {
        // Get the list of articles in the specified category
        bytes32[] memory articleList = articles[category];
        // Get the description of each article
        string[] memory descriptionList = new string[](articleList.length);
        for (uint i = 0; i < articleList.length; i++) {
            descriptionList[i] = articleDescription[articleList[i]];
        }
        return (articleList, descriptionList);
    }

    // Function to update truth value of an article
    function updateTruthValue(bytes32 articleID, uint category) internal {
        // Count votes only if fact-checker is still registered
        uint totalVotes = 0;
        uint positiveVotes = 0;
        for (uint i = 0; i < articleVotes[articleID].length; i++) {
            if (factCheckers[articleVotes[articleID][i].user].registrationStatus && factCheckers[articleVotes[articleID][i].user].voted[articleID]) {
                totalVotes += factCheckers[articleVotes[articleID][i].user].stake[category] * factCheckers[articleVotes[articleID][i].user].trustworthiness[category];
                if(factCheckers[articleVotes[articleID][i].user].positiveVote[articleID]){
                    positiveVotes+= factCheckers[articleVotes[articleID][i].user].stake[category] * factCheckers[articleVotes[articleID][i].user].trustworthiness[category];
                }
            }
        }
        
        // Update the truth value of the article based on the majority vote
        if (positiveVotes >= totalVotes / 2) {
            articleTruthValue[articleID] = true;
        } else {
            articleTruthValue[articleID] = false;
        }
    }

    // Function to confiscate stake from dishonest voters
    function confiscateStake(address pkey, uint category) internal {
        // User is not allowed to vote in this category anymore
        factCheckers[pkey].allowed[category] = false;
        // Confiscate the stake of the user in this category and distribute among other users
        uint confiscatedStake = factCheckers[pkey].stake[category];
        factCheckers[pkey].stake[category] = 0;
        factCheckers[pkey].deposit -= confiscatedStake;
        factCheckers[pkey].votes[category] = 0;
        // Update voted and positiveVote mappings for the user
        for (uint i = 0; i < articles[category].length; i++) {
            if (factCheckers[pkey].voted[articles[category][i]]) {
                factCheckers[pkey].voted[articles[category][i]] = false;
                factCheckers[pkey].positiveVote[articles[category][i]] = false;
            }
        }
        // Remove the votes of the user in this category
        for (uint i = 0; i < articles[category].length; i++) {
            if (factCheckers[pkey].voted[articles[category][i]]) {
                for (uint j = 0; j < articleVotes[articles[category][i]].length; j++) {
                    if (articleVotes[articles[category][i]][j].user == pkey) {
                        for (uint k = j; k < articleVotes[articles[category][i]].length - 1; k++) {
                            articleVotes[articles[category][i]][k] = articleVotes[articles[category][i]][k + 1];
                        }
                        articleVotes[articles[category][i]].pop();
                        break;
                    }
                }
            }
        }
        // Get the total stake * trustworthiness score for this category
        uint totalStake = 0;
        for (uint l = 0; l < factCheckersCount; l++) {
            address i = indexedFactCheckers[l];
            if (factCheckers[i].votes[category] >= 10 && factCheckers[i].registrationStatus) {
                totalStake += factCheckers[i].stake[category] * factCheckers[i].trustworthiness[category];
            }
        }
        // Distribute the amount among the users
        for (uint l = 0; l < factCheckersCount; l++) {
            address i = indexedFactCheckers[l];
            if (factCheckers[i].votes[category] >= 10 && factCheckers[i].registrationStatus) {
                // Increase the deposit amount of the user and update the stake
                factCheckers[i].deposit += (factCheckers[i].stake[category] * factCheckers[i].trustworthiness[category] / totalStake) * confiscatedStake;
                uint totalVotes = 0;
                for(uint k = 0; k < 10; k++){
                    totalVotes += factCheckers[i].votes[k];
                }
                for(uint j = 0; j < 10; j++){
                    factCheckers[i].stake[j] = factCheckers[i].votes[j] * factCheckers[i].deposit / totalVotes;
                }
            }
        }
        // Update truth value for all articles in this category
        for (uint i = 0; i < articles[category].length; i++) {
            updateTruthValue(articles[category][i], category);
        }
        // Update trustworthiness score 
        for (uint i = 0; i < 10; i++) {
            updateTrustworthiness(i);
        }
    }

    // Function to check if stake should be confiscated
    function checkifConfiscate(uint category) internal {
        // Check if the trustworthiness score of any fact-checker is below 0.2 in this category
        for (uint l = 0; l < factCheckersCount; l++) {
            address i = indexedFactCheckers[l];
            if (factCheckers[i].votes[category] >= 10 && factCheckers[i].trustworthiness[category] < 20 && factCheckers[i].registrationStatus) {
                confiscateStake(factCheckers[i].publicKey, category);
            }
        }
    }

    // Function to update trustworthiness score
    function updateTrustworthiness(uint category) internal {
        // Calculate the mean trustworthiness score for this category
        uint totalTrustworthiness = 0;
        uint participants = 0;
        for (uint l = 0; l < factCheckersCount; l++) {
            address j = indexedFactCheckers[l];
            if(factCheckers[j].votes[category] == 0){
                continue;
            }
            participants++;
            uint correctVotes = 0;
            uint totalVotes = 0;
            for (uint k = 0; k < articles[category].length; k++) {
                if (factCheckers[j].voted[articles[category][k]]) {
                    totalVotes++;
                    if(factCheckers[j].positiveVote[articles[category][k]] == articleTruthValue[articles[category][k]]){
                        correctVotes++;
                    }
                }
            }        
            factCheckers[j].trustworthiness[category] = 100 * correctVotes / totalVotes;
            totalTrustworthiness += factCheckers[j].trustworthiness[category];       
        }
        meanTrustworthinessScore[category] = totalTrustworthiness / participants;
        checkifConfiscate(category);
    }

    // Function to distribute funds based on the majority vote
    function distributeFunds(bytes32 articleID, uint category, uint amount) internal {
        // Get the total stake * trustworthiness score for this article 
        // and distribute among users who voted for the majority vote 
        // and have trustworthiness score > 0.4 in this category
        // and have voted for at least 10 articles in this category
        uint totalStake = 0;
        for (uint l = 0; l < factCheckersCount; l++) {
            address i = indexedFactCheckers[l];
            if (factCheckers[i].votes[category] >= 10 && factCheckers[i].trustworthiness[category] > 40 && factCheckers[i].registrationStatus && factCheckers[i].voted[articleID]) {
                // Check if the user voted for the majority vote
                if (factCheckers[i].positiveVote[articleID] == articleTruthValue[articleID]) {
                    totalStake += factCheckers[i].stake[category] * factCheckers[i].trustworthiness[category];
                }
            }
        }
        // Distribute the amount among the users who voted for the majority vote
        for (uint l = 0; l < factCheckersCount; l++) {
            address i = indexedFactCheckers[l];
            if (factCheckers[i].votes[category] >= 10 && factCheckers[i].trustworthiness[category] > 40 && factCheckers[i].registrationStatus && factCheckers[i].voted[articleID]) {
                // Check if the user voted for the majority vote
                if (factCheckers[i].positiveVote[articleID] == articleTruthValue[articleID]) {
                    // Increase the deposit amount of the user and update the stake
                    factCheckers[i].deposit += (factCheckers[i].stake[category] * factCheckers[i].trustworthiness[category] / totalStake) * amount;
                    uint totalVotes = 0;
                    for(uint k = 0; k < 10; k++){
                        totalVotes += factCheckers[i].votes[k];
                    }
                    for(uint k = 0; k < 10; k++){
                        factCheckers[i].stake[k] = factCheckers[i].votes[k] / totalVotes * factCheckers[i].deposit;
                    }
                }
            }
        }
        // Update truth value for all articles in this category
        for (uint i = 0; i < articles[category].length; i++) {
            updateTruthValue(articles[category][i], category);
        }
        // Update trustworthiness score
        for (uint i = 0; i < 10; i++) {
            updateTrustworthiness(i);
        }
    }

    // Function to view voting results for a specific article
    function viewVotingResults(bytes32 articleID, uint category) external payable returns (bool) {
        // Ensure the sender has provided the minimum required ETH amount
        require(msg.value >= minimumViewDeposit, "Insufficient ETH provided to view voting results");

        // Call the distributeFunds function to distribute the received ETH
        distributeFunds(articleID, category, msg.value);

        // Return 1 if the article is true, 0 if the article is false
        return articleTruthValue[articleID]; 
    }   
}
