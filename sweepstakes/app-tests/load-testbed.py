import pandas as pd

def get_tournament_list(file_path):
    try:
        # 1. Load the JSON
        with open(file_path, 'r') as f:
            df = pd.read_json(f, orient='index', convert_dates=False) 
            # 'orient=index' ensures your IDs (like 401811937) become the rows

        # Force the index to be numeric, then back to string for the GUI
        df.index = pd.to_numeric(df.index, errors='coerce').astype(int).astype(str)

        # 2. Get the IDs for the dropdown
        tournament_ids = df.index.tolist()
        
        # 3. (Optional) Create a list of "Friendly Names" for the dropdown
        # e.g., "THE PLAYERS Championship (401811937)"
        friendly_names = []
        for tourn_id, row in df.iterrows():
            name = row['tournamentFullName']
            friendly_names.append(f"{name} ({tourn_id})")
            
        print(friendly_names)
        print(df)
    
    except Exception as e:
        print(f"Error: {e}")
        return [], None
    
get_tournament_list('../control/gui-save.json')