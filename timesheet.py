# author: zainab ahsan
# last updated: 2025-08-13

import pandas as pd
import os
class Timesheet:

    CURRENT_FILE = "timesheet_updated.csv"     # current/updated timesheet
    PREVIOUS_FILE = "timesheet_previous.csv"   # previous previous

    @staticmethod
    def load_timesheets():
        # load current file
        if not os.path.exists(Timesheet.CURRENT_FILE):
            raise FileNotFoundError(f"Error: {Timesheet.CURRENT_FILE} does not exist.")
        current_df = pd.read_csv(Timesheet.CURRENT_FILE)

        # load previous file or create it from current if missing
        if os.path.exists(Timesheet.PREVIOUS_FILE):
            previous_df = pd.read_csv(Timesheet.PREVIOUS_FILE)
        else:
            print(f"No previous file found. Creating {Timesheet.PREVIOUS_FILE} from current file.")
            current_df.to_csv(Timesheet.PREVIOUS_FILE)
            previous_df = current_df.copy()

        return Timesheet.index_dfs(current_df, previous_df)
    
    def check_updates(current_df, previous_df):
        # check for added rows/courses
        added_rows = current_df.loc[~current_df.index.isin(previous_df.index)]
        # check for removed rows/courses
        removed_rows = previous_df.loc[~previous_df.index.isin(current_df.index)]
        # check for updated rows/courses
        common_index = current_df.index.intersection(previous_df.index)
        
        # Align columns before comparing to handle added/removed columns
        previous_df_aligned, current_df_aligned = previous_df.align(current_df, join='inner', axis=1)
        
        diffs = current_df_aligned.loc[common_index].compare(previous_df_aligned.loc[common_index], result_names=('new', 'old'))
        
        if not diffs.empty:
            # Reshape the diffs DataFrame to be more readable
            updated_rows = diffs.stack(level=0).reset_index()
            updated_rows.rename(columns={'level_2': 'Field', 'new': 'New Value', 'old': 'Old Value'}, inplace=True)
            # Reorder columns for clarity
            updated_rows = updated_rows[['Division', 'Course + Section', 'Field', 'Old Value', 'New Value']]
        else:
            updated_rows = pd.DataFrame(columns=['Division', 'Course + Section', 'Field', 'Old Value', 'New Value'])

        return added_rows, removed_rows, updated_rows
        
    def index_dfs(current_df, previous_df):
        index_cols = ["Division", "Course + Section"]
        current_df.set_index(index_cols, inplace=True)
        previous_df.set_index(index_cols, inplace=True)
        return current_df, previous_df

    @staticmethod
    def main():
        current_df, previous_df = Timesheet.load_timesheets()
        added, removed, updated = Timesheet.check_updates(current_df, previous_df)
        
        output_file = 'changes.csv'
        with open(output_file, 'w') as f:
            f.write("Added Rows\n")
            if not added.empty:
                added.to_csv(f, header=True)
            
            f.write("\nRemoved Rows\n")
            if not removed.empty:
                removed.to_csv(f, header=True)
                
            f.write("\nUpdated Rows\n")
            if not updated.empty:
                updated.to_csv(f, header=True, index=False)
        
        print(f"Changes saved to {output_file}")
        
if __name__ == "__main__":
    Timesheet.main()