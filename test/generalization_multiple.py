import pandas as pd
from itertools import product
from collections import defaultdict

def generalized_joint_estimator_flexible_base(df, total_population):
    from itertools import product
    from collections import defaultdict

    joint_df = df[df['variable'].str.contains('_')]
    marginals_df = df[~df['variable'].str.contains('_')]

    marginal_lookup = dict(zip(zip(marginals_df['variable'], marginals_df['category']), marginals_df['value']))
    marginal_groups = marginals_df.groupby('variable')['category'].apply(list).to_dict()
    variables = list(marginal_groups.keys())
    all_combinations = list(product(*[marginal_groups[v] for v in variables]))

    joint_distributions = {}
    for _, row in joint_df.iterrows():
        vars_tuple = tuple(row['variable'].split('_'))
        cats_tuple = tuple(row['category'].split('_'))
        value = row['value']
        joint_distributions.setdefault(vars_tuple, {})[cats_tuple] = value

    # Allow joints of length >= 2, grouped by base (first variable)
    joint_groups_by_base = defaultdict(list)
    for joint_vars in joint_distributions:
        if len(joint_vars) >= 2:
            base = joint_vars[0]
            joint_groups_by_base[base].append(joint_vars)

    results = []

    for combo in all_combinations:
        combo_dict = dict(zip(variables, combo))
        estimate = 1.0
        used_vars = set()
        used_joints = []

        for base_var, joint_list in joint_groups_by_base.items():
            base_val = combo_dict.get(base_var)
            base_count = marginal_lookup.get((base_var, base_val), None)
            if base_val is not None and base_count:
                conditional_product = 1.0
                joint_conditional_used = False
                for joint_vars in joint_list:
                    joint_cats = tuple(combo_dict.get(v) for v in joint_vars)
                    joint_val = joint_distributions[joint_vars].get(joint_cats, None)
                    if joint_val is not None:
                        conditional_product *= joint_val / base_count
                        used_vars.update(joint_vars)
                        used_joints.append('_'.join(joint_vars))
                        joint_conditional_used = True
                if joint_conditional_used:
                    estimate *= (base_count / total_population) * conditional_product

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
results_generalized = generalized_joint_estimator_flexible_base(df, total_population)