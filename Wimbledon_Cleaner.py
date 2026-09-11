import pandas as pd

master_df = pd.read_excel('Wimbledon.xlsx')
flags_df = pd.read_csv('Wimbledon_Live_Flags.csv')

valid_filenames = set(master_df['Filename'].dropna().tolist())
dropped_files = flags_df[~flags_df['Filename'].isin(valid_filenames)]['Filename'].tolist()

print(f"Removing {len(dropped_files)} unmatched snapshot records:")
for f in dropped_files:
    print(f"- {f}")

cleaned_flags_df = flags_df[flags_df['Filename'].isin(valid_filenames)]

# Save as the exact name you have in your folder
cleaned_flags_df.to_csv('Cleaned_Wimbledon_Dataset.csv', index=False)
print("Dataset cleaning complete.")