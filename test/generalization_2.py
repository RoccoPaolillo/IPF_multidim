from itertools import product
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import combinations as it_combinations


def generalized_joint_estimator(df, total_population):
    joint_df = df[df['variable'].str.contains('_')]
    marginals_df = df[~df['variable'].str.contains('_')]

    # Build marginal lookup
    marginal_lookup = dict(zip(zip(marginals_df['variable'], marginals_df['category']), marginals_df['value']))
    marginal_groups = marginals_df.groupby('variable')['category'].apply(list).to_dict()
    variables = list(marginal_groups.keys())
    all_combinations = list(product(*[marginal_groups[v] for v in variables]))

    # Parse joint distributions
    joint_distributions = {}
    for _, row in joint_df.iterrows():
        vars_tuple = tuple(row['variable'].split('_'))
        cats_tuple = tuple(row['category'].split('_'))
        value = row['value']
        joint_distributions.setdefault(vars_tuple, {})[cats_tuple] = value

    # Specifically extract age_hpt and age_hf
    joint_age_hpt = joint_distributions.get(('age', 'hpt'), {})
    joint_age_hf = joint_distributions.get(('age', 'hf'), {})

    results = []
    for combo in all_combinations:
        combo_dict = dict(zip(variables, combo))
        gender = combo_dict.get('gender')
        age = combo_dict.get('age')
        hpt = combo_dict.get('hpt')
        hf = combo_dict.get('hf')

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
            hf_marg = marginal_lookup.get(('hf', hf), 0)
            estimate = (male_val / total_population) * age_val * (
                (hpt_joint_val / age_val) * (hf_marg / total_population)
            )
            used_joint = "age_hpt"
        elif hf_joint_val is not None and age_val > 0:
            hpt_marg = marginal_lookup.get(('hpt', hpt), 0)
            estimate = (male_val / total_population) * age_val * (
                (hf_joint_val / age_val) * (hpt_marg / total_population)
            )
            used_joint = "age_hf"
        else:
            estimate = 1.0
            for var in variables:
                val = marginal_lookup.get((var, combo_dict[var]), 0)
                estimate *= val / total_population
            estimate *= total_population
            used_joint = "none"

        results.append({
            'combination': combo,
            'estimated_count': round(estimate),
            'used_joints': used_joint
        })

    return pd.DataFrame(results)


df = pd.read_csv("C:/Users/LENOVO/Documents/GitHub/IPF_multidim/input_marginals.csv", delimiter=';')
total_population = 6333024
results_generalized = generalized_joint_estimator(df, total_population)
