import pandas as pd
from itertools import product
from collections import defaultdict
import argparse
import sys

def syntheticextraction(df_tuples, target_components, display_mode='split'):
    """
    Perform synthetic population extraction using IPF algorithm.
    
    Args:
        df_tuples: DataFrame with columns for each dimension (gender, age, hpt, hf) and value
        target_components: List of target categories to filter results
        display_mode: 'split' (default) shows all combinations, 'aggregate' sums unspecified dimensions
    """

    # Get dimension columns (all except 'value')
    dimension_cols = [col for col in df_tuples.columns if col != 'value']
    
    # Compute total population from first dimension's marginal only
    # Find rows with exactly one non-NA dimension
    marginal_mask = df_tuples[dimension_cols].notna().sum(axis=1) == 1
    
    # Get the first dimension that has marginals
    for dim in dimension_cols:
        dim_marginals = df_tuples[marginal_mask & df_tuples[dim].notna()]
        if len(dim_marginals) > 0:
            total_population = int(dim_marginals['value'].sum())
            break
    
    # Separate marginal and joint distributions
    # Marginals: exactly one dimension is non-empty
    # Joints: two or more dimensions are non-empty
    df_tuples['n_active_dims'] = df_tuples[dimension_cols].notna().sum(axis=1)
    marginals = df_tuples[df_tuples['n_active_dims'] == 1].copy()
    joints = df_tuples[df_tuples['n_active_dims'] >= 2].copy()
    
    # Build marginal lookup: {(dimension, category): value}
    marginal_lookup = {}
    marginal_groups = defaultdict(list)
    
    for _, row in marginals.iterrows():
        for dim in dimension_cols:
            val = row[dim]
            if pd.notna(val) and str(val).strip() != '':
                category = str(val).strip()
                marginal_lookup[(dim, category)] = row['value']
                if category not in marginal_groups[dim]:
                    marginal_groups[dim].append(category)
    
    # Determine which dimensions we're working with
    variables = [dim for dim in dimension_cols if dim in marginal_groups]
    
    # Build all possible combinations
    all_combinations = list(product(*[marginal_groups[v] for v in variables]))
    
    # Build joint distributions: {(dim1, dim2, ...): {(cat1, cat2, ...): value}}
    joint_distributions = {}
    
    for _, row in joints.iterrows():
        active_dims = []
        active_cats = []
        
        for dim in dimension_cols:
            val = row[dim]
            if pd.notna(val) and str(val).strip() != '':
                active_dims.append(dim)
                active_cats.append(str(val).strip())
        
        if len(active_dims) >= 2:
            dims_tuple = tuple(active_dims)
            cats_tuple = tuple(active_cats)
            joint_distributions.setdefault(dims_tuple, {})[cats_tuple] = row['value']
    
    # Group joints by base (first dimension)
    joint_groups_by_base = defaultdict(list)
    for joint_dims in joint_distributions:
        if len(joint_dims) >= 2:
            base = joint_dims[0]
            joint_groups_by_base[base].append(joint_dims)
    
    # Determine filter mode for target_components
    # Check if target_components is a tuple/list matching dimensions (can include None for "any")
    if isinstance(target_components, (list, tuple)) and len(target_components) == len(variables):
        filter_mode = "tuple"
    elif target_components == ["all"]:
        filter_mode = "all"
    else:
        raise ValueError(
            f"target_components must be either ['all'] or a tuple matching dimensions: [{', '.join(variables)}].\n"
            f"Got: {target_components}\n"
            f"Use None for dimensions you don't want to constrain.\n"
            f"Example: [None, '30', 'no', 'no'] for age=30, hpt=no, hf=no, any gender"
        )
    
    # Main IPF calculation

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
        
        # Apply joint distributions using conditional probabilities
        for base_var, joint_list in joint_groups_by_base.items():
            base_val = combo_dict.get(base_var)
            base_count = marginal_lookup.get((base_var, base_val), None)
            
            if base_val is not None and base_count:
                conditional_product = 1.0
                joint_conditional_used = False
                
                for joint_dims in joint_list:
                    joint_cats = tuple(combo_dict.get(dim) for dim in joint_dims)
                    joint_val = joint_distributions[joint_dims].get(joint_cats, None)
                    
                    if joint_val is not None:
                        # Conditional probability: P(joint) / P(base)
                        conditional_product *= joint_val / base_count
                        used_vars.update(joint_dims)
                        used_joints.append('_'.join(joint_dims))
                        joint_conditional_used = True
                
                if joint_conditional_used:
                    # Multiply by base probability and conditional product
                    estimate *= (base_count / total_population) * conditional_product
        
        # Apply remaining marginal probabilities for unused variables
        for var in variables:
            if var not in used_vars:
                val = marginal_lookup.get((var, combo_dict[var]), 0)
                estimate *= val / total_population
        
        results.append({
            'combination': '_'.join(combo),
            'variables': '_'.join(variables),
            'estimated_count': round(estimate * total_population),
            'weights_joints': ', '.join(sorted(set(used_joints))) if used_joints else 'none'
        })

# from here the output preparation
    
    results_df = pd.DataFrame(results)
    
    # Apply filtering based on target_components
    if filter_mode == "tuple":
        # Filter by matching specific dimensions (None means "any value")
        def match_tuple(combo_str: str) -> bool:
            parts = combo_str.split('_')
            if len(parts) != len(target_components):
                return False
            for i, (target, actual) in enumerate(zip(target_components, parts)):
                if target is not None and str(target) != actual:
                    return False
            return True
        
        matching_rows = results_df[results_df['combination'].apply(match_tuple)]
        total_est = int(matching_rows['estimated_count'].sum())
        
        # Create label showing only non-None components
        label_parts = [f"{variables[i]}={target}" for i, target in enumerate(target_components) if target is not None]
        
        # Convert to tuple format matching input structure
        output_rows = []
        for _, row in matching_rows.iterrows():
            parts = row['combination'].split('_')
            tuple_row = {dim: val for dim, val in zip(dimension_cols, parts)}
            tuple_row['value'] = row['estimated_count']
            output_rows.append(tuple_row)
        
        results_df = pd.DataFrame(output_rows)
        
        # Apply display mode
        if display_mode == 'aggregate':
            # For aggregate mode, set unspecified dimensions to empty and sum values
            agg_row = {}
            for i, (dim, target) in enumerate(zip(dimension_cols, target_components)):
                if target is not None:
                    agg_row[dim] = target
                else:
                    agg_row[dim] = ''
            agg_row['value'] = total_est
            results_df = pd.DataFrame([agg_row])
    else:
        # For "all" mode, convert results to tuple format matching input structure
        output_rows = []
        for _, row in results_df.iterrows():
            parts = row['combination'].split('_')
            tuple_row = {dim: val for dim, val in zip(dimension_cols, parts)}
            tuple_row['value'] = row['estimated_count']
            output_rows.append(tuple_row)
        
        results_df = pd.DataFrame(output_rows)
    
    return results_df

def parse_filter(filter_str, df_tuples):
    """
    Parse filter string into target_components format.
    
    Args:
        filter_str: Filter specification string
            - "all": Generate all combinations
            - "dimension1:value1,dimension2:value2": Filter by specific dimension:value pairs
              Omitted dimensions default to "any" (None)
        df_tuples: DataFrame to extract dimension information from
    
    Returns:
        List of target components in tuple format [val1, val2, ...] with None for "any"
    
    Examples:
        "all" -> ["all"]
        "gender:male,age:30" -> ["male", "30", None, None] (assuming 4 dimensions)
        "age:30,hpt:no,hf:no" -> [None, "30", "no", "no"]
    """
    if filter_str.lower() == "all":
        return ["all"]
    
    # Get dimension columns from dataframe
    dimension_cols = [col for col in df_tuples.columns if col != 'value']
    
    # Parse comma-separated dimension:value pairs
    filter_dict = {}
    filter_parts = [part.strip() for part in filter_str.split(',')]
    
    for part in filter_parts:
        if ':' not in part:
            raise ValueError(f"Invalid filter format: '{part}'. Expected 'dimension:value'")
        
        dim, val = part.split(':', 1)
        dim = dim.strip()
        val = val.strip()
        
        if dim not in dimension_cols:
            raise ValueError(f"Unknown dimension: '{dim}'. Available dimensions: {', '.join(dimension_cols)}")
        
        filter_dict[dim] = val
    
    # Build target_components as tuple matching dimension order (None for omitted)
    target_components = [filter_dict.get(dim, None) for dim in dimension_cols]
    return target_components

def main():
    """
    Main function to handle command-line arguments and run synthetic extraction.
    """
    parser = argparse.ArgumentParser(
        description='Synthetic population extraction using IPF algorithm',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate full synthetic population to stdout
  python synthpopgen.py -i input_file_tuples.csv -f all
  
  # Generate full synthetic population to file
  python synthpopgen.py -i input_file_tuples.csv -f all -o output.csv
  
  # Filter for age=30, hpt=no, hf=no (any gender) - split mode (default)
  python synthpopgen.py -i input_file_tuples.csv -f "age:30,hpt:no,hf:no" -d split
  
  # Filter for male, age=30, hf=yes (any hpt) - aggregate mode (sum into one row)
  python synthpopgen.py -i input_file_tuples.csv -f "gender:male,age:30,hf:yes" -d aggregate
  
  # Filter for female only - split mode shows all combinations
  python synthpopgen.py -i input_file_tuples.csv -f "gender:female" -o female_results.csv
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input CSV file in tuple format (mandatory)'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=False,
        default=None,
        help='Output CSV file (optional, prints to stdout if not specified)'
    )
    
    parser.add_argument(
        '-f', '--filter',
        required=False,
        default='all',
        help='Filter specification (optional, defaults to "all"). '
             'Use "all" for full population, or comma-separated dimension:value pairs. '
             'Omitted dimensions default to "any". '
             'Example: "gender:male,age:30,hpt:no" or "age:60100"'
    )
    
    parser.add_argument(
        '-d', '--display',
        required=False,
        default='split',
        choices=['split', 'aggregate'],
        help='Display mode (optional, defaults to "split"). '
             '"split": show all combinations of unspecified dimensions (multiple rows). '
             '"aggregate": sum up unspecified dimensions into a single row with empty values for those dimensions. '
             'Example with -f "gender:male,age:30,hf:yes": '
             'split shows 2 rows (hpt:yes and hpt:no), aggregate shows 1 row with empty hpt.'
    )
    
    args = parser.parse_args()
    
    try:
        # Read the tuple-based CSV file directly
        # Use dtype=str to preserve string values and avoid float conversion
        df_tuples = pd.read_csv(args.input, delimiter=';', dtype=str)
        
        # Convert value column to numeric
        df_tuples['value'] = pd.to_numeric(df_tuples['value'])
        
        # Parse filter argument into target_components
        target_components = parse_filter(args.filter, df_tuples)
        
        # Run synthetic extraction
        synthetic_df = syntheticextraction(df_tuples, target_components, display_mode=args.display)
        
        # Output results in tuple format (semicolon-delimited, matching input format)
        if args.output:
            synthetic_df.to_csv(args.output, index=False, sep=';')
            print(f"Results saved to {args.output}", file=sys.stderr)
        else:
            print(synthetic_df.to_csv(index=False, sep=';'))

    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
os.chdir("C:/Users/LENOVO/Documents/GitHub/IPF_multidim/")
df = pd.read_csv("test/input_file.csv", delimiter=';')
synthetic_df = syntheticextraction(df, target_components = ["hfno","hptno","age30"]) # "age30","hfno","hptno" "all"

