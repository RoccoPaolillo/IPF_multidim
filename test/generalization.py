from itertools import product
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("C:/Users/LENOVO/Documents/GitHub/IPF_multidim/input_marginals.csv", delimiter=';')

# Rebuild variable-category-value structure
#df_split = df["variable;category;value"].str.split(";", expand=True)
#df_split.columns = ["variable", "category", "value"]
#df_split["value"] = pd.to_numeric(df_split["value"])

# Create a lookup dictionary
# value_dict = df_split.set_index(["variable", "category"])["value"].to_dict()
total_population = 6333024

# Separate joint and marginal distributions
joint_df = df[df['variable'].str.contains('_')]
marginals_df = df[~df['variable'].str.contains('_')]

# Build marginal lookup
marginal_lookup = dict(zip(zip(marginals_df['variable'], marginals_df['category']), marginals_df['value']))

# Group marginals by variable
marginal_groups = marginals_df.groupby('variable')['category'].apply(list).to_dict()
variables = list(marginal_groups.keys()) # here the position for loop

# Create all combinations
combinations = list(product(*[marginal_groups[v] for v in variables]))

# Parse joint_map from joint_df
joint_map = {}
for _, row in joint_df.iterrows():
    joint_var = row['variable']
    joint_cats = row['category']
    value = row['value']
    var1, var2 = joint_var.split('_')
    cat1, cat2 = joint_cats.split('_')
    joint_map[(var1, var2, cat1, cat2)] = value  # split the individual components of joint distribution

# Identify age-based joint distributions for hpt and hf
joint_age_hpt = {(c1, c2): val for (v1, v2, c1, c2), val in joint_map.items() if v1 == "age" and v2 == "hpt"}
joint_age_hf = {(c1, c2): val for (v1, v2, c1, c2), val in joint_map.items() if v1 == "age" and v2 == "hf"}

# Apply correct logic
results_extended = []

for combo in combinations:
    combo_dict = dict(zip(variables, combo))

    gender = combo_dict['gender'] # key of the dictionary we should not call by name
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
