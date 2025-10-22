import pandas as pd
from synthpopgen import syntheticextraction, parse_filter

def syntheticextraction_flex(df_or_path,
                             target_components,
                             display_mode="split",
                             output_path = "output.csv"):
    """
    Flexible version of syntheticextraction:
    - Accepts either a CSV file path or a DataFrame
    - Accepts either a string filter or a parsed list
    - Automatically writes output to CSV
    """

    # load input
    if isinstance(df_or_path, str):
        df = pd.read_csv(df_or_path, delimiter=";", dtype=str)
        df["value"] = pd.to_numeric(df["value"])
    else:
        df = df_or_path

    # parse filter
    if isinstance(target_components, str):
        target_components = parse_filter(target_components, df)

    # run synthetic extraction
    results_df = syntheticextraction(df, target_components, display_mode)
    print(results_df)
    
    # write csv
    results_df.to_csv(output_path, index=False)

    return results_df

syntheticextraction_flex("input_file_tuples.csv","all",display_mode="aggregate", output_path =  "output_all.csv")