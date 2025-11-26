#!/usr/bin/env python3
"""
Analyze oTree devserver CSV output (all_apps_wide format) for fixed network experiment.
This script works with CSV files downloaded from the devserver admin interface.

Usage: python3 devserver_bots_analysis.py [csv_file]
Example: python3 devserver_bots_analysis.py devserver_all_apps_wide-2025-11-26.csv
"""

import pandas as pd
import numpy as np
import sys

def analyze_devserver_network(csv_path):
    """Analyze the fixed network structure from devserver all_apps_wide CSV"""
    
    # Read the wide format CSV
    df = pd.read_csv(csv_path)
    
    print("=" * 70)
    print("DEVSERVER SESSION - FIXED NETWORK ANALYSIS")
    print("=" * 70)
    print()
    
    # Get participant info
    print("📊 OVERVIEW")
    print("-" * 70)
    print(f"Total participants: {len(df)}")
    
    # Check round 1 to see who has discussion_grp data
    round1_discussion = df['mock.1.player.discussion_grp']
    participants_with_data = round1_discussion.notna().sum()
    print(f"Participants with mock data: {participants_with_data}")
    
    # Determine number of rounds by checking column names
    mock_rounds = []
    for col in df.columns:
        if col.startswith('mock.') and '.player.discussion_grp' in col:
            round_num = int(col.split('.')[1])
            mock_rounds.append(round_num)
    max_round = max(mock_rounds) if mock_rounds else 0
    print(f"Total rounds: {max_round}")
    print()
    
    # Expected network
    print("🔗 EXPECTED NETWORK")
    print("-" * 70)
    print("Position 1 → neighbors at positions [2, 3]")
    print("Position 2 → neighbors at positions [1, 4]")
    print("Position 3 → neighbors at positions [1, 4]")
    print("Position 4 → neighbors at positions [2, 3]")
    print()
    
    # Analyze round 1
    print("✅ ACTUAL NETWORK (Round 1)")
    print("-" * 70)
    
    # Filter participants who have discussion_grp data
    active_participants = df[df['mock.1.player.discussion_grp'].notna()].copy()
    
    if len(active_participants) > 0:
        # Sort by position for cleaner output
        active_participants = active_participants.sort_values('mock.1.player.id_in_group')
        
        for idx, row in active_participants.iterrows():
            participant_code = row['participant.code']
            position = int(row['mock.1.player.id_in_group'])
            neighbors = row['mock.1.player.discussion_grp']
            print(f"Position {position} ({participant_code}): neighbors={neighbors}")
        
        print()
        print("🔍 NETWORK CONSISTENCY CHECK")
        print("-" * 70)
        
        # Check consistency across rounds
        for idx, row in active_participants.iterrows():
            participant_code = row['participant.code']
            
            # Get discussion_grp for all rounds
            discussion_grps = []
            for r in range(1, max_round + 1):
                col_name = f'mock.{r}.player.discussion_grp'
                if col_name in df.columns and pd.notna(row[col_name]):
                    discussion_grps.append(row[col_name])
            
            unique_neighbors = len(set(discussion_grps))
            total_rounds = len(discussion_grps)
            status = '✓' if unique_neighbors == 1 else '✗'
            print(f"{status} {participant_code}: {total_rounds} rounds, {unique_neighbors} unique neighbor set(s)")
        
        if all(len(set([row[f'mock.{r}.player.discussion_grp'] 
                       for r in range(1, max_round + 1) 
                       if pd.notna(row[f'mock.{r}.player.discussion_grp'])])) == 1 
               for idx, row in active_participants.iterrows()):
            print("✅ All players have consistent networks across all rounds!")
        
        print()
        print("📈 SAMPLE RESPONSES")
        print("-" * 70)
        
        for round_num in [1, 10, 20]:
            if round_num <= max_round:
                print(f"\nRound {round_num}:")
                for idx, row in active_participants.iterrows():
                    participant_code = row['participant.code']
                    pos = int(row[f'mock.{round_num}.player.id_in_group'])
                    
                    old_r = row[f'mock.{round_num}.player.old_response']
                    new_r = row[f'mock.{round_num}.player.new_response']
                    neighbor_resp = row[f'mock.{round_num}.player.neighbor_responses']
                    
                    old_r = int(old_r) if pd.notna(old_r) else 'NA'
                    new_r = int(new_r) if pd.notna(new_r) else 'NA'
                    
                    print(f"  P{pos}: old={old_r:2}, new={new_r:2}, neighbors={neighbor_resp}")
        
        # Group treatment details if available
        if 'mock.1.group.group_size' in df.columns:
            print()
            print("📈 GROUP TREATMENT DETAILS")
            print("-" * 70)
            first_row = active_participants.iloc[0]
            print(f"Group size: {first_row['mock.1.group.group_size']}")
            if pd.notna(first_row.get('mock.1.group.beta_50')):
                print(f"Beta 50: {first_row['mock.1.group.beta_50']}")
            if pd.notna(first_row.get('mock.1.group.anti_prop')):
                print(f"Anti-conformist proportion: {first_row['mock.1.group.anti_prop']}")
            
            # Final round majority
            final_col = f'mock.{max_round}.group.majority_response'
            if final_col in df.columns and pd.notna(first_row[final_col]):
                maj = first_row[final_col]
                maj_val = int(maj) if maj != 99 else 'No majority (tie)'
                print(f"Final majority response: {maj_val}")
    else:
        print("No participants with discussion data found!")
    
    print()
    print("=" * 70)
    print("✅ Analysis complete!")
    print("=" * 70)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        # Default to the most recent file
        csv_path = 'devserver_all_apps_wide-2025-11-26.csv'
    
    try:
        analyze_devserver_network(csv_path)
    except FileNotFoundError:
        print(f"Error: File '{csv_path}' not found!")
        print()
        print("Usage: python3 devserver_bots_analysis.py [csv_file]")
        print("Example: python3 devserver_bots_analysis.py devserver_all_apps_wide-2025-11-26.csv")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
