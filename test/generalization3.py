import pandas as pd
from itertools import product
from collections import defaultdict

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

    # Group joint distributions by shared base variable (only 2-way for now)
    joint_groups_by_base = defaultdict(list)
    for joint_vars in joint_distributions:
        if len(joint_vars) == 2:
            base, dependent = joint_vars
            joint_groups_by_base[base].append((base, dependent))

    results = []
    for combo in all_combinations:
        combo_dict = dict(zip(variables, combo))
        estimate = 1.0
        used_vars = set()
        used_joints = []

        # First, apply joint groups sharing the same base
        for base_var, joint_list in joint_groups_by_base.items():
            base_val = combo_dict.get(base_var)
            base_count = marginal_lookup.get((base_var, base_val), None)

            if base_val is not None and base_count:
                # Apply each joint conditional on base
                joint_conditional_used = False
                conditional_product = 1.0
                for joint_vars in joint_list:
                    _, dep_var = joint_vars
                    dep_val = combo_dict.get(dep_var)
                    joint_val = joint_distributions[joint_vars].get((base_val, dep_val), None)

                    if joint_val is not None:
                        conditional_product *= joint_val / base_count
                        used_vars.update(joint_vars)
                        used_joints.append('_'.join(joint_vars))
                        joint_conditional_used = True

                if joint_conditional_used:
                    estimate *= (base_count / total_population) * conditional_product

        # Multiply marginals for any variables not yet used
        for var in variables:
            if var not in used_vars:
                val = marginal_lookup.get((var, combo_dict[var]), 0)
                estimate *= val / total_population

        results.append({
            'combination': combo,
            'estimated_count': round(estimate * total_population),
            'used_joints': ', '.join(sorted(set(used_joints))) if used_joints else 'none'
        })

    return pd.DataFrame(results)

df = pd.read_csv("C:/Users/LENOVO/Documents/GitHub/IPF_multidim/input_marginals.csv", delimiter=';')
total_population = 6333024
results_generalized = generalized_joint_estimator(df, total_population)