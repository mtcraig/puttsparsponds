import pandas as pd
import json

def load_active_save(file_path):
    try:
        # 1. Use the standard json library to load the file
        # This keeps the IDs exactly as they are in the JSON (usually strings)
        with open(file_path, 'r') as f:
            raw_data = json.load(f)
        
        # 2. Convert that dictionary into a Pandas DataFrame
        # 'orient="index"' ensures your IDs (like 401811937) stay as the rows
        df = pd.DataFrame.from_dict(raw_data, orient='index')
        
        # 3. Force the Index to be strings (removes any .0 or scientific notation)
        # We do this immediately to lock in the format
        df.index = df.index.map(str)
        
        # 4. Build the names for your dropdown
        names = []
        for tourn_id, row in df.iterrows():
            # We use the index (tourn_id) directly
            full_name = row.get('tournamentFullName', 'Unknown Tournament')
            names.append(f"{full_name} ({tourn_id})")
            
        print(names)
        print("---")
        print(df)
        print("---")
        print(f"Successfully loaded {len(names)} tournaments with clean IDs.")

    except Exception as e:
        print(f"Error in load_active_save: {e}")
        messagebox.showerror("Load Error", f"Could not process active-save.json: {e}")

        
load_active_save('../control/gui-save.json')