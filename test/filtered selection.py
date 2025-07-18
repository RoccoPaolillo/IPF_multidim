import pandas as pd
from collections import defaultdict
import os

# Load the data
os.chdir("C:/Users/LENOVO/Documents/GitHub/IPF_multidim/")
df = pd.read_csv("syntheticpopulation.csv", delimiter=',')

component_sums = defaultdict(float)

# Loop through each row
for _, row in df.iterrows():
    components = row['combination'].split('_')
    for component in components:
        component_sums[component] += row['estimated_count']

# Convert to a DataFrame for readability
result_df = pd.DataFrame(component_sums.items(), columns=['component', 'total_estimated_count'])
result_df = result_df.sort_values(by='total_estimated_count', ascending=False)
result_df['total_estimated_count'] = result_df['total_estimated_count'].astype(int)
result_df.to_csv("back_marginals.csv",index = False)


# Define the target components to filter for
target_components = ["female","age60100","hptyes"]



# Filter rows where all target components are present
mask = df['combination'].apply(lambda x: all(comp in x.split('_') for comp in target_components))
matching_rows = df[mask]

# Calculate total
total_estimated_count = matching_rows['estimated_count'].sum()
total_estimated_countdf = pd.DataFrame([{'combination': '_'.join(target_components) ,'estimated_count': total_estimated_count}])
total_estimated_countdf.to_csv("filtered_syntheticTEST.csv", index=False)