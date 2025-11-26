#!/usr/bin/env python3
"""
Analyze oTree bot test CSV output for fixed network experiment.
This script validates the fixed network structure and shows key statistics.
"""

import pandas as pd
import json
import sys

def analyze_network(csv_path='bot_test_data/mock.csv'):
    """Analyze the fixed network structure from mock.csv"""
    
    df = pd.read_csv(csv_path)
    df_game = df[df['player.discussion_grp'].notna()].copy()
    
    print('=' * 70)
    print('FIXED NETWORK EXPERIMENT - CSV ANALYSIS')
    print('=' * 70)
    print()
    
    # Overview
    print('📊 EXPERIMENT OVERVIEW')
    print('-' * 70)
    print(f'Total participants in session: {df["participant.code"].nunique()}')
    print(f'Participants who played mock app: {df_game["participant.code"].nunique()}')
    print(f'Total rounds: {df_game["subsession.round_number"].max():.0f}')
    print(f'Total data rows: {len(df_game)}')
    print()
    
    # Expected network
    print('🔗 EXPECTED FIXED NETWORK STRUCTURE')
    print('-' * 70)
    print('Position 1 → neighbors at positions [2, 3]')
    print('Position 2 → neighbors at positions [1, 4]')
    print('Position 3 → neighbors at positions [1, 4]')
    print('Position 4 → neighbors at positions [2, 3]')
    print()
    
    # Find 4-player groups (those with exactly 2 neighbors)
    print('✅ ACTUAL 4-PLAYER GROUPS')
    print('-' * 70)
    
    round1 = df_game[df_game['subsession.round_number'] == 1].copy()
    four_player_participants = []
    
    for _, row in round1.iterrows():
        disc_grp_str = row['player.discussion_grp']
        neighbors = eval(disc_grp_str)
        if len(neighbors) == 2:
            four_player_participants.append(row['participant.code'])
    
    # Group them into sets of 4
    groups_found = len(four_player_participants) // 4
    print(f'Found {groups_found} complete 4-player group(s)\n')
    
    # Analyze each group
    for group_num in range(groups_found):
        start_idx = group_num * 4
        end_idx = start_idx + 4
        group_codes = four_player_participants[start_idx:end_idx]
        
        print(f'Group {group_num + 1}: {group_codes}')
        
        # Show network structure
        for code in group_codes:
            player_data = round1[round1['participant.code'] == code].iloc[0]
            pos = int(player_data['player.id_in_group'])
            neighbors = player_data['player.discussion_grp']
            print(f'  Position {pos} ({code}): neighbors={neighbors}')
        
        # Verify consistency across rounds
        print('\n  Network Consistency Check:')
        all_consistent = True
        for code in group_codes:
            participant_data = df_game[df_game['participant.code'] == code]
            unique_neighbors = participant_data['player.discussion_grp'].nunique()
            is_consistent = unique_neighbors == 1
            rounds = len(participant_data)
            status = '✓' if is_consistent else '✗'
            print(f'    {status} {code}: {rounds} rounds, {unique_neighbors} unique neighbor set(s)')
            if not is_consistent:
                all_consistent = False
        
        if all_consistent:
            print('  ✅ All players have consistent networks across all rounds!')
        print()
        
        # Show sample rounds
        print(f'  Sample Responses:')
        for round_num in [1, 10, 20]:
            print(f'    Round {round_num}:')
            for code in group_codes:
                player_round = df_game[(df_game['participant.code'] == code) & 
                                       (df_game['subsession.round_number'] == round_num)]
                if len(player_round) > 0:
                    row = player_round.iloc[0]
                    pos = int(row['player.id_in_group'])
                    old_r = int(row['player.old_response']) if pd.notna(row['player.old_response']) else 'NA'
                    new_r = int(row['player.new_response']) if pd.notna(row['player.new_response']) else 'NA'
                    neighbor_resp = row['player.neighbor_responses']
                    print(f'      P{pos}: old={old_r:2}, new={new_r:2}, neighbors={neighbor_resp}')
        print()
    
    # Group statistics
    if groups_found > 0:
        sample_group_data = df_game[df_game['participant.code'].isin(four_player_participants[:4])]
        if len(sample_group_data) > 0:
            print('📈 GROUP TREATMENT DETAILS')
            print('-' * 70)
            first_row = sample_group_data.iloc[0]
            print(f'Group size: {first_row["group.group_size"]}')
            print(f'Beta 50: {first_row["group.beta_50"]}')
            print(f'Anti-conformist proportion: {first_row["group.anti_prop"]}')
            
            # Final round majority
            final_round = sample_group_data[sample_group_data['subsession.round_number'] == 20]
            if len(final_round) > 0:
                maj = final_round.iloc[0]['group.majority_response']
                if pd.notna(maj):
                    maj_val = int(maj) if maj != 99 else 'No majority (tie)'
                    print(f'Final majority response: {maj_val}')
    
    print()
    print('=' * 70)
    print('Analysis complete! ✨')
    print('=' * 70)

if __name__ == '__main__':
    csv_path = sys.argv[1] if len(sys.argv) > 1 else 'bot_test_data/mock.csv'
    analyze_network(csv_path)
