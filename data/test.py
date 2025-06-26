import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

page_time = pd.read_csv('PageTimes-b0qkdyda.csv')
participant_code = page_time['participant_code'].unique().tolist()
len(participant_code)

page_names = page_time['page_name'].unique().tolist()
page_names 

# Create a function to compute time differences between consecutive pages for a given participant
def compute_page_time_differences(page_time, page_names, participant):
    """
    Compute differences in epoch_time_completed for consecutive pages for a given participant.

    Args:
        page_time (DataFrame): The DataFrame containing page time data.
        page_names (list): List of mock page names to compute differences for.
        participant (str): The participant code.

    Returns:
        list: A list of differences in epoch_time_completed for consecutive pages.
    """
    differences = []
    for i in range(1, len(page_names)):
        # Filter data for the current and previous page
        page_prev = page_time[
            (page_time['page_name'] == page_names[i - 1]) &
            (page_time['participant_code'] == participant)
        ]
        page_curr = page_time[
            (page_time['page_name'] == page_names[i]) &
            (page_time['participant_code'] == participant)
        ]
        
        # Check if both pages have data for the participant
        if not page_prev.empty and not page_curr.empty:
            # Compute the difference for the given participant
            time_diff = page_curr['epoch_time_completed'].values[0] - page_prev['epoch_time_completed'].values[0]
            differences.append(int(time_diff))
        else:
            # Append None if data is missing
            differences.append(None)
    
    return differences



# Example usage:
participant = 'kl6idv17'
time_differences = compute_page_time_differences(page_time, page_names, participant)
print(f"Time differences for participant {participant}: {time_differences}")


### Mock app analysis ###
mock_page_names = page_names[-8:]

# Create a dictionary to store time differences for each participant
participant_time_differences = {}

for participant in participant_code:
    # Compute time differences for the current participant
    time_differences = compute_page_time_differences(page_time, mock_page_names, participant)
    
    # Store the result in the dictionary
    participant_time_differences[participant] = time_differences

# Compute the average and standard deviation across all participants
num_pages = len(mock_page_names) - 1  # Number of page transitions
average_differences = []
std_differences = []

for i in range(num_pages):
    # Collect differences for the current page transition across all participants
    values = [differences[i] for differences in participant_time_differences.values() if differences[i] is not None]
    
    # Compute the average and standard deviation
    if values:
        average_differences.append(np.mean(values))
        std_differences.append(np.std(values))
    else:
        average_differences.append(0)
        std_differences.append(0)

# Create x-axis values (sequence of page names)
# x_values = range(1, num_pages + 1)  # Sequence of page transitions
x_values = []
for i in mock_page_names[1:]: # Exclude the first page for x-axis
    x_values.append(i)

plt.figure(figsize=(20, 6))
# Plot the average differences with error bars
plt.errorbar(x_values, average_differences, yerr=std_differences, fmt='-o', capsize=5, label='Average Time Differences')

plt.xticks(rotation=45, ha='right')  # Rotate x-axis 

# Annotate each point with its value
for i, (x, y) in enumerate(zip(x_values, average_differences)):
    plt.text(x, y, f'{y:.2f}', fontsize=10, ha='center', va='bottom')  # Display value with 2 decimal places

# Add labels and title
plt.xlabel('Page Time in Mock app')
plt.show()
#plt.savefig('average_time_differences_mock.png')
plt.close()






### Full app analysis (N=10) ###
# Create a dictionary to store time differences for each participant
participant_time_differences = {}

# filter to only include those who have data for the ALL app
page_time_full_app = page_time[page_time['app_name'] == 'Pay']
participant_code_full = page_time_full_app['participant_code'].unique().tolist()
page_time_full_app = page_time[page_time['participant_code'].isin(participant_code_full)]
#page_name_full_app = page_time_full_app['page_name'].unique().tolist()

page_name_full_app = ['InitializeParticipant',
 'Introduction',
 'Demographics',
 'NeighborhoodInstruction',
 'Neighborhood',
 'Training',
 'TrainingNeighbor_1',
 'TrainingNeighbor_2',
 'ExperimentInstruction',
 'Neighborhood_1',
 'Scenario',
 'Commitment',
 'FinalPage',
 'GroupingWaitPage',
 'GroupSizeWaitPage',
 'DiscussionGRPWaitPage',
 'Phase3',
 'Nudge',
 'Discussion',
 'Feedback']


for i in participant_code_full:
    # Compute time differences for the current participant
    time_differences = compute_page_time_differences(page_time_full_app, page_name_full_app, i)
    
    # Store the result in the dictionary
    participant_time_differences[i] = time_differences

# Compute the average and standard deviation across all participants
num_pages = len(page_name_full_app) - 1  # Number of page transitions
average_differences = []
std_differences = []

for i in range(num_pages):
    # Collect differences for the current page transition across all participants
    values = [differences[i] for differences in participant_time_differences.values() if differences[i] is not None]
    
    # Compute the average and standard deviation
    if values:
        average_differences.append(np.mean(values))
        std_differences.append(np.std(values))
    else:
        average_differences.append(0)
        std_differences.append(0)

# Create x-axis values (sequence of page names)
# x_values = range(1, num_pages + 1)  # Sequence of page transitions
x_values = []
for i in page_name_full_app[1:]: # Exclude the first page for x-axis
    x_values.append(i)

plt.figure(figsize=(20, 6))
# Plot the average differences with error bars
plt.errorbar(x_values, average_differences, yerr=std_differences, fmt='-o', capsize=5, label='Average Time Differences')

# Set y-axis limit
plt.ylim(0, 600)
plt.xticks(rotation=45, ha='right')  # Rotate x-axis 

# Annotate each point with its value
for i, (x, y) in enumerate(zip(x_values, average_differences)):
    plt.text(x, y, f'{y:.2f}', fontsize=10, ha='center', va='bottom')  # Display value with 2 decimal places

# Add labels and title
plt.xlabel('Page Time in ALL app')
plt.show()
plt.savefig('average_time_N10.png')



### Presurvey app analysis ###
presurvey_page_names = page_names[:14]
presurvey_page_names = ['InitializeParticipant',
 'Introduction',
 'Demographics',
 'NeighborhoodInstruction',
 'Neighborhood',
 'Training',
 'TrainingNeighbor_1',
 'TrainingNeighbor_2',
 'ExperimentInstruction',
 'Neighborhood_1',
 'Scenario',
 'Commitment',
 'FinalPage',]
 #'AttentionCheck']
# Create a dictionary to store time differences for each participant
participant_time_differences = {}

for participant in participant_code:
    # Compute time differences for the current participant
    time_differences = compute_page_time_differences(page_time, presurvey_page_names, participant)
    
    # Store the result in the dictionary
    participant_time_differences[participant] = time_differences

# Compute the average and standard deviation across all participants
num_pages = len(presurvey_page_names) - 1

for i in participant_code_full:
    # Compute time differences for the current participant
    time_differences = compute_page_time_differences(page_time_full_app, presurvey_page_names, i)
    
    # Store the result in the dictionary
    participant_time_differences[i] = time_differences

# Compute the average and standard deviation across all participants
num_pages = len(presurvey_page_names) - 1  # Number of page transitions
average_differences = []
std_differences = []

for i in range(num_pages):
    # Collect differences for the current page transition across all participants
    values = [differences[i] for differences in participant_time_differences.values() if differences[i] is not None]
    
    # Compute the average and standard deviation
    if values:
        average_differences.append(np.mean(values))
        std_differences.append(np.std(values))
    else:
        average_differences.append(0)
        std_differences.append(0)

# Create x-axis values (sequence of page names)
# x_values = range(1, num_pages + 1)  # Sequence of page transitions
x_values = []
for i in presurvey_page_names[1:]: # Exclude the first page for x-axis
    x_values.append(i)

plt.figure(figsize=(20, 6))
# Plot the average differences with error bars
plt.errorbar(x_values, average_differences, yerr=std_differences, fmt='-o', capsize=5, label='Average Time Differences')
plt.ylim(0, 600)  # Set y-axis limit
plt.xticks(rotation=45, ha='right')  # Rotate x-axis 

# Annotate each point with its value
for i, (x, y) in enumerate(zip(x_values, average_differences)):
    plt.text(x, y, f'{y:.2f}', fontsize=10, ha='center', va='bottom')  # Display value with 2 decimal places

# Add labels and title
plt.xlabel('Page Time in presurvey app')
plt.show()
plt.savefig('average_time_differences_presurvey.png')






### Those who waited ###
participant_code

# Filter otree_data to find matching participant.code
participant_label_wait = pd.read_csv('participantid_waitingbonus.csv')['Participant id'].unique().tolist()
otree_data = pd.read_csv('all_apps_wide_b0qkdyda.csv')
len(participant_code_wait) # 15 people who waited

participant_code_wait = otree_data[otree_data['participant.label'].isin(participant_label_wait)]['participant.code'].unique().tolist()

page_time_wait = page_time[page_time['participant_code'].isin(participant_code_wait)]

page_name_wait = ['InitializeParticipant',
 'Introduction',
 'Demographics',
 'NeighborhoodInstruction',
 'Neighborhood',
 'Training',
 'TrainingNeighbor_1',
 'TrainingNeighbor_2',
 'ExperimentInstruction',
 'Neighborhood_1',
 'Scenario',
 'Commitment',
 'FinalPage',
# 'AttentionCheck',
 'GroupingWaitPage',
 'GroupSizeWaitPage',
 'DiscussionGRPWaitPage']

# Create a dictionary to store time differences for each participant
participant_time_differences = {}
for i in participant_code_wait:
    # Compute time differences for the current participant
    time_differences = compute_page_time_differences(page_time_wait, page_name_wait, i)
    
    # Store the result in the dictionary
    participant_time_differences[i] = time_differences

# Compute the average and standard deviation across all participants
num_pages = len(page_name_wait) - 1  # Number of page transitions
average_differences = []
std_differences = []

for i in range(num_pages):
    # Collect differences for the current page transition across all participants
    values = [differences[i] for differences in participant_time_differences.values() if differences[i] is not None]
    
    # Compute the average and standard deviation
    if values:
        average_differences.append(np.mean(values))
        std_differences.append(np.std(values))
    else:
        average_differences.append(0)
        std_differences.append(0)

# Create x-axis values (sequence of page names)
# x_values = range(1, num_pages + 1)  # Sequence of page transitions
x_values = []
for i in page_name_wait[1:]: # Exclude the first page for x-axis
    x_values.append(i)

plt.figure(figsize=(20, 6))
# Plot the average differences with error bars
plt.errorbar(x_values, average_differences, yerr=std_differences, fmt='-o', capsize=5, label='Average Time Differences')

plt.xticks(rotation=45, ha='right')  # Rotate x-axis 

# Annotate each point with its value
for i, (x, y) in enumerate(zip(x_values, average_differences)):
    plt.text(x, y, f'{y:.2f}', fontsize=10, ha='center', va='bottom')  # Display value with 2 decimal places

# Add labels and title
plt.xlabel('Page Time for those who waited')
plt.show()
plt.savefig('average_time_differences_wait.png')



### Find arrival time for those who waited ###
# Load participant_code_wait and otree_data


# Filter otree_data to find matching participant.code
participant_label_wait = pd.read_csv('participantid_waitingbonus.csv')['Participant id'].unique().tolist()
otree_data = pd.read_csv('all_apps_wide_b0qkdyda.csv')
len(participant_code_wait) # 15 people who waited

participant_code_wait = otree_data[otree_data['participant.label'].isin(participant_label_wait)]['participant.code'].unique().tolist()

page_time_wait = page_time[page_time['participant_code'].isin(participant_code_wait)]

page_name_wait = ['InitializeParticipant',
 'Introduction',
 'Demographics',
 'NeighborhoodInstruction',
 'Neighborhood',
 'Training',
 'TrainingNeighbor_1',
 'TrainingNeighbor_2',
 'ExperimentInstruction',
 'Neighborhood_1',
 'Scenario',
 'Commitment',
 'FinalPage',
# 'AttentionCheck',
 'GroupingWaitPage',
 'GroupSizeWaitPage',
 'DiscussionGRPWaitPage']

# Filter rows where app_name is "Pay" for those who only waited (not continue)
pay_epoch_times = page_time_wait[page_time_wait['app_name'] == 'Pay'][['epoch_time_completed', 'page_name']]

pay_epoch_times = pay_epoch_times.loc[pay_epoch_times['page_name'] == 'FinalPage', 'epoch_time_completed']

# those who needed trianing neighbor 2
# everyone
test = page_time.loc[page_time['page_name'] == 'TrainingNeighbor_2', 'epoch_time_completed']
len(test)
# those who waited but not matched
test = page_time_wait.loc[page_time_wait['page_name'] == 'TrainingNeighbor_2', 'epoch_time_completed']
len(test)
# those who waited and matched
test = page_time_full_app.loc[page_time_full_app['page_name'] == 'TrainingNeighbor_2', 'epoch_time_completed']
len(test)

from datetime import datetime, timezone, timedelta

# Convert epoch times to date and time in GMT+2
pay_epoch_times_converted = pay_epoch_times.apply(
    lambda x: datetime.fromtimestamp(x, tz=timezone(timedelta(hours=2)))
)

pay_epoch_times_converted
# Save the converted epoch times to a CSV file
pay_epoch_times_converted.to_csv('waitingonly_FinalPage_time.csv', index=False)

# Filter rows where app_name is "Pay" for those who only waited (not continue)
pay_full_epoch_times = page_time_full_app[page_time_full_app['app_name'] == 'presurvey'][['epoch_time_completed', 'page_name']]

pay_full_epoch_times = pay_full_epoch_times.loc[pay_full_epoch_times['page_name'] == 'FinalPage', 'epoch_time_completed']

test = pay_full_epoch_times.loc[pay_full_epoch_times['page_name'] == 'TrainingNeighbor_2', 'epoch_time_completed']

# Convert epoch times to date and time in GMT+2
pay_full_epoch_times_converted = pay_full_epoch_times.apply(
    lambda x: datetime.fromtimestamp(x, tz=timezone(timedelta(hours=2)))
)

pay_full_epoch_times_converted
# Save the converted epoch times to a CSV file
pay_full_epoch_times_converted.to_csv('N10allapp_FinalPage_time.csv', index=False)