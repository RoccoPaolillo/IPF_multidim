import mesa
import pandas as pd

# class agents initialization
# **attrs dictionary from df_agents key, value
class PersonAgent(mesa.Agent):
    def __init__(self, model, **attrs):
        super().__init__(model)
        for k, v in attrs.items():
            setattr(self, k, v)

# for future schedule activation (not activated)
    def step(self):
        pass

# model initialization
class PopulationModel(mesa.Model):
    def __init__(self, output_csv: str, sep=";"):
        super().__init__()

# read pdf and consider all variables as string except "value" integer
        df = pd.read_csv(output_csv, sep=sep, dtype=str)
        df["value"] = df["value"].astype(int)

# to expand the output csv. repeat the index of each row for how many "values", 
# to expand to the number of agents to be initiated for each crossed category by row
        df_agents = (
            df.loc[df.index.repeat(df["value"])]
              .drop(columns=["value"])
              .reset_index(drop=True)
        )
        

        # Keep the list of characteristics (all columns become agent attrs)
        self.char_cols = list(df_agents.columns)

        # initialization of each agent with characteristics from df_agents
        PersonAgent.from_dataframe(self, df_agents)

        # ---- Reporter: counts for each joint combination of all characteristics ----
        def cross_counts(model):
            # Convert agents -> rows 
            rows = [
                {c: getattr(a, c) for c in model.char_cols}
                for a in model.agents
            ]
            g = (
                pd.DataFrame(rows)
                  .groupby(model.char_cols, dropna=False)
                  .size()
            )

            # Return as dict with readable keys
            # key like "age=3060|hpt=yes|hf=no|gender=male"
            out = {
                "|".join(f"{col}={val}" for col, val in zip(model.char_cols, idx)): int(cnt)
                for idx, cnt in g.items()
            }
            return out

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "N": lambda m: len(m.agents),
                "cross_counts": cross_counts
            }
        )

        # collect at t=0
        self.datacollector.collect(self)

    def step(self):
        # actual scheduler of agents' actions (inactive)
        self.agents.shuffle_do("step")
        # to collect output from the model
        self.datacollector.collect(self)


### To run the actual model
# model initialized with output.csv (df_agents in the code)    
# NOTE! The script is already set to use "output.csv" as external file generated from the SPG service
# You can set to another file
model = PopulationModel("output.csv", sep=";")
# model.run_for(2) # to execute 3 runs (0,1,2)  
# to collect report     
model_vars = model.datacollector.get_model_vars_dataframe()

# to extract a tidy table for visualization
rows = []
for step, d in model_vars["cross_counts"].items():
    for profile, count in d.items():
        rows.append({"step": step, "profile": profile, "count": count})

cross_df = pd.DataFrame(rows)

