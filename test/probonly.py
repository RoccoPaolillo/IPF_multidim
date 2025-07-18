# -*- coding: utf-8 -*-
"""
Created on Sun Jul 13 23:39:23 2025

@author: LENOVO
"""

joint_distribution_rows = df[df['variable'].str.contains('_')]

# Display those rows to the user
tools.display_dataframe_to_user(name="Joint Distributions", dataframe=joint_distribution_rows)
joint_distribution_rows.head()

from itertools import product

# Define total population
total_population = 6333024

# Step 1: Extract marginal categories for each variable
# We ignore variables that contain an underscore (these are joint distributions)
marginals = df[~df['variable'].str.contains('_')]

# Group categories by variable
variable_categories = marginals.groupby('variable')['category'].apply(list).to_dict()

# Step 2: Generate all combinations of one category per marginal variable
combinations = list(product(*variable_categories.values()))

# Prepare results
results = []

# Create a quick lookup for values
value_lookup = dict(zip(zip(marginals['variable'], marginals['category']), marginals['value']))

# Step 3: Compute the formula for each combination
for combo in combinations:
    product_prob = 1.0
    for var, cat in zip(variable_categories.keys(), combo):
        value = value_lookup.get((var, cat), 0)
        product_prob *= value / total_population
    estimate = total_population * product_prob
    results.append({
        'combination': combo,
        'estimated_count': round(estimate)
    })

# Convert to DataFrame and show to user
results_df = pd.DataFrame(results)
tools.display_dataframe_to_user(name="Estimated Counts from Marginals", dataframe=results_df)
results_df.head()

#### JOINT DISTRIBUTIONS

# Extend to compute estimates for all combinations using multiple known joint distributions: age_hpt and age_hf

results_extended = []

for combo in combinations:
    combo_dict = dict(zip(variables, combo))

    gender = combo_dict['gender']
    age = combo_dict['age']
    hpt = combo_dict['hpt']
    hf = combo_dict['hf']

    # Get marginal values
    male_val = marginal_lookup.get(('gender', gender), 0)
    age_val = marginal_lookup.get(('age', age), 0)

    # Check if both joint distributions exist for this age
    hpt_joint_val = joint_age_hpt.get((age, hpt), None)
    hf_joint_val = joint_age_hf.get((age, hf), None)

    if hpt_joint_val is not None and hf_joint_val is not None and age_val > 0:
        # Apply full conditional formula with both joint distributions
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
        # Use marginals only
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

# Convert to DataFrame and display
results_extended_df = pd.DataFrame(results_extended)
tools.display_dataframe_to_user(name="Estimates with All Known Joint Distributions", dataframe=results_extended_df)
results_extended_df.head()
