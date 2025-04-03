import numpy as np
import pandas as pd
def calc_bust(p:float=1/13):
    """
    Calculate the probability of the dealer getting a certain sum given the prbability of drawing any card.

    Args:
        card (int): card number. Between 17 and 21, inclusive
        p (float): odds of drawing a card. default 1/13

    Returns:
        probabilities: an array of probabilities, where each index is the probability of getting the card in question
        when starting at the card corresponding to the index.
    """
    probs = np.zeros(27)
    probs[22:] = 1
    # aces have to be 1
    for i in range(16, 10, -1):
        for j in range(1, 11):
            if j == 10:
                probs[i] += 4*p*probs[i+j] # 4 10s
            else:
                probs[i] += p*probs[i+j]
    # aces have to be 11 from current sums 6-10, and we can't transition from 6-7
    for i in range(10, 5, -1):
        for j in range(2, 12):
            if i+j > 21:
                break
            if j == 10:
                probs[i] += 4*p*probs[i+j]
            else:
                probs[i] += p*probs[i+j]
    
    probs_soft = np.zeros(7)
    # aces can be both 1 and 11
    # calculate soft probabilities
    for i in range(6, 0, -1):
        for j in range(1,11): #TODO: check the upper bound (should it be 6 or 7)
            # going to another soft case (the sum of an ace valued at 11 is less than 17)
            multiplier = 4 if j == 10 else 1
            if i+j <= 6:
                probs_soft[i] += p*probs_soft[i+j]*multiplier
            
            # hard cases

            # dealer stands
            elif i+j+10 <= 21:
                probs_soft[i] += p*probs[i+j+10]*multiplier
            # go to somewhere between 12 and 16, inclusive. hard probabilities
            else:
                probs_soft[i] += p*probs[i+j]*multiplier
    # calculate hard probabilities for 2-6
    for i in range(5,1,-1):
        for j in range(1, 11):
            # use the soft hand probability if we get an ace
            if j == 1:
                probs[i] += p*probs_soft[i+j]
            elif j == 10:
                probs[i] += 4*p*probs[i+j]
            else:
                probs[i] += p*probs[i+j]
    # getting an ace on the first card
    probs[1] = probs_soft[1]

    return probs

def calc_prob(card: int, p:float=1/13):
    """
    Calculate the probability of the dealer getting a certain sum given the prbability of drawing any card.

    Args:
        card (int): card number. Between 17 and 21, inclusive
        p (float): odds of drawing a card. default 1/13

    Returns:
        probabilities: an array of probabilities, where each index is the probability of getting the card in question
        when starting at the card corresponding to the index.
    """
    probs = np.zeros(22)
    probs[card] = 1
    # aces have to be 1
    for i in range(16, 10, -1):
        for j in range(1, 11):
            if i+j > 21:
                break
            if j == 10:
                probs[i] += 4*p*probs[i+j] # 4 10s
            else:
                probs[i] += p*probs[i+j]
    # aces have to be 11 from current sums 6-10, and we can't transition from 6-7
    for i in range(10, 5, -1):
        for j in range(2, 12):
            if i+j > 21:
                break
            if j == 10:
                probs[i] += 4*p*probs[i+j]
            else:
                probs[i] += p*probs[i+j]
    
    probs_soft = np.zeros(7)
    # aces can be both 1 and 11
    # calculate soft probabilities
    for i in range(6, 0, -1):
        for j in range(1,11): #TODO: check the upper bound (should it be 6 or 7)
            # going to another soft case (the sum of an ace valued at 11 is less than 17)
            multiplier = 4 if j == 10 else 1
            if i+j <= 6:
                probs_soft[i] += p*probs_soft[i+j]*multiplier
            
            # hard cases

            # dealer stands
            elif i+j+10 <= 21:
                probs_soft[i] += p*probs[i+j+10]*multiplier
            # go to somewhere between 12 and 16, inclusive. hard probabilities
            else:
                probs_soft[i] += p*probs[i+j]*multiplier
    # calculate hard probabilities for 2-6
    for i in range(5,1,-1):
        for j in range(1, 11):
            # use the soft hand probability if we get an ace
            if j == 1:
                probs[i] += p*probs_soft[i+j]
            elif j == 10:
                probs[i] += 4*p*probs[i+j]
            else:
                probs[i] += p*probs[i+j]
    # getting an ace on the first card
    probs[1] = probs_soft[1]

    return probs

o_17 = calc_prob(17)
o_18 = calc_prob(18)
o_19 = calc_prob(19)
o_20 = calc_prob(20)
o_21 = calc_prob(21)
o_bust = calc_bust()[:22]

o_17_starting = o_17[1:22]
o_18_starting = o_18[1:22]
o_19_starting = o_19[1:22]
o_20_starting = o_20[1:22]
o_21_starting = o_21[1:22]
o_bust_starting = o_bust[1:22]

# Create a pandas dataframe that combines all 6 arrays as columns
df = pd.DataFrame({
    '17': o_17_starting,
    '18': o_18_starting,
    '19': o_19_starting,
    '20': o_20_starting,
    '21': o_21_starting,
    'Bust': o_bust_starting,
    'sum': o_17_starting + o_18_starting + o_19_starting + o_20_starting + o_21_starting + o_bust_starting
})

df.index = range(1, 22)

print(df)

# def calculate_move(dealer_card, player_sum):
#     """
#     Calculate the optimal move given the dealer's card and the player's sum.

#     Args:
#         dealer_card (int): the dealer's card
#         player_sum (int): the player's sum

#     Returns:
#         move: the optimal move
#     """
#     if player_sum < 17:
#         return 'Hit'
#     if player_sum > 21:
#         return 'Bust'
#     if player_sum == 21:
#         return 'Stand'
#     if player_sum == 20:
#         return 'Stand'
#     if player_sum == 19:
#         return 'Stand'
#     if player_sum == 18