"""
Created on Thu May 15 09:38:41 2025

@author: juncosa
"""

import os
import re
import pandas as pd
import ast
import numpy as np
import math


print(os.getcwd())

os.chdir('/Users/lasmimarbun/Documents/Git/Prolific-Full-Experiment/')
data_clean = 'data/Clean_files/'

df_raw = pd.read_csv('data/Raw_otree/all_apps_wide_b0qkdyda.csv') # change file name to current file

variables = df_raw.columns.to_list()

participant_vars = [var for var in variables if re.match(r'^participant\.', var)]
presurvey_vars = [var for var in variables if re.match(r'^presurvey\.', var)]
mock_vars = [var for var in variables if re.match(r'^mock\.', var)]
pay_vars = [var for var in variables if re.match(r'^Pay\.', var)]
noPay_vars = [var for var in variables if re.match(r'^noPay\.', var)]
player_vars = presurvey_vars + mock_vars + pay_vars + noPay_vars
other_vars = [var for var in variables if var not in participant_vars+presurvey_vars+mock_vars] 

print("No. ALL variables:", len(variables))
print("No. participant variables:", len(participant_vars))
print("No. player variables in presurvey:", len(presurvey_vars)) 
print("No. player variables in mock:", len(mock_vars))
print("No. player variables in pay:", len(pay_vars))
print("No. player variables in noPay:", len(noPay_vars))
print("No. player variables:", len(player_vars)) 
print("No. other variables:", len(other_vars)) 


participant_vars_keep = [
 'participant.code',
 'participant.label',
 'participant.time_started_utc',
 'participant.gives_consent',
 'participant.no_consent',
 'participant.training_attempt',
 'participant.training_success',
 'participant.no_consent',
 'participant.failed_commitment',
 'participant.treatment',
 'participant.scenario_order',
 'participant.all_responses',
 'participant.wait_page_arrival',
 'participant.failed_attention_check',
 'participant.active',
 'participant.single_group',
 'participant.reason',
 'participant.is_group_single',
 'participant.scenario',
 'participant.anticonformist',
 'participant.position']

# keep variables in session vars
other_vars_keep = ['session.code',
                 'session.combined_responses',]

player_vars_all = [
    'presurvey.{i}.player.id_in_group',
    'presurvey.{i}.player.role',
    'presurvey.{i}.player.payoff',
    'presurvey.{i}.player.gives_consent',
    'presurvey.{i}.player.scenario_code',
    'presurvey.{i}.player.dropout',
    'presurvey.{i}.player.test_scenario',
    'presurvey.{i}.player.dilemmatopic',
    'presurvey.{i}.player.majority',
    'presurvey.{i}.player.howmanyneighbors',
    'presurvey.{i}.player.total_correct',
    'presurvey.{i}.player.training_counter',
    'presurvey.{i}.player.attention_check',
    'presurvey.{i}.player.age',
    'presurvey.{i}.player.gender',
    'presurvey.{i}.player.education_lvl',
    'presurvey.{i}.player.neighborhood_type',
    'presurvey.{i}.player.response',
    'presurvey.{i}.player.attitude_certainty',
    'presurvey.{i}.player.likelihood',
    'presurvey.{i}.player.political_charge',
    'presurvey.{i}.player.emotional_charge',
    'presurvey.{i}.player.disagree_conform',
    'presurvey.{i}.player.commit_attention_Q1',
    'presurvey.{i}.player.commit_attention_Q2',
    'presurvey.{i}.player.commit_attention_Q3',
    'presurvey.{i}.group.id_in_subsession',
    'presurvey.{i}.subsession.round_number',
    'mock.{i}.player.id_in_group',
    'mock.{i}.player.role',
    'mock.{i}.player.payoff',
    'mock.{i}.player.scenario',
    'mock.{i}.player.discussion_grp',
    'mock.{i}.player.old_response',
    'mock.{i}.player.new_response',
    'mock.{i}.player.forced_response',
    'mock.{i}.group.id_in_subsession',
    'mock.{i}.group.group_size',
    'mock.{i}.group.is_group_single',
    'mock.{i}.subsession.round_number',
    'noPay.{i}.player.id_in_group',
    'noPay.{i}.player.id_in_group',
    'Pay.{i}.player.feedback_final',
    'Pay.{i}.player.id_in_group',]

# variables that have multiple rounds
player_vars_allR = [
    'presurvey.{i}.player.response',
   # 'presurvey.{i}.player.attitude_certainty',
   # 'presurvey.{i}.player.likelihood',
    'presurvey.{i}.player.political_charge',
    'presurvey.{i}.player.emotional_charge',
    'presurvey.{i}.player.scenario_code',
    'mock.{i}.player.scenario',
    'mock.{i}.player.discussion_grp',
    'mock.{i}.player.old_response',
    'mock.{i}.player.new_response',
    'mock.{i}.player.forced_response'
]
# variables that have multiple rounds in presurvey app
player_vars_presurvey_allR = [
    'presurvey.{i}.player.response',
    'presurvey.{i}.player.political_charge',
    'presurvey.{i}.player.emotional_charge',
    'presurvey.{i}.player.scenario_code',
]
# variables that have multiple rounds in mock app
player_vars_mock_allR = [
    'mock.{i}.player.scenario',
    'mock.{i}.player.discussion_grp',
    'mock.{i}.player.old_response',
    'mock.{i}.player.new_response',
    'mock.{i}.player.forced_response'
]

# variables that only appear in round 1
player_vars_allR1 = [
    'presurvey.{i}.player.id_in_group',
    'presurvey.{i}.player.role',
    'presurvey.{i}.player.payoff',
    'presurvey.{i}.player.gives_consent',
    'presurvey.{i}.player.test_scenario',
    'presurvey.{i}.player.dilemmatopic',
    'presurvey.{i}.player.majority',
    'presurvey.{i}.player.howmanyneighbors',
    'presurvey.{i}.player.total_correct',
    'presurvey.{i}.player.training_counter',
    'presurvey.{i}.player.attention_check',
    'presurvey.{i}.player.age',
    'presurvey.{i}.player.gender',
    'presurvey.{i}.player.education_lvl',
    'presurvey.{i}.player.neighborhood_type',
    'mock.{i}.player.id_in_group',
    'mock.{i}.player.role',
    'mock.{i}.player.payoff',
    'mock.{i}.group.is_group_single',
    'noPay.{i}.player.id_in_group',
    'noPay.{i}.player.id_in_group',
    'Pay.{i}.player.feedback_final',
    'Pay.{i}.player.id_in_group',
    ]

# Mock app has 5 rounds whilst presurvey app have 4 rounds
# Define variables that only appear in round 5 (mock)
player_vars_R5 = [
    'mock.{i}.player.scenario',
    'mock.{i}.player.discussion_grp',
    'mock.{i}.player.old_response',
    'mock.{i}.player.new_response',
    'mock.{i}.player.forced_response'
]


player_vars_keep = []
for r in range(1,6):
    if r == 1:
        all_vars = player_vars_allR1 + player_vars_allR
    elif r == 5:
        all_vars = player_vars_R5
    else:
        all_vars = player_vars_allR 
    
    for var in all_vars:
        player_vars_keep.append(var.format(i=r))
        
all_vars_keep = participant_vars_keep + other_vars_keep + player_vars_keep  
# df_clean = df_raw[all_vars_keep]
df_clean = df_raw[[col for col in all_vars_keep if col in df_raw.columns]]
df_clean = df_clean[df_clean['participant.label'].notna()].reset_index(drop=True)
print('Shape clean data:', df_clean.shape)

df_clean['participant.scenario_order'] = df_clean['participant.scenario_order'].apply(ast.literal_eval)


def player_info(df,k): 
    varas = ['session.code','participant.code',
             'participant.scenario',
             'participant.anticonformist',
             'participant.label',
            'presurvey.1.player.gives_consent',
            'presurvey.1.player.age',
            'presurvey.1.player.gender',
            'presurvey.1.player.education_lvl',
            'presurvey.1.player.neighborhood_type']
    
    varas_lists = [df.loc[k,vara] for vara in varas]
    
    return varas_lists



# For the mock app (discussion over 5 rounds), we need to keep the variables for all rounds
# and then create a dictionary with the player information for each round.
# The player information will include the participant code, scenario order, and responses for each round.
# Define the player_info variables (as in your player_info function)
player_info_vars = ['session.code','participant.code',
             'participant.scenario',
             'participant.anticonformist',
             'participant.label',
            'presurvey.1.player.gives_consent',
            'presurvey.1.player.age',
            'presurvey.1.player.gender',
            'presurvey.1.player.education_lvl',
            'presurvey.1.player.neighborhood_type']

player_vars_mock_allR = [
    'mock.{i}.player.scenario',
    'mock.{i}.player.discussion_grp',
    'mock.{i}.player.old_response',
    'mock.{i}.player.new_response',
    'mock.{i}.player.forced_response'
]
# variables that have multiple rounds in presurvey app
player_vars_presurvey_allR = [
    'presurvey.{i}.player.response',
    'presurvey.{i}.player.political_charge',
    'presurvey.{i}.player.emotional_charge',
    'presurvey.{i}.player.scenario_code',
]


### PRESURVEY APP participants 
# Identify participants with incomplete presurvey answers
invalid_presurvey = df_clean[df_clean['presurvey.4.player.response'].isnull()]
len(pd.Series(invalid_presurvey['participant.code']).unique()) # 5 people
# Print the participants with incomplete presurvey answers
print("Participants with incomplete presurvey answers:")
print(invalid_presurvey[['participant.label']])

# Remove participants with incomplete presurvey answers
df_clean_presurvey = df_clean[~df_clean['participant.label'].isin(invalid_presurvey['participant.label'])].reset_index(drop=True)

# Verify the remaining participants
print(f"Remaining participants: {len(df_clean_presurvey['participant.label'].unique())}")
print(f"Shape of df_clean after removal: {df_clean_presurvey.shape}") # 31 participants

def extract_code(s):
    if pd.isna(s):
        return None
    match = re.search(r"'code': '([^']+)'", s)
    return match.group(1) if match else None

for i in range(1, 5):  # Presurvey has 4 rounds
    df_clean_presurvey['participant.scenario_order'] = df_clean_presurvey['presurvey.{i}.player.scenario'].apply(extract_code)

### Prepare the long-format data for the 'presurvey app' participants
long_data_presurvey = []
# Iterate through each row in the cleaned DataFrame and create a dictionary for each round of the presurvey app with the player information and responses.
for idx, row in df_clean_presurvey.iterrows():
    scenario_order = row['participant.scenario_order']
    for r in range(1, 5):  # Presurvey has 4 rounds
        round_data = {var: row[var] for var in player_info_vars} #player_info_vars is the participant unique identifier
        round_data['round_no'] = r
        round_data['scenario'] = scenario_order[r-1] if len(scenario_order) >= r else None
        # Add all presurvey round variables for this round, but drop the round number from the column name
        for var in player_vars_presurvey_allR:
            colname = var.format(i=r)
            shortname = var.replace('presurvey.{i}.', '').replace('player.', '') # e.g. 'response', 'political_charge', 'emotional_charge'
            round_data[shortname] = row.get(colname, None)
        long_data_presurvey.append(round_data)

df_long_presurvey = pd.DataFrame(long_data_presurvey)
df_long_presurvey.shape # 15 vars over 10 participants (4 rows/rounds each)
# Save the long-format DataFrame to a CSV file
df_long_presurvey.to_csv(data_clean + 'presurvey_long_format.csv', index=False)



### MOCK APP participants
# Identify participants with incomplete mock app answers
invalid_participants = df_clean[df_clean['mock.5.player.new_response'].isnull()]
len(pd.Series(invalid_participants['participant.code']).unique())

# Print the participants with incomplete mock app answers
print("Participants with incomplete presurvey answers:")
print(invalid_participants[['participant.label']])

# Remove participants with incomplete mock app answers
df_clean = df_clean[~df_clean['participant.label'].isin(invalid_participants['participant.label'])].reset_index(drop=True)


# Verify the remaining participants
print(f"Remaining participants: {len(df_clean['participant.label'].unique())}")
print(f"Shape of df_clean after removal: {df_clean.shape}")

df_clean.columns


# For the mock app (discussion over 5 rounds), we need to keep the variables for all rounds
# and then create a dictionary with the player information for each round.
# The player information will include the participant code, scenario order, and responses for each round.
player_vars_mock_allR = [
    'mock.{i}.player.scenario',
    'mock.{i}.player.discussion_grp',
    'mock.{i}.player.old_response',
    'mock.{i}.player.new_response',
    'mock.{i}.player.forced_response'
]

### Prepare the long-format data for the 'mock app' only over 5 rounds
long_data = []
df_clean.shape
# Iterate through each row in the cleaned DataFrame and create a dictionary for each round of the mock app with the player information and responses.
# This will create a long-format DataFrame with one row per round per participant.
for idx, row in df_clean.iterrows():
    scenario_order = row['participant.scenario']
    for r in range(1, 6):
        round_data = {var: row[var] for var in player_info_vars} #player_info_vars is the participant unique identifier
        round_data['round_no'] = r
        round_data['scenario'] = scenario_order[r-1] if len(scenario_order) >= r else None
        # Add all mock round variables for this round, but drop the round number from the column name
        for var in player_vars_mock_allR:
            colname = var.format(i=r)
            shortname = var.replace('mock.{i}.', '').replace('player.', '')  # e.g. 'scenario', 'discussion_grp'
            round_data[shortname] = row.get(colname, None)
        long_data.append(round_data)

df_long = pd.DataFrame(long_data)
df_long.shape # 16 vars over 10 participants (5 rows/rounds each)

# Save the long-format DataFrame to a CSV file
df_long.to_csv(data_clean + 'mock_long_format.csv', index=False)


### Prepare the long-format data for the 'presurvey app' of those in the mock app
long_data_presurvey = []
# Iterate through each row in the cleaned DataFrame and create a dictionary for each round of the presurvey app with the player information and responses.
for idx, row in df_clean.iterrows():
    scenario_order = row['participant.scenario_order']
    for r in range(1, 5):  # Presurvey has 4 rounds
        round_data = {var: row[var] for var in player_info_vars} #player_info_vars is the participant unique identifier
        round_data['round_no'] = r
        round_data['scenario'] = scenario_order[r-1] if len(scenario_order) >= r else None
        # Add all presurvey round variables for this round, but drop the round number from the column name
        for var in player_vars_presurvey_allR:
            colname = var.format(i=r)
            shortname = var.replace('presurvey.{i}.', '').replace('player.', '') # e.g. 'response', 'political_charge', 'emotional_charge'
            round_data[shortname] = row.get(colname, None)
        long_data_presurvey.append(round_data)

df_long_presurvey = pd.DataFrame(long_data_presurvey)
df_long_presurvey.shape # 15 vars over 10 participants (4 rows/rounds each)
# Save the long-format DataFrame to a CSV file
df_long_presurvey.to_csv(data_clean + 'presurvey_mock_long_format.csv', index=False)