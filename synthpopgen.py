import pandas as pd
from itertools import product
from collections import defaultdict
import os

def syntheticextraction(df, target_components):
    from itertools import product
    from collections import defaultdict
    
    # total population computed as sum of categories first variable (assuming sample from same population)
    total_population = int(df[df['variable'] == df["variable"].unique()[0]]["value"].sum())

    # identify what joint distribution used for correction exist (separated by _) or marginals
    joint_df = df[df['variable'].str.contains('_')]
    marginals_df = df[~df['variable'].str.contains('_')]

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
                        # for each known joint distribution combination, compute conditional probability (HPT30 / AGE30)
                        conditional_product *= joint_val / base_count
                        used_vars.update(joint_vars)
                        used_joints.append('_'.join(joint_vars))
                        joint_conditional_used = True
                if joint_conditional_used:
                    # conditional product multiplied by probability reference level (AGE/POPULATION * (HPT30/AGE30))
                    estimate *= (base_count / total_population) * conditional_product

        for var in variables:
            if var not in used_vars:
                val = marginal_lookup.get((var, combo_dict[var]), 0)
                # updates again the estimate for each combination by the probability of remaining marginals
                # (MALE/population) * (AGE30/population) * (HPT30/AGE30)
                estimate *= val / total_population
        
        results.append({
            'combination': '_'.join(combo),
            'variables': '_'.join(variables),
            # the actual estimates multiplying the probabilities computed by the amount of the population
            'estimated_count': round(estimate * total_population),
            # meaning what known joint weights have been used
            'weights_joints': ', '.join(sorted(set(used_joints))) if used_joints else 'none'
        })
        
        results_df = pd.DataFrame(results)
        
        if target_components == ["all"]:
            results_df.to_csv('syntheticpopulation.csv', index=False)
        else:
            component_sums = defaultdict(float)

            # Loop through each row
            for _, row in results_df.iterrows():
                components = row['combination'].split('_')
                for component in components:
                    component_sums[component] += row['estimated_count']

            # Convert to a DataFrame for readability
            result_df = pd.DataFrame(component_sums.items(), columns=['component', 'total_estimated_count'])
            result_df = result_df.sort_values(by='total_estimated_count', ascending=False)
            result_df['total_estimated_count'] = result_df['total_estimated_count'].astype(int)


            # Filter rows where all target components are present
            mask = results_df['combination'].apply(lambda x: all(comp in x.split('_') for comp in target_components))
            matching_rows = results_df[mask]

            # Calculate total
            filtered_df = matching_rows['estimated_count'].sum()
            filtered_df = pd.DataFrame([{'combination': '_'.join(target_components) ,'estimated_count': filtered_df}])
            filtered_df.to_csv("filtered_synthetic.csv", index=False)
        
   
    return results_df

os.chdir("C:/Users/LENOVO/Documents/GitHub/IPF_multidim/")
df = pd.read_csv("input_file.csv", delimiter=';')
synthetic_df = syntheticextraction(df, target_components = ["all"])
# synthetic_df = syntheticextraction(df, target_components = ["male","hptyes"])