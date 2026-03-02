import os
import sys
import argparse
from itertools import product
from collections import defaultdict

import pandas as pd
import numpy as np


def syntheticextraction(df_tuples, target_components, display_mode='split', synth_total=None):
    """
    Perform synthetic population extraction using IPF-style probability construction.

    Args:
        df_tuples: DataFrame with columns for each dimension (e.g., gender, age, hpt, hf) and 'value'
        target_components: ["all"] OR list/tuple with length = #dimensions, using None for "any"
        display_mode: 'split' (default) shows all combinations, 'aggregate' sums unspecified dimensions
        synth_total: optional int target population size (only applied meaningfully for -f all).
                     If provided, counts are allocated to sum EXACTLY to synth_total using
                     the Hamilton / largest remainder method.
    """

    # Get dimension columns (all except 'value')
    dimension_cols = [col for col in df_tuples.columns if col != 'value']

    # Compute total population from first dimension's marginal only
    # Find rows with exactly one non-NA dimension
    marginal_mask = df_tuples[dimension_cols].notna().sum(axis=1) == 1
    
    totals = []
    totals_by_dim = {}
    
    for dim in dimension_cols:
        dim_marginals = df_tuples[marginal_mask & df_tuples[dim].notna()]
        if len(dim_marginals) > 0:
            dim_total = float(dim_marginals["value"].sum())
        if dim_total > 0:
            totals.append(dim_total)
            totals_by_dim[dim] = dim_total
    
    if len(totals) == 0:
        raise ValueError("Could not infer a valid total population from marginals (no positive marginal totals).")
        
    avg_total = float(np.mean(totals))
    total_population = int(round(avg_total))
    
    if total_population <= 0:
        raise ValueError("Could not infer a valid total population from marginals (average total <= 0).")
    
    
#    marginal_mask = df_tuples[dimension_cols].notna().sum(axis=1) == 1

#    total_population = None
#    for dim in dimension_cols:
#        dim_marginals = df_tuples[marginal_mask & df_tuples[dim].notna()]
#        if len(dim_marginals) > 0:
#            total_population = int(dim_marginals['value'].sum())
#            break

#    if total_population is None or total_population <= 0:
#        raise ValueError("Could not infer a valid total population from marginals (sum <= 0).")

    # Separate marginal and joint distributions
    df_tuples = df_tuples.copy()
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
                marginal_lookup[(dim, category)] = float(row['value'])
                if category not in marginal_groups[dim]:
                    marginal_groups[dim].append(category)

    # Determine which dimensions we're working with
    variables = [dim for dim in dimension_cols if dim in marginal_groups]

    if len(variables) == 0:
        raise ValueError("No marginal groups found. Check that your input has valid marginals.")

    # Build all possible combinations (full joint grid)
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
            joint_distributions.setdefault(dims_tuple, {})[cats_tuple] = float(row['value'])

    # Group joints by base (first dimension)
    joint_groups_by_base = defaultdict(list)
    for joint_dims in joint_distributions:
        if len(joint_dims) >= 2:
            base = joint_dims[0]
            joint_groups_by_base[base].append(joint_dims)

    # Determine filter mode for target_components
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

    # --------------------------
    # Main probability construction
    # --------------------------
    rows = []
    for combo in all_combinations:
        combo_dict = dict(zip(variables, combo))
        estimate = 1.0
        used_vars = set()
        used_joints = []

        # Apply joint distributions using conditional probabilities
        for base_var, joint_list in joint_groups_by_base.items():
            base_val = combo_dict.get(base_var)
            base_count = marginal_lookup.get((base_var, base_val), None)

            if base_val is not None and base_count and base_count > 0:
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
                val = marginal_lookup.get((var, combo_dict[var]), 0.0)
                estimate *= (val / total_population) if total_population > 0 else 0.0

        rows.append({
            'combination': '_'.join(combo),
            'variables': '_'.join(variables),
            'raw_estimate': float(estimate),
            'weights_joints': ', '.join(sorted(set(used_joints))) if used_joints else 'none'
        })

    results_df = pd.DataFrame(rows)

    # --------------------------
    # Allocate integer counts
    # - default: sum to inferred total_population
    # - if synth_total is set: sum EXACTLY to synth_total (Hamilton / largest remainder)
    # --------------------------
    target_total = int(synth_total) if synth_total is not None else int(total_population)
    if target_total < 0:
        raise ValueError("--synth-total must be >= 0")

    w = results_df["raw_estimate"].to_numpy(dtype=float)
    w_sum = float(w.sum())
    if w_sum <= 0:
        raise ValueError("All estimated weights are zero; cannot allocate counts.")

    scaled = (w / w_sum) * target_total
    floors = np.floor(scaled).astype(int)
    remainder = target_total - int(floors.sum())

    frac = scaled - floors
    order_desc = np.argsort(-frac)  # descending

    if remainder > 0:
        floors[order_desc[:remainder]] += 1
    elif remainder < 0:
        # rare: remove from smallest fractional parts
        order_asc = np.argsort(frac)
        floors[order_asc[:(-remainder)]] -= 1
        floors = np.maximum(floors, 0)

    results_df["estimated_count"] = floors
    results_df = results_df.drop(columns=["raw_estimate"])

    # --------------------------
    # Filtering / output conversion to tuple-format
    # --------------------------
    if filter_mode == "tuple":
        def match_tuple(combo_str: str) -> bool:
            parts = combo_str.split('_')
            if len(parts) != len(target_components):
                return False
            for target, actual in zip(target_components, parts):
                if target is not None and str(target) != actual:
                    return False
            return True

        matching_rows = results_df[results_df['combination'].apply(match_tuple)]
        total_est = int(matching_rows['estimated_count'].sum())

        # Convert to tuple format matching input structure
        output_rows = []
        for _, row in matching_rows.iterrows():
            parts = row['combination'].split('_')
            tuple_row = {dim: val for dim, val in zip(dimension_cols, parts)}
            tuple_row['value'] = int(row['estimated_count'])
            output_rows.append(tuple_row)

        results_df = pd.DataFrame(output_rows)

        if display_mode == 'aggregate':
            agg_row = {}
            for dim, target in zip(dimension_cols, target_components):
                agg_row[dim] = target if target is not None else ''
            agg_row['value'] = int(total_est)
            results_df = pd.DataFrame([agg_row])

    else:
        # "all" mode, return full joint in tuple format
        output_rows = []
        for _, row in results_df.iterrows():
            parts = row['combination'].split('_')
            tuple_row = {dim: val for dim, val in zip(dimension_cols, parts)}
            tuple_row['value'] = int(row['estimated_count'])
            output_rows.append(tuple_row)

        results_df = pd.DataFrame(output_rows)

    return results_df


def parse_filter(filter_str, df_tuples):
    """
    Parse filter string into target_components format.

    Examples:
        "all" -> ["all"]
        "gender:male,age:30" -> ["male", "30", None, None] (assuming 4 dims in file order)
        "age:30,hpt:no,hf:no" -> [None, "30", "no", "no"]
    """
    if filter_str.lower() == "all":
        return ["all"]

    dimension_cols = [col for col in df_tuples.columns if col != 'value']

    filter_dict = {}
    filter_parts = [part.strip() for part in filter_str.split(',') if part.strip()]

    for part in filter_parts:
        if ':' not in part:
            raise ValueError(f"Invalid filter format: '{part}'. Expected 'dimension:value'")

        dim, val = part.split(':', 1)
        dim = dim.strip()
        val = val.strip()

        if dim not in dimension_cols:
            raise ValueError(f"Unknown dimension: '{dim}'. Available dimensions: {', '.join(dimension_cols)}")

        filter_dict[dim] = val

    target_components = [filter_dict.get(dim, None) for dim in dimension_cols]
    return target_components


def compute_rmse(df_tuples, synthetic_df):
    """
    RMSE between observed constraints in df_tuples (value)
    and synthetic_df (value), where synthetic_df is full-joint and
    is aggregated to match each constraint row.
    """
    dimension_cols = [c for c in df_tuples.columns if c not in ("value", "n_active_dims")]

    squared_errors = []

    for _, obs_row in df_tuples.iterrows():
        active_dims = {
            dim: str(obs_row[dim]).strip()
            for dim in dimension_cols
            if pd.notna(obs_row[dim]) and str(obs_row[dim]).strip() != ''
        }

        mask = pd.Series(True, index=synthetic_df.index)
        for dim, val in active_dims.items():
            mask &= synthetic_df[dim].astype(str) == val

        predicted_sum = synthetic_df.loc[mask, "value"].sum()
        observed_value = obs_row["value"]
        squared_errors.append((predicted_sum - observed_value) ** 2)

    return float(np.sqrt(np.mean(squared_errors)))


def _constraint_key_from_row(row, dimension_cols):
    parts = []
    for dim in dimension_cols:
        v = row[dim]
        if pd.notna(v) and str(v).strip() != '':
            parts.append(f"{dim}={str(v).strip()}")
    return ",".join(parts)


def compute_ape(df_tuples, synthetic_df, eps=1e-12):
    """
    APE only for constraints that exist in df_tuples (empirical observables),
    aggregated by unique constraint definition (e.g., gender=male, age=30,hpt=yes).
    """
    dimension_cols = [c for c in df_tuples.columns if c not in ("value", "n_active_dims")]

    if "n_active_dims" not in df_tuples.columns:
        df_tuples = df_tuples.copy()
        df_tuples["n_active_dims"] = df_tuples[dimension_cols].notna().sum(axis=1)

    rows = []
    for _, obs_row in df_tuples.iterrows():
        active_dims = {
            dim: str(obs_row[dim]).strip()
            for dim in dimension_cols
            if pd.notna(obs_row[dim]) and str(obs_row[dim]).strip() != ''
        }

        mask = pd.Series(True, index=synthetic_df.index)
        for dim, val in active_dims.items():
            mask &= synthetic_df[dim].astype(str) == val

        predicted = float(synthetic_df.loc[mask, "value"].sum())
        observed = float(obs_row["value"])

        rows.append({
            "constraint": _constraint_key_from_row(obs_row, dimension_cols),
            "observed": observed,
            "predicted": predicted
        })

    ape_df = (
        pd.DataFrame(rows)
        .groupby(["constraint"], as_index=False)
        .agg(observed=("observed", "sum"), predicted=("predicted", "sum"))
    )

    ape_df["avg_percentage_err"] = np.where(
        np.abs(ape_df["observed"]) > eps,
        np.abs(ape_df["predicted"] - ape_df["observed"]) / ape_df["observed"] * 100.0,
        np.nan
    )
    ape_df["avg_percentage_err"] = ape_df["avg_percentage_err"].round(8)

    return ape_df


def main():
    parser = argparse.ArgumentParser(
        description='Synthetic population extraction using IPF algorithm',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python synthpopgen.py -i input_file_tuples.csv -f all -o output.csv
  python synthpopgen.py -i input_file_tuples.csv -f "age:30,hpt:no,hf:no" -d split
  python synthpopgen.py -i input_file_tuples.csv -f "gender:male,age:30,hf:yes" -d aggregate

  # Validation (default basename "validation"):
  python synthpopgen.py -i input_file_tuples.csv -f all --validate

  # Validation with custom basename:
  python synthpopgen.py -i input_file_tuples.csv -f all --validate myrun

  # Exact synthetic population size (full joint only):
  python synthpopgen.py -i input_file_tuples.csv -f all --synth-total 50000 -o output.csv
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
             '"aggregate": sum up unspecified dimensions into a single row with empty values for those dimensions.'
    )

    # Validation can be:
    # - omitted => None
    # - --validate => "validation"
    # - --validate BASENAME => "BASENAME"
    parser.add_argument(
        '-v', '--validate',
        nargs='?',
        const='validation',
        default=None,
        metavar='BASENAME',
        help='Run validation (RMSE + APE). If no basename is provided, uses "validation". '
             'Validation is allowed only when -f "all".'
    )

    parser.add_argument(
        '--synth-total',
        type=int,
        default=None,
        help='Target size of the synthetic population. If set, output counts sum EXACTLY to this value. '
             'Supported only with -f "all".'
    )

    args = parser.parse_args()

    try:
        df_tuples = pd.read_csv(args.input, delimiter=';', dtype=str)
        if 'value' not in df_tuples.columns:
            raise ValueError("Input file must contain a 'value' column.")

        df_tuples['value'] = pd.to_numeric(df_tuples['value'])

        # Guards
        if args.validate is not None and args.filter.lower() != "all":
            print('Error: --validate can only be used together with -f "all".', file=sys.stderr)
            sys.exit(1)

        if args.synth_total is not None and args.filter.lower() != "all":
            print('Error: --synth-total is only supported with -f "all".', file=sys.stderr)
            sys.exit(1)

        # Validation compares to original constraints, so disallow scaling totals for now
        if args.validate is not None and args.synth_total is not None:
            print('Error: --validate cannot be used with --synth-total (constraints are for the original population).', file=sys.stderr)
            sys.exit(1)

        target_components = parse_filter(args.filter, df_tuples)

        synthetic_df = syntheticextraction(
            df_tuples,
            target_components,
            display_mode=args.display,
            synth_total=args.synth_total
        )

        # --- Optional validation ---
        if args.validate is not None:
            rmse = compute_rmse(df_tuples, synthetic_df)
            rmse_df = pd.DataFrame([{
                "metric": "RMSE",
                "value": rmse,
                "n_constraints": len(df_tuples)
            }])

            ape_df = compute_ape(df_tuples, synthetic_df)

            # Write validation files next to output if possible (VRE-friendly)
            base = str(args.validate).strip() if str(args.validate).strip() else "validation"
            base = base.rsplit(".", 1)[0]  # if user passes ".csv", strip it

            out_dir = os.path.dirname(args.output) if args.output else os.getcwd()
            rmse_path = os.path.join(out_dir, f"{base}_RMSE.csv")
            ape_path = os.path.join(out_dir, f"{base}_APE.csv")

            rmse_df.to_csv(rmse_path, index=False, sep=';')
            ape_df["observed"] = ape_df["observed"].round().astype("Int64")
            ape_df["predicted"] = ape_df["predicted"].round().astype("Int64")
            ape_df.to_csv(ape_path, index=False, sep=';')

            print(f"Validation saved to {rmse_path} and {ape_path}", file=sys.stderr)

        # Output results
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
