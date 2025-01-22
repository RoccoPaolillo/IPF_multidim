import numpy as np
import pandas as pd

ipf_array = pd.read_csv('C:/Users/rocpa/OneDrive/Documenti/GitHub/IPF_multidim/GIS/data/lazio_ASL_istat/df_range.csv')

# Function to perform iterative proportional fitting (IPF) on the 4D array
def ipf_adjustment(array, max_iter=100, tolerance=1e-5):
    # Get the marginal totals (sums across each dimension)
    age_marginals = array.sum(axis=(1, 2, 3))  # sum across gender, hpt, hf for each age
    gender_marginals = array.sum(axis=(0, 2, 3))  # sum across age, hpt, hf for each gender
    hpt_marginals = array.sum(axis=(0, 1, 3))  # sum across age, gender, hf for each hpt status
    hf_marginals = array.sum(axis=(0, 1, 2))  # sum across age, gender, hpt for each health factor

    # Start the IPF algorithm
    for iteration in range(max_iter):
        # Row (age) fitting
        for i in range(array.shape[0]):
            factor = age_marginals[i] / array[i].sum()
            array[i] *= factor
        
        # Gender fitting
        for j in range(array.shape[1]):
            factor = gender_marginals[j] / array[:, j].sum()
            array[:, j] *= factor
        
        # HPT fitting
        for k in range(array.shape[2]):
            factor = hpt_marginals[k] / array[:, :, k].sum()
            array[:, :, k] *= factor
        
        # HF fitting
        for l in range(array.shape[3]):
            factor = hf_marginals[l] / array[:, :, :, l].sum()
            array[:, :, :, l] *= factor
        
        # Check for convergence (if changes are smaller than the tolerance, stop)
        new_marginals = [
            array.sum(axis=(1, 2, 3)),
            array.sum(axis=(0, 2, 3)),
            array.sum(axis=(0, 1, 3)),
            array.sum(axis=(0, 1, 2)),
        ]
        change = np.max([np.abs(new_m - old_m).sum() for new_m, old_m in zip(new_marginals, [age_marginals, gender_marginals, hpt_marginals, hf_marginals])])
        if change < tolerance:
            break
        
        # Update marginals for the next iteration
        age_marginals, gender_marginals, hpt_marginals, hf_marginals = new_marginals

    return array

# Apply IPF to adjust the 4D array
ipf_result = ipf_adjustment(np.copy(ipf_array))

# Display the final adjusted 4D array
ipf_result.shape, ipf_result.sum(axis=(1, 2, 3))  # Check the final sums after adjustment