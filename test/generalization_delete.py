from itertools import product
import pandas as pd

df = pd.read_csv("C:/Users/LENOVO/Documents/GitHub/IPF_multidim/input_marginals.csv", delimiter=';')

# Rebuild variable-category-value structure
#df_split = df["variable;category;value"].str.split(";", expand=True)
#df_split.columns = ["variable", "category", "value"]
#df_split["value"] = pd.to_numeric(df_split["value"])

# Create a lookup dictionary
# value_dict = df_split.set_index(["variable", "category"])["value"].to_dict()
total = 6333024

# Identify unique categories per variable
variables = df_split.groupby("variable")["category"].unique().to_dict()

# If we have at least four different variables, pick one category from each to form a combination
if len(variables) < 4:
    result_df = pd.DataFrame([{"error": "Need at least four distinct variables for full generalization"}])
else:
    # Generate all combinations: pick one category per variable
    combinations = list(product(*variables.values()))
    
    results = []
    for combo in combinations:
        # Map combo to variables
        combo_dict = dict(zip(variables.keys(), combo))
        try:
            C1 = value_dict[(list(variables.keys())[0], combo_dict[list(variables.keys())[0]])]
            C2 = value_dict[(list(variables.keys())[1], combo_dict[list(variables.keys())[1]])]
            C3 = value_dict[(list(variables.keys())[2], combo_dict[list(variables.keys())[2]])]
            C4 = value_dict[(list(variables.keys())[3], combo_dict[list(variables.keys())[3]])]

            numerator = ((C1 / total) * ((C2 / total) * C3)) * ((C1 / total) * ((C2 / total) * C4))
            denominator = (C1 / total) * C2
            value = numerator / denominator if denominator != 0 else None

            results.append({
                list(variables.keys())[0]: combo_dict[list(variables.keys())[0]],
                list(variables.keys())[1]: combo_dict[list(variables.keys())[1]],
                list(variables.keys())[2]: combo_dict[list(variables.keys())[2]],
                list(variables.keys())[3]: combo_dict[list(variables.keys())[3]],
                "value": value
            })
        except KeyError:
            continue

    result_df = pd.DataFrame(results)

import ace_tools as tools; tools.display_dataframe_to_user(name="Generalized Formula Results", dataframe=result_df)
