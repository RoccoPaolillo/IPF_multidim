from itertools import product
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import combinations as it_combinations



def generalized_joint_estimator(df, total_population):
    # Separate joint and marginal distributions
    joint_df = df[df['variable'].str.contains('_')]
    marginals_df = df[~df['variable'].str.contains('_')]

    # Build marginal lookup
    marginal_lookup = dict(zip(zip(marginals_df['variable'], marginals_df['category']), marginals_df['value']))

    # Group marginals by variable
    marginal_groups = marginals_df.groupby('variable')['category'].apply(list).to_dict()
    variables = list(marginal_groups.keys())

    # Generate all combinations of categories
    all_combinations = list(product(*[marginal_groups[v] for v in variables]))

    # Step 1: Parse joint distributions into a structured dictionary
    joint_distributions = {}
    for _, row in joint_df.iterrows():
        vars_tuple = tuple(row['variable'].split('_'))
        cats_tuple = tuple(row['category'].split('_'))
        value = row['value']
        joint_distributions.setdefault(vars_tuple, {})[cats_tuple] = value

    # Step 2: Estimate each combination
    results = []

    for category_combo in all_combinations:
        combo_dict = dict(zip(variables, category_combo))
        estimate = 1.0
        used_vars = set()
        used_joints = []

        # Try using joint distributions in descending order of joint size
        for joint_vars in sorted(joint_distributions.keys(), key=lambda x: -len(x)):
            if all(v in combo_dict for v in joint_vars):
                joint_cats = tuple(combo_dict[v] for v in joint_vars)
                joint_val = joint_distributions[joint_vars].get(joint_cats, None)

                # Find base variable to normalize the joint (first variable)
                base_var = joint_vars[0]
                base_cat = combo_dict[base_var]
                base_val = marginal_lookup.get((base_var, base_cat), None)

                if joint_val is not None and base_val:
                    # P(joint | base_var) * P(base_var)
                    estimate *= (joint_val / base_val) * (base_val / total_population)
                    used_vars.update(joint_vars)
                    used_joints.append('_'.join(joint_vars))

        # Multiply remaining marginals
        for var in variables:
            if var not in used_vars:
                val = marginal_lookup.get((var, combo_dict[var]), 0)
                estimate *= val / total_population

        results.append({
            'combination': category_combo,
            'estimated_count': round(estimate * total_population),
            'used_joints': ', '.join(sorted(used_joints)) if used_joints else 'none'
        })

    return pd.DataFrame(results)

# Apply the generalized function to the current dataset

df = pd.read_csv("C:/Users/LENOVO/Documents/GitHub/IPF_multidim/input_marginals.csv", delimiter=';')
total_population = 6333024
results_generalized = generalized_joint_estimator(df, total_population)
