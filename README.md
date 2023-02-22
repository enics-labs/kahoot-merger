# kahoot-merger
A python script for parsing Kahoot! result Excels.

# Goal
The goal of the kahoot-merger script is to collect all the results from a bunch of Kahoot! quiz reports and combine them into a merged Excel sheet.

Why is this interesting/important?
I hold Kahoot! quizzes in my university classes. In fact, these are the framework for my "flipped classroom" style of teaching. And I give part of my grade based on these Kahoots. In the age of Generation-Z, this is one of the only ways to actually get the students to come to class, so I don't have to talk to an empty room :)

The use case is:
- I hold Kahoot! quizzes during my lectures.
- I require the students to login using a format, such as "FIRST_NAME.LAST_NAME" (e.g., "Adam Teman")
- At the end of the semester, I download all the reports from the Kahoot website. These are nicely formatted Excel sheets with a lot of data about the quizzes.
- Then I run the kahoot-merger script to collect the scores from all the reports and merge them according to the student names.

# Before running the script:

## Download Kahoot Reports:

To get the Kahoot! Reports:
- Login to your kahoot.com account
- Click on "Reports"
- Click on the hamburger menu on the right of the relevant quiz name
- Select "Download Report"

Gather all your reports into a directory called "reports"

## Create a list of student names and IDs

The goal of the students ID file is to map the names that the students use in the Kahoot to a single person. 
If a student doesn't follow the rules (and they never do), then you will have a separate entry for each player name he or she used.
Therefore, this stage is not mandatory, but if you want nice results, you should follow these steps:
- Create a .csv file called "students.csv" and save it under the "students" directory.
- Call the column headers: "First Name", "Last Name" and "ID"
- Fill in the first name, last name and ID of your participants in the document.
(see example students.csv file provided in the repo)

A few notes:
- You can use any identifier in the ID column (I use the students' ID number that I get in the course list)
- The script will merge different naming conventions, such as "first.last", "last.first", "first_last", etc. 
  However, if a student accidentally registers with some strange user name, the output of the script will tell you and you will get rows with strange user names in the merged excel sheet.
- To solve this, copy the name they used into the students.csv file and add the same ID as for the regular entry. I will elaborate upon this in the USAGE section below.

# USAGE

1. Make sure you have all the reports in the "reports" directory and the students file in the "students" directory.
2. Run the python script: %> python3 merge_kahoots.py
3. Hopefully, the script will finish without any errors, and your merged report will be under the "merged_kahoots" directory.
4. The terminal will print out a list of students without IDs. If you can match their mistake with the right ID, then copy the string they used into your students.csv file and in the ID column, add the correct ID associated with this student. In other words, you will have your regular entry from before (e.g., "Joe", "Blow", "12345") and then your duplicate entry with the same ID (e.g., "JOEBLOW","","12345").
5. Now rerun the script and your output worksheet should be clean.

Note that this will sum up the accumulated total of a student who got disconnected during the quiz and reconnected, something that happens quite often.

# Output
- You will get a worksheet under the "merged_kahoots" directory with a date stamp. 
- The worksheet (currently) has three tabs "Scores", "Correct" and "Ratio"
- The "Scores" Tab has the scores of each quiz and a column with the Total Sum.
- The "Correct" Tab has number of correct answers in each quiz and a column with the number of quizzes above a threshold (default is 3 correct answers). 
- The "Ratio" Tab has ratio of the student's score in each quiz to the top score achieved in that quiz and a column with the number of quizzes above a threshold (default is 25% of the top score). 


### What are these thresholds?
So, I have gone through several use cases of providing a grade for Kahoot! participation. At first, I gave a bonus relative to the total score. But it caused all kinds of problems (e.g., "I was sick", "My internet dropped", etc.). 
Then I went to "participate if you want". But I found myself alone in the class with three students.
So I moved to giving part of the grade according to participation in the Kahoots. But I found many "0" scores from students who logged in but didn't participate. 
I finally settled on a criteria for participation, which is that you have to have a certain number of correct answers or score to have it count.

So, there are currently two types of thresholds to count a Kahoot!
1. Correct Answers: If a student has at least 3 correct answers, I count their participation. You can set the threshold value in the constants definition with the CORRECT_THRESHOLD variable.
2. Ratio: This is a more flexible and more representative criteria. I count participation only if the student's score is at least 25% of the top score achieved in the Kahoot. You can set the threshold value in the constants definition with the RATIO_THRESHOLD variable.

# Acknowledgements
This script originated when I gave a challenge to my class in 2019, giving the top Kahoot grade (5 points...) for whoever would write me such a script. David Peled jumped on the opportunity and I used his script for several years. However, I needed to change some features and after a few years of experience with the existing script, I found myself spending way too many hours rewriting it. So the current, 95% rewritten code, is provided here.

Thanks, David, for being the one to jumpstart this.
