import pandas as pd
import datetime

def possession_time():
    df = pd.read_csv('QuadballStats.csv')

    df = df.dropna(subset=['Timestamp'])
    df['Timestamp_td'] = pd.to_timedelta(df['Timestamp'])
    df = df.sort_values(by='Timestamp_td')

    df = df.drop(['Tournament', 'Game Link'], axis=1)

    possession_start_mask = df['Event Type'].isin(['Possession Change'])

    df['Possession ID'] = possession_start_mask.cumsum()
    df['Possessing Team'] = df.groupby('Possession ID')['Posteam'].transform('first')

    possession_starts_df = df[
        df['Event Type'].isin(['Possession Change']) & df['Posteam'].notna()
    ].copy()
    possession_starts_df = possession_starts_df[['Possession ID', 'Timestamp_td', 'Posteam']]
    possession_starts_df = possession_starts_df.rename(columns={'Timestamp_td': 'Start_time_td'})

    goal_times_df = df[df['Event Type'] == 'Goal Scored'].copy()
    goal_times_df = goal_times_df[['Possession ID', 'Timestamp_td']]
    goal_times_df = goal_times_df.rename(columns={'Timestamp_td': 'Goal_time_td'})

    merged_df = pd.merge(possession_starts_df, goal_times_df, on='Possession ID')
    merged_df['Time_to_goal_sec'] = (merged_df['Goal_time_td'] - merged_df['Start_time_td']).dt.total_seconds().round(0).astype('Int64')
    print(merged_df[(merged_df['Posteam'] == 'UTSA') & (merged_df['Time_to_goal_sec'] <= 10)].to_markdown(index=False))

    goal_possession_ids = df[df['Event Type'] == 'Goal Scored']['Possession ID'].unique()

    possessions_df = df[df['Event Type'].isin(['Possession Change', 'Game End'])].copy()
    possessions_df['End Time'] = possessions_df['Timestamp_td'].shift(-1)
    possessions_df['Duration_sec'] = (possessions_df['End Time'] - possessions_df['Timestamp_td']).dt.total_seconds()
    
    final_analysis = possessions_df[
        (possessions_df['Posteam'].notna()) &
        (possessions_df['Duration_sec'].notna())
    ].copy()

    final_analysis = final_analysis.rename(columns={
        'Posteam': 'Possessing_Team',
        'Timestamp': 'Start_Time'
    })

    final_analysis['Goal_Scored'] = final_analysis['Possession ID'].isin(goal_possession_ids)

    final_report = final_analysis[[
        'Possession ID',
        'Possessing_Team',
        'Start_Time',
        'Duration_sec',
        'Goal_Scored'
    ]]


    exclude = [13, 67, 7, 9, 11, 15, 17, 19, 21, 43, 47, 71, 77, 79]
    print(final_report[final_report['Possession ID'].isin(exclude)].to_markdown(index=False))

    ut_pos = final_analysis[final_analysis['Possessing_Team'] == 'UT']
    total_top = datetime.timedelta(seconds=ut_pos['Duration_sec'].sum())
    average_top = round((total_top / len(ut_pos)).total_seconds(), 2)
    average_top_goals = round(datetime.timedelta(seconds=ut_pos[ut_pos['Goal_Scored']]['Duration_sec'].mean()).total_seconds(), 2)

    print(f"The total time of possession for UT was {total_top}. The average time per possession was {average_top} seconds. The average time per possession that resulted in a goal was {average_top_goals} seconds.")

    print(datetime.timedelta(seconds=final_analysis[final_analysis['Possessing_Team'] == 'UTSA']['Duration_sec'].sum()))

possession_time()