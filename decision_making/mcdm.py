import numpy as np

def normalize_vector(vector):
    # Calculate the sum of all elements in the vector
    total = sum(vector)
    
    # Check if the total is not zero to avoid division by zero
    if total != 0:
        # Divide each element in the vector by the total
        normalized_vector = [x / total for x in vector]
        return normalized_vector
    else:
        # Handle the case where the vector has all zeros
        return vector  # Return the original vector if the total is zero

def distance(decision_matrix, weights, benefit_criteria):
    nrows = decision_matrix.shape[0]
    ncols = decision_matrix.shape[1]
    weights = normalize_vector(weights)
    
    # Step 1: Normalize the decision matrix
    normalized_matrix = decision_matrix.copy()
    normalized_weights = weights.copy()
    for i in range(ncols):
        if benefit_criteria[i] == True:
            normalized_matrix[:, i] = decision_matrix[:, i] / np.linalg.norm(decision_matrix[:, i])
        else:
            normalized_matrix[:, i] = np.linalg.norm(decision_matrix[:, i]) / decision_matrix[:, i]



def gdominance(decision_matrix, weights, benefit_criteria):
    nrows = decision_matrix.shape[0]
    ncols = decision_matrix.shape[1]
    weights = normalize_vector(weights)
    
    # Step 1: Normalize the decision matrix
    normalized_matrix = decision_matrix.copy()
    for i in range(ncols):
        if benefit_criteria[i] == True:
            normalized_matrix[:, i] = decision_matrix[:, i] / np.linalg.norm(decision_matrix[:, i])
        else:
            normalized_matrix[:, i] = np.linalg.norm(decision_matrix[:, i]) / decision_matrix[:, i]
    
def topsis(decision_matrix, weights, benefit_criteria):
    nrows = decision_matrix.shape[0]
    ncols = decision_matrix.shape[1]
    
    # Step 1: Normalize the decision matrix
    normalized_matrix = decision_matrix.copy()
    
    for i in range(ncols):
        if benefit_criteria[i] == True:
            normalized_matrix[:, i] = decision_matrix[:, i] / np.linalg.norm(decision_matrix[:, i])
        else:
            normalized_matrix[:, i] = np.linalg.norm(decision_matrix[:, i]) / decision_matrix[:, i]
    
    # Step 2: Calculate the weighted normalized decision matrix
    weighted_normalized_matrix = normalized_matrix * weights
    
    # Step 3: Calculate the ideal and anti-ideal solutions
    ideal_solution = np.max(weighted_normalized_matrix, axis=0)
    anti_ideal_solution = np.min(weighted_normalized_matrix, axis=0)
    
    # Step 4: Calculate the distance to ideal and distance to anti-ideal solutions
    distance_to_ideal = np.linalg.norm(weighted_normalized_matrix - ideal_solution, axis=1)
    distance_to_anti_ideal = np.linalg.norm(weighted_normalized_matrix - anti_ideal_solution, axis=1)
    
    # Step 5: Calculate the TOPSIS score
    topsis_score = distance_to_anti_ideal / (distance_to_ideal + distance_to_anti_ideal)
    
    # Step 6: Rank the alternatives based on the TOPSIS score
    ranking_order = np.argsort(topsis_score)  # Sort in ascending order
    
    # The ranking_order contains the indices of alternatives, sorted from best to worst
    return ranking_order

def vikor(decision_matrix, weights, v):
    weights = normalize_vector(weights)
    nrows = decision_matrix.shape[0]
    ncols = decision_matrix.shape[1]
    
    # Initialize the fi* and fi^ values for each criterion
    fi_star = np.min(decision_matrix, axis=0)
    fi_hat = np.max(decision_matrix, axis=0)
    
    # Initialize arrays to store Sj and Rj values for each alternative
    S_values = np.zeros(nrows)
    R_values = np.zeros(nrows)
    
    # Step 3: Compute Sj and Rj for each alternative
    for j in range(nrows):
        S_j = 0
        R_j = 0
        for i in range(ncols):
            #if benefit_criteria[i]:
            #    S_j += weights[i] * ((fi_star[i] - decision_matrix[j, i]) / (fi_star[i] - fi_hat[i]))
            #    R_j = max(R_j, weights[i] * ((fi_star[i] - decision_matrix[j, i]) / (fi_star[i] - fi_hat[i])))
            #else:
            S_j += weights[i] * ((decision_matrix[j, i] - fi_star[i]) / (fi_hat[i] - fi_star[i]))
            R_j = max(R_j, weights[i] * ((decision_matrix[j, i] - fi_star[i]) / (fi_hat[i] - fi_star[i])))
        S_values[j] = S_j
        R_values[j] = R_j
    
    # Step 4: Compute Qj for each alternative
    #v = (5 + 1) / (2 * 5)  # Modify v as per your requirements
    S_star = np.min(S_values)
    S_hat = np.max(S_values)
    R_star = np.min(R_values)
    R_hat = np.max(R_values)
    Q_values = v * (S_values - S_star) / (S_hat - S_star) + (1 - v) * (R_values - R_star) / (R_hat - R_star)
    
    # Step 5: Rank the alternatives based on Q values
    ranking_order = np.argsort(Q_values)  # Sort in ascending order
    
    # Find the compromise solution(s) based on the conditions C1 and C2
    DQ = 1 / (nrows - 1)  # You can adjust DQ as needed
    best_alternative = ranking_order[0]
    
    if (Q_values[ranking_order[1]] - Q_values[ranking_order[0]]) >= DQ:
        # Condition C1 is satisfied
        compromise_solutions = [ranking_order[0], ranking_order[1]]
    else:
        compromise_solutions = [ranking_order[0]]
    
    if best_alternative not in compromise_solutions:
        # Condition C2 is not satisfied
        compromise_solutions.append(best_alternative)
    
    # The compromise solution(s) are in the compromise_solutions list
    return compromise_solutions


if __name__ == "__main__":

    # Step 1: Define the decision matrix (fij values)
    decision_matrix = np.random.rand(20, 5)  # Random values for 20 alternatives and 5 criteria
    
    # Step 2: Define weights for the criteria
    weights = [0.2, 0.2, 0.2, 0.2, 0.2]  # You can adjust the weights as needed
    
    # Determine if each criterion is benefit or cost
    benefit_criteria = [True, True, True, True, True]  # Assuming all criteria are benefit criteria
    v = 0.7
    compromise_solutions = vikor(decision_matrix, weights, benefit_criteria, v)
    print("Compromise Solution(s):", compromise_solutions)
    ranking_order = topsis(decision_matrix, weights, benefit_criteria)

    print("TOPSIS Ranking Order:", ranking_order)

    '''
    VIKOR
    Certainly! Let's consider an example to illustrate how you might choose an appropriate value for the parameter "v" in the VIKOR method.
    
    Suppose you're involved in a decision-making process related to selecting a supplier for your company's products. You have several criteria to evaluate potential suppliers, including cost, quality, delivery time, and environmental impact. You want to use the VIKOR method to make the decision.
    
    In this scenario, you can set "v" based on the following considerations:
    
    1. Stakeholder Preferences: Start by consulting with the relevant stakeholders, such as procurement managers, quality control experts, and environmental sustainability advocates. Ask them about their preferences in terms of group consensus and individual satisfaction.
    
    2. Importance of Criteria: Assess the relative importance of each criterion. For example, cost and quality might be critical factors where you want to ensure group consensus (higher "v" value). On the other hand, delivery time and environmental impact might be criteria where individual supplier preferences matter more (lower "v" value).
    
    3. Compromise Tolerance: Consider the tolerance for compromise within your organization. If there's a strong desire to reach a unanimous decision among stakeholders, a higher "v" value (closer to 1) would be suitable. If some flexibility for individual preferences is acceptable, a lower "v" value (closer to 0) might be chosen.
    
    4. Past Experience: Reflect on past decision-making experiences in your organization. If previous decisions have leaned heavily toward group consensus or individual satisfaction, use that as a guide.
    
    For example, based on stakeholder input and these considerations, you might decide to set "v" to 0.7. This value indicates a preference for group consensus (70% emphasis on Sj) while allowing some consideration for individual regret (30% emphasis on Rj). 
    
    However, please note that the choice of "v" is context-specific and should be tailored to your organization's unique preferences and the specific nature of the decision-making problem. It's a subjective decision, and the value of "v" can vary from one situation to another based on the dynamics of the decision-making process.'''
