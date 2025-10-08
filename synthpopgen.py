import pandas as pd
from itertools import product
from collections import defaultdict
import argparse
import sys

def syntheticextraction(df_tuples, target_components):
    """
    Perform synthetic population extraction using IPF algorithm.
    
    Args:
        df_tuples: DataFrame with columns for each dimension (gender, age, hpt, hf) and value
        target_components: List of target categories to filter results
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
  
  # Filter for age=30, hpt=no, hf=no (any gender) and save to file
  python synthpopgen.py -i input_file_tuples.csv -f "age:30,hpt:no,hf:no" -o filtered.csv
  
  # Filter for male, age=60-100, hpt=yes (any hf)
  python synthpopgen.py -i input_file_tuples.csv -f "gender:male,age:60100,hpt:yes"
  
  # Filter for female only (all other dimensions)
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
        synthetic_df = syntheticextraction(df_tuples, target_components)
        
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
