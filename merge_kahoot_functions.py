#*********************************************************************************#
#    Written by Adi Teman 2023
#       inspired by David Peled, 2019
#*********************************************************************************#
# Functions in merge_kahoot_functions.py
#   get_id_table:  Parses the table of student names and IDs
#   get_players_and_scores: Parses the Kahoot reports
#   write_out_excel: Exports the summary excel file
#*********************************************************************************#
#*********************************************************************************#

#-----------------------------#
#   Get ID Table              #
#-----------------------------#
# Input: Name of the students id table file we want to open
# Output: Two hashes -
#   1) IDs to student name
#   2) Frozensets to IDs
def get_id_table(filename):
    import pandas as pd

    # Read ID table into dataframe
    df = pd.read_csv(filename)

    # Column headers for dataframe:
    ID     = 'ID'
    #FIRST  = 'First Name'
    #LAST   = 'Last Name'
    NAME = 'Name'

    ID_HASH = dict()
    KAHOOT_NAMES_HASH = dict()
        
    for index, row in df.iterrows():
        this_id=str(row[ID])
        print(row[NAME])
        this_name=row[NAME].split(' ')
        this_frozen=frozenset([str(item) for item in this_name if item])
        if not this_id in ID_HASH:
            ID_HASH[this_id]=this_name
        KAHOOT_NAMES_HASH[this_frozen]=this_id
    return ID_HASH, KAHOOT_NAMES_HASH
#------get_id_table--------------#


#*********************************************************************************#
#*********************************************************************************#

#-----------------------------#
#   Get Players and Scores    #
#-----------------------------#
# Input: Kahoot Report XLSX file
# Output: Dataframe containing
#   1) Frozenset of player name
#   2) Score, Number of Correct Answers, Ratio to High Score

def get_players_and_scores(path,report,KAHOOT_NAMES_HASH):
    import pandas as pd
    # Kahoot report headers:
    PLAYER = 'Player'
    SCORE = 'Total Score (points)'
    CORRECT = 'Correct Answers'

    # Remove the xlsx extension from the file name 
    kahoot_name = report[:-4]
    print("Reading "+report)

    # Read the xlsx into a pandas dataframe
    #       Use the "Final Scores" sheet
    #       The third row [2] is the header row
    #       Only read the column names you want
    df = pd.read_excel(path + '/' + report, \
        sheet_name='Final Scores', \
        header=2, \
        usecols=[PLAYER,SCORE,CORRECT])
    
    # Clean up the data a bit:
    # ------------------------
    # Get rid of null values
    df = df.dropna()
    # Make all players names into lowercase
    df[PLAYER] = df[PLAYER].str.lower()
    # remove any junk around the player name: whitespace, ., #, etc.
    df[PLAYER] = df[PLAYER].str.strip('.# \t\n\r\x0b\x0c')
    # Turn the points from strings to integers
    df[SCORE] = df[SCORE].apply(lambda x: int(x))

    # Create Index out of IDs (when they exist) and odd player names (otherwise)
    # -------------------------------------
    # First we split the string about the characters: '.','_','-' and other white space characters.
    # Note the '+' indicates we want to include cases of repeating characters.
    # Example: 'david. ._ -- .peled' will become ['david','peled']
    players = df[PLAYER].str.split(r'[._\s-]+', expand=False)
 
    # We then turn the lists into frozensets.
    #     this creates un-ordered pairs which is exactly what we want:
    # To create equivalence between the lists ['david', 'peled'] and ['peled','david']
    players = players.apply(lambda val: frozenset(val))

    # Now we can look up the ID of the frozenset and create a list of IDs
    id_list=[]
    couldnt_find=[] # list of names not defined in the students list
    for set in players:
        if set in KAHOOT_NAMES_HASH:
            id_list.append(KAHOOT_NAMES_HASH[set])
            #print('Adding '+ KAHOOT_NAMES_HASH[set])
        else:
            id_list.append(' '.join(set))
            couldnt_find.append(set)
            #print(' '.join(set) + ' Not in hash')
            #print(list(set)[0] + ' ' + list(set)[1] + ' Not in hash')

    # Finally, we add the id_list to the dataframe as an index 
    df.insert(0,'ID',id_list)


    
    # Dealing with the Dahaman Effect: 
    # -------------------------------
    # When a student leaves mid-kahoot and re-enters, 
    #   his points might be scattered through different instances of his name.
    #   So to deal with this we need to sum all the points of a player with the same ID 
    # 1) We split our table to sub-groups by the ID.
    #    df.groupby() returns the grouped-by table
    # 2) We then access the points (and correct) column and use the sum transformation (which operates by groups).
    df[SCORE] = df.groupby('ID')[SCORE].transform('sum')
    df[CORRECT] = df.groupby('ID')[CORRECT].transform('sum')
    # 3) This resulted in all the rows with the same frozenset to have the same score and correct. So we need to drop the dupes.
    df = df.drop_duplicates(subset='ID')


    # If we want to count legit participation according to ratio of score:
    # 1) Calculate the highest score in the kahoot
    highscore=df[SCORE].max()
    # 2) Make a list of the ratio of each score to the high score
    score_ratio=[]
    for score in df[SCORE]:
        score_ratio.append(round(score/highscore,2))
    # 3) Add a score ratio column to the dataframe
    df['Ratio']=score_ratio
    
    # Return the dataframe with names that include the kahoot name
    output_df=df[['ID',SCORE,CORRECT,'Ratio']]
    output_df.columns=['ID',kahoot_name+' Score',kahoot_name+' Correct',kahoot_name+'Ratio']
    return(output_df,couldnt_find)
#-------get_players_and_scores-------------#



#*********************************************************************************#
#*********************************************************************************#


#-----------------------------#
#   write_out_excel           #
#-----------------------------#
# Input: Name of the students id table file we want to open
# Output: Two hashes -
#   1) IDs to student name
#   2) Frozensets to IDs
def write_out_excel(merged,ID_HASH,CORRECT_THRESHOLD,RATIO_THRESHOLD,OUTPUT_FILE):
    import pandas as pd
    import numpy as np
    pd.options.mode.chained_assignment = None  # quiets SettingWithCopyWarning
    # Column headers for dataframe:
    ID     = 'ID'
    FIRST  = 'First Name'
    LAST   = 'Last Name'

    # Add First Name and Last Name of IDs to dataframe
    # ------------------------------------------------
    first_list=[]
    last_list=[]
    for id in merged[ID]:
        if id in ID_HASH:
            print(id, ID_HASH[id][0], ID_HASH[id][1])
            first_list.append(ID_HASH[id][0])
            last_list.append(ID_HASH[id][1])
        else:
            first_list.append('')
            last_list.append('')
    merged.insert(1,FIRST,first_list)
    merged.insert(2,LAST,last_list)

    # -----------------------------------------------------#
    # Create separate dataframes for scores, correct, ratio
    # -----------------------------------------------------#
    basic_columns=[ID,FIRST,LAST]
    # Score DataFrame 
    # ---------------
    # including number of missed Kahoots and total score from all Kahoots:
    score_columns=[i for i in merged.columns.to_list() if 'Score' in i]
    score_df  = merged[basic_columns + score_columns]
    # Counting missed kahoots: just Counting Null Scores created by the outer-join.
    missed_kahoots = score_df.iloc[:,3:].isnull().sum(axis=1)
    score_df['Missed Kahoots'] = missed_kahoots
    # Removing names -> replacing nulls with 0 -> converting strings to integers, and finally summing row by row.
    total_scores = score_df.iloc[:,3:].fillna(0).astype('int64').sum(axis=1)
    score_df['Total Score']=total_scores
    
    # Correct DataFrame
    # -----------------
    # including number of Kahoots with Correct>Threshold
    correct_columns = [i for i in merged.columns.to_list() if 'Correct' in i]
    correct_df = merged[basic_columns + correct_columns]
    total_correct_list=[]
    for index, row in correct_df.iterrows():
        total_correct=0
        for num_correct in row[3:]:
            if num_correct>=CORRECT_THRESHOLD:
                total_correct+=1
        total_correct_list.append(total_correct)
    correct_df['>'+str(CORRECT_THRESHOLD)+' Correct']=total_correct_list

    # Final Grade DataFrame
    # ---------------------
    # Calculate the grade:
    # --- More than 7 correct = 100
    # --- Every wrong answer under that --> -20
    
    grades_df = merged[basic_columns + correct_columns] # Create the dataframe
    grades_df = grades_df.fillna(0)  # turn NaN into zeros
    for i in range(grades_df.shape[0]):  # Iterate over rows
        for j in range(3,grades_df.shape[1]):  # Iterate over columns
            # Change the number of correct answers into a grade between 0 and 100, as described above
            grades_df.iat[i, j] = max(0,min(100,(grades_df.iat[i, j]-2)*20)) 
    # Now choose the top 7 Kahoots and find their average.
    # Store this in a new column
    # Store the number of points (the Kahoot is worth 8 points)
    grades_df['Average'] = 0
    grades_df['Points'] = 0

    for index, row in grades_df.iterrows():  # Iterate over rows
        print(row.iloc[3:].tolist())
        grades = sorted(row.iloc[3:].tolist(),reverse=True)  # Sort the grades in a list
        average_grade = np.mean(grades[:7])   # Calculate the average of the top 7 grades
        # Write the average grade into the 'Average' column
        grades_df.at[index, 'Average'] = int(average_grade)
        # Write the number of points into the 'Points' column
        final_points = int(8 * (average_grade / 100))
        grades_df.at[index, 'Points'] = final_points



                

    # Ratio DataFrame
    # ---------------
    # including ratio > threshold
    ratio_columns=[i for i in merged.columns.to_list() if 'Ratio' in i]
    ratio_df  =merged[basic_columns+ratio_columns]
    total_ratio_list=[]
    for index, row in ratio_df.iterrows():
        total_ratio=0
        for num_ratio in row[3:]:
            if num_ratio>=RATIO_THRESHOLD:
                total_ratio+=1
        total_ratio_list.append(total_ratio)
    ratio_df['Score > '+str(RATIO_THRESHOLD)+'*Max']=total_ratio_list

   
    print('Writing '+ OUTPUT_FILE)    
    with pd.ExcelWriter(OUTPUT_FILE) as writer:
        score_df.to_excel(writer, sheet_name='Scores', index=False)
        correct_df.to_excel(writer, sheet_name='Correct', index=False)
        ratio_df.to_excel(writer, sheet_name='Ratio', index=False)
        grades_df.to_excel(writer, sheet_name='Final Grade', index=False)

    return   

#----write_out_excel----------#

