import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import re
print(os.getcwd())

# df = pd.read_csv('C:/Users/lasmimarbun/Documents/Git/Prolific-Full-Experiment/data/Clean_files/mock_long_format.csv') # change file name as needed
df = pd.read_csv('C:/Users/Lasmi Marbun/Documents/Git/Prolific-Full-Experiment/data/Clean_files/mock_long_format.csv') # change file name as needed
df.head()
df.shape

df.columns


# Create round 0 answer by taking the old_response from the round_no 1
round0_rows = (
    df[df['round_no'] == 1]
    .copy()
    .assign(round_no=0, old_response=lambda x: x['old_response'])
)
# only keep the necessary columns
#round0_rows = round0_rows[['participant.code', 'round_no', 'old_response']]


# Concatenate the new round 0 rows with the original DataFrame
df_with_round0 = pd.concat([df, round0_rows], ignore_index=True)

# Sort if needed
df_with_round0 = df_with_round0.sort_values(['participant.code', 'round_no']).reset_index(drop=True)

# Rename old_response to response and remove old_response and new_response columns
df_with_round0 = df_with_round0.rename(columns={'old_response': 'response'})
df_with_round0 = df_with_round0.drop(columns=['new_response'])
df_with_round0.head()

# Compute polarization index per round and store c values
mu_round = []
c_neg = []
c_pos = []
c_neu = []
# Iterate through each round and calculate the polarization index
for round_no in df_with_round0['round_no'].unique().tolist():
    round_data = df_with_round0[df_with_round0['round_no'] == round_no]
    response = round_data['response']
    # Calculate polarization index
    c_negative = (response == -1).sum() / len(response)
    c_positive = (response == 1).sum() / len(response)
    c_neutral = (response == 0).sum() / len(response)
    #mu = (1 - abs(c_negative - c_positive)) / 2
    mu = (1 - abs(c_negative - c_positive)) / 2  * (c_positive / (c_neutral + c_positive)   + c_negative/ (c_neutral + c_negative))
    mu_round.append(mu)
    c_neg.append(c_negative)
    c_pos.append(c_positive)
    c_neu.append(c_neutral)

c_pos 
c_neg 
c_neu
mu_round

# check color keys
import matplotlib.colors as mcolors
print(mcolors.CSS4_COLORS.keys())


# Get the sorted list of round numbers
round_numbers = sorted(df_with_round0['round_no'].unique().tolist())

plt.figure(figsize=(12, 6))
plt.plot(round_numbers, mu_round, marker='o', linestyle='--',label='mu (Polarization Index)', color='purple')
plt.plot(round_numbers, c_neg, marker='x',linestyle='--', label='c_negative', color='red')
plt.plot(round_numbers, c_pos, marker='^',linestyle='--', label='c_positive', color='blue')
plt.plot(round_numbers, c_neu, marker='s',linestyle='--', label='c_neutral', color='green')
plt.xlabel('Round Number')
plt.ylabel('Value')
plt.ylim(0,1.1)
plt.axhline(y=0.5, color='gray', linestyle='-', linewidth=1, label='mu=0.5 consensus')
plt.title('Polarization Index (mu) values per Round')
plt.xticks(round_numbers)
plt.legend()
plt.grid(False)
plt.tight_layout()
plt.show()


# Get the fifth element of each c list
values = [c_neg[4], c_pos[4], c_neu[4]]
labels = ['c_negative', 'c_positive', 'c_neutral']

plt.figure(figsize=(6, 4))
plt.bar(labels, values, color=['tomato', 'mediumseagreen', 'cornflowerblue'])
plt.ylabel('Proportion')
plt.title('Proportion of Responses (Round 5)')
plt.ylim(0, 1)
plt.show()
