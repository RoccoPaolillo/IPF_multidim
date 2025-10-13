import pandas as pd
from itertools import product
from collections import defaultdict
import os

def syntheticextraction(df, target_components):
    from itertools import product
    from collections import defaultdict

    # total population computed as sum of categories of the first variable
    total_population = int(df[df['variable'] == df["variable"].unique()[0]]["value"].sum())

    # identify joint and marginal distributions
    joint_df = df[df['variable'].str.contains('_')]
    marginals_df = df[~df['variable'].str.contains('_')]

    # Determine whether target_components are variables or categories
    variables_set = set(df["variable"])
    categories_set = set(df["category"])

    # Activate modality "all", "variable" or "category" based
    if target_components == ["all"]:
        filter_mode = "all"
    elif all(comp in variables_set for comp in target_components):
        filter_mode = "variable"
    elif all(
        # allow composite tokens like "age30_hptyes" by checking that at least one
        # subtoken exists in categories_set; the precise matching is done later
        any(sub in categories_set for sub in comp.split('_'))
        for comp in target_components
    ):
        filter_mode = "category"
    else:
        raise ValueError(
            "target_components must all be variables, all categories (composite allowed, e.g. 'age30_hptyes'), or ['all']."
        )

    # --- FILTERING based on target_components ---
    if filter_mode == "variable":
        # Filter marginals to only the selected variables
        marginals_df = marginals_df[marginals_df['variable'].isin(target_components)].copy()

        # Filter joints where any part of the joint variable name is in target_components
        def joint_filter(var):
            return any(v in target_components for v in var.split('_'))

        joint_df = joint_df[joint_df['variable'].apply(joint_filter)].copy()

    # identify all possible combinations
    marginal_lookup = dict(zip(zip(marginals_df['variable'], marginals_df['category']), marginals_df['value']))
    marginal_groups = marginals_df.groupby('variable')['category'].apply(list).to_dict()
    variables = list(marginal_groups.keys())
    all_combinations = list(product(*[marginal_groups[v] for v in variables]))

    # joint distributions used for conditional probability (equivalent to marginals empirical for cross-category in IPF)
    joint_distributions = {}
    for _, row in joint_df.iterrows():
        vars_tuple = tuple(row['variable'].split('_'))
        cats_tuple = tuple(row['category'].split('_'))
        value = row['value']
        joint_distributions.setdefault(vars_tuple, {})[cats_tuple] = value

    # Allow joints of length >= 2, grouped categories by base (first variable)
    joint_groups_by_base = defaultdict(list)
    for joint_vars in joint_distributions:
        if len(joint_vars) >= 2:
            base = joint_vars[0]
            joint_groups_by_base[base].append(joint_vars)
            
# from here the actual algorithm
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
                        # for each known joint distribution combination, compute conditional probability (e.g., HPT30 / AGE30)
                        conditional_product *= joint_val / base_count
                        used_vars.update(joint_vars)
                        used_joints.append('_'.join(joint_vars))
                        joint_conditional_used = True
                if joint_conditional_used:
                    # conditional product multiplied by probability reference level (AGE/POP * (HPT30/AGE30))
                    estimate *= (base_count / total_population) * conditional_product

        for var in variables:
            if var not in used_vars:
                val = marginal_lookup.get((var, combo_dict[var]), 0)
                # multiply by remaining marginals as probabilities
                estimate *= val / total_population

        results.append({
            'combination': '_'.join(combo),
            'variables': '_'.join(variables),
            'estimated_count': round(estimate * total_population),
            'weights_joints': ', '.join(sorted(set(used_joints))) if used_joints else 'none'
        })

# from here the output preparation
    
    results_df = pd.DataFrame(results)

    if filter_mode == "category":
        # Expand composite target components like "age30_hptyes" -> ["age30","hptyes"]
        expanded_targets = [comp.split('_') for comp in target_components]

        def match_combo(combo_str: str) -> bool:
            parts = combo_str.split('_')
            # each group of sub-components must all be present
            return all(all(sub in parts for sub in group) for group in expanded_targets)

        matching_rows = results_df[results_df['combination'].apply(match_combo)]
        total_est = int(matching_rows['estimated_count'].sum())

        filtered_df = pd.DataFrame([{
            'combination': '_'.join(target_components),
            'estimated_count': total_est
        }])
        filtered_df.to_csv("filtered_synthetic.csv", index=False)
    else:
        results_df.to_csv('syntheticpopulation.csv', index=False)

    return results_df

os.chdir("C:/Users/LENOVO/Documents/GitHub/IPF_multidim/")
df = pd.read_csv("input_file_old.csv", delimiter=';')
synthetic_df = syntheticextraction(df, target_components = ["age30","male"])

