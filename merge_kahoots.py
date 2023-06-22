import os
import pandas as pd
from datetime import datetime
import numpy as np  # for np.nan 
import merge_kahoot_functions as mk


__author__ = "Prof. Adam Teman"
__inspired_by__ = "David Peled"
__copyright = "Copyright (c) 2023 EnICS Labs"
__credits__ = ["David Peled", "Prof. Adam Teman", "Google"]

__license__ = "MIT"
__version__ = "2.1"
__maintainer__ = "Adam Teman"
__email__ = "adam.teman@biu.ac.il"
__status__ = "Development"


#--------------------------------------#
#  Constant Definitions                #
#--------------------------------------#

# -------------- File & Folder Names -------------- #
REPORTS_PATH = 'reports'              # Folder where we keep the kahoot csvs.
STUDENTS_FILE = 'students/students.csv'
# A suffix we will add to the final result file:
DAY_MONTH_YEAR = str(datetime.now().day) + '_' + str(datetime.now().month) + '_' + str(datetime.now().year)  
# The name of the result file:
OUTPUT_PATH = 'merged_kahoots'
OUTPUT_FILE = OUTPUT_PATH + '/merged_kahoots' + '_generated' + DAY_MONTH_YEAR + '.xlsx' 

# Thresholds for final result calculation
CORRECT_THRESHOLD=3    # Need more than 3 right answers to count Kahoot
RATIO_THRESHOLD=0.25   # Need more than 25% of the top score to count Kahoot

#------------------------#
#         Main           #
#------------------------# 

if __name__ == '__main__':

    # Create hashes for the student names and IDs
    ID_HASH, KAHOOT_NAMES_HASH = mk.get_id_table(STUDENTS_FILE)
    #df=pd.DataFrame(data=KAHOOT_NAMES_HASH, index=[0])
    #df.to_excel("tmp.xlsx",index=False)

    # Get all xlsx files in the 'kahoots/' directory.
    reports = os.listdir(REPORTS_PATH)


    # Iterate over all xlsx files 
    #-----------------------------#
    couldnt_find_list=[]
    for report in reports:
        # Parse excel sheet and return a pandas dataframe
        this_report,couldnt_find = mk.get_players_and_scores(REPORTS_PATH,report,KAHOOT_NAMES_HASH)
        couldnt_find_list += couldnt_find
        # Merge the dataframes of all kahoots together
        if 'merged' in globals():   # check if this is the first file
            merged = pd.merge(merged, this_report, \
                    left_on='ID', right_on='ID', how='outer')
        else:                               # if it is the first file
            merged = this_report
    
    # Write out the final output in a multisheet Excel file
    if not os.path.isdir(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    mk.write_out_excel(merged,ID_HASH,CORRECT_THRESHOLD,RATIO_THRESHOLD,OUTPUT_FILE)
   
    print('Finished Parsing Kahoot data successfully.')

    print("Couldn't find IDs for the following player names:")
    for name in couldnt_find_list:
        print(' '.join(name))
