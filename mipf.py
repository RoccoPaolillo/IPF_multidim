import numpy as np
import pandas as pd

# Load the uploaded file
data = pd.read_csv('C:/Users/rocpa/OneDrive/Documenti/GitHub/IPF_multidim/GIS/data/lazio_ASL_istat/df_range.csv')

def iterative_proportional_fitting(initial_table, target_marginals, tol=1e-6, max_iter=1000):
    """
    Perform Iterative Proportional Fitting (IPF) to adjust an n-dimensional table to given marginals.

    Parameters:
    initial_table (ndarray): The initial contingency table (n-dimensional).
    target_marginals (list of ndarrays): List of target marginal tables.
                                       Each ndarray corresponds to a marginal table.
    tol (float): Tolerance for convergence.
    max_iter (int): Maximum number of iterations.

    Returns:
    ndarray: Adjusted contingency table that matches target marginals.
    """
    table = initial_table.copy()
    num_marginals = len(target_marginals)
    
    for iteration in range(max_iter):
        old_table = table.copy()
        
        # Iteratively update table to match each marginal
        for axis, target_marginal in enumerate(target_marginals):
            
            # Sum along the current axis to find the current marginal
            current_marginal = np.sum(table, axis=tuple(i for i in range(table.ndim) if i != axis))

            # Avoid division by zero, handle cases where the current marginal might be zero
            with np.errstate(divide='ignore', invalid='ignore'):
                adjustment = np.where(current_marginal != 0, target_marginal / current_marginal, 0)

            # Reshape adjustment to match the dimensions of the table
            expand_shape = [1] * table.ndim
            expand_shape[axis] = adjustment.shape[0]
            adjustment = adjustment.reshape(expand_shape)

            table *= adjustment

        # Check for convergence
        if np.allclose(table, old_table, atol=tol):
            print(f"Converged in {iteration + 1} iterations.")
            break
    else:
        print(f"Did not converge within {max_iter} iterations.")

    return table

# Prepare data for IPF example
age_groups = data['eta_range'].unique()
gender_categories = ['fem_r', 'man_r']
hf_categories = ['mar_hfASL', 'mar_nohfASL']
hpt_categories = ['mar_hptfemASL', 'mar_nohptfemASL', 'mar_hptmanASL', 'mar_nohptmanASL']

# Construct initial table (example: age x gender x heart failure x hypertension)
initial_table = np.ones((len(age_groups), len(gender_categories), 2, 2), dtype=float)

# Define target marginals (sampled from the dataset)
marginal_age = data.groupby('classi_eta')[['fem', 'man']].sum().sum(axis=1).values
marginal_gender = data[['fem', 'man']].sum().values
marginal_hf = data[['mar_hfASL', 'mar_nohfASL']].sum().values
marginal_hpt = [data[['mar_hptfemASL', 'mar_nohptfemASL']].sum().values.sum(), 
                data[['mar_hptmanASL', 'mar_nohptmanASL']].sum().values.sum()]

# Apply IPF
adjusted_table = iterative_proportional_fitting(
    initial_table,
    [marginal_age, marginal_gender, marginal_hf, marginal_hpt]
)

# Output
print("Adjusted contingency table:")
print(adjusted_table)
