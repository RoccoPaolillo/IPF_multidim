# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 01:02:28 2025

@author: LENOVO
"""

# Load the new dataset provided by the user
new_file_path = "/mnt/data/input_marginals.csv"
df = pd.read_csv(new_file_path, delimiter=';')

# Re-define total population
total_population = 6333024

# Separate joint and marginal distributions
joint_df = df[df['variable'].str.contains('_')]
marginals_df = df[~df['variable'].str.contains('_')]

# Build marginal lookup
marginal_lookup = dict(zip(zip(marginals_df['variable'], marginals_df['category']), marginals_df['value']))

# Group marginals by variable
marginal_groups = marginals_df.groupby('variable')['category'].apply(list).to_dict()
variables = list(marginal_groups.keys())

# Create all combinations
from itertools import product
combinations = list(product(*[marginal_groups[v] for v in variables]))

# Parse joint_map from joint_df
joint_map = {}
for _, row in joint_df.iterrows():
    joint_var = row['variable']
    joint_cats = row['category']
    value = row['value']
    var1, var2 = joint_var.split('_')
    cat1, cat2 = joint_cats.split('_')
    joint_map[(var1, var2, cat1, cat2)] = value

# Identify age-based joint distributions for hpt and hf
joint_age_hpt = {(c1, c2): val for (v1, v2, c1, c2), val in joint_map.items() if v1 == "age" and v2 == "hpt"}
joint_age_hf = {(c1, c2): val for (v1, v2, c1, c2), val in joint_map.items() if v1 == "age" and v2 == "hf"}

# Apply correct logic
results_extended = []

for combo in combinations:
    combo_dict = dict(zip(variables, combo))

    gender = combo_dict['gender']
    age = combo_dict['age']
    hpt = combo_dict['hpt']
    hf = combo_dict['hf']

    male_val = marginal_lookup.get(('gender', gender), 0)
    age_val = marginal_lookup.get(('age', age), 0)

    hpt_joint_val = joint_age_hpt.get((age, hpt), None)
    hf_joint_val = joint_age_hf.get((age, hf), None)

    if hpt_joint_val is not None and hf_joint_val is not None and age_val > 0:
        estimate = (male_val / total_population) * age_val * (
            (hpt_joint_val / age_val) * (hf_joint_val / age_val)
        )
        used_joint = "age_hpt + age_hf"
    elif hpt_joint_val is not None and age_val > 0:
        estimate = (male_val / total_population) * age_val * (hpt_joint_val / age_val) * (
            marginal_lookup.get(('hf', hf), 0) / total_population
        )
        used_joint = "age_hpt"
    elif hf_joint_val is not None and age_val > 0:
        estimate = (male_val / total_population) * age_val * (hf_joint_val / age_val) * (
            marginal_lookup.get(('hpt', hpt), 0) / total_population
        )
        used_joint = "age_hf"
    else:
        estimate = 1.0
        for var in variables:
            val = marginal_lookup.get((var, combo_dict[var]), 0)
            estimate *= val / total_population
        estimate *= total_population
        used_joint = "none"

    results_extended.append({
        'combination': combo,
        'estimated_count': round(estimate),
        'used_joint': used_joint
    })

# Create and display the results
results_extended_df = pd.DataFrame(results_extended)
import ace_tools as tools; tools.display_dataframe_to_user(name="Extended Estimates from New Dataset", dataframe=results_extended_df)
