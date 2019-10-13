import sys
import subprocess
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QImage, QPixmap
from datetime import datetime
import json
import pandas as pd
import csv
from datetime import timedelta

data = {}
data['demo'] = []

#Reading csv for data stored by Demo GUI:
def update_row(data_dynamic_list, skill, demo_cnt, accuracy, diff, asset_updated_cnt, frames, days, feedback, iteration):
    data_dynamic_list.extend([skill, demo_cnt, accuracy, diff, asset_updated_cnt, frames, days, feedback, iteration])
    return data_dynamic_list

# Function to insert row in the dataframe 
def Insert_row(row_number, df, row_value): 
    # Slice the upper half of the dataframe 
    df1 = df[0:row_number] 
    # Store the result of lower half of the dataframe 
    df2 = df[row_number:] 
    # Insert the row in the upper half dataframe 
    df1.loc[row_number]=row_value
    # Concat the two dataframes 
    df_result = pd.concat([df1, df2])
    # Reassign the index labels 
    df_result.index = [*range(df_result.shape[0])]
    # Return the updated dataframe 
    return df_result

def write_csv(self, data_dynamic_list, skillname, feedback):
    df = pd.read_csv('data_dynamic.csv')

    if(feedback == 'NOT OK' or feedback == 'CANT TELL' and skillname != 'bumping'):
        row_num = self.learnable_count
        self.learnable_count += 1
        self.learnt_count += 1
        self.extrapolated_skills_count += 1
    elif(feedback == 'OK' and skillname != 'bumping'):
        row_num = self.learnt_count
        self.learnt_count += 1
        self.extrapolated_skills_count += 1
    elif(skillname == 'bumping'):
        row_num = self.extrapolated_skills_count
        self.extrapolated_skills_count += 1
    
    df_new = Insert_row(row_num, df, data_dynamic_list)
    df_new.to_csv('data_dynamic.csv', index=False)
    
def read_txt():
    with open('out.txt', 'r') as output:
        accuracy = output.read()
    return accuracy

def write_json(feedback, count, name, skill):
    data['demo'].append({
    'name': name,
    'datetime': str(datetime.now()),
    'skill' : skill,
    'feedback': feedback
    })
    #writing data in JSON
    with open('data_dict.json', 'w') as json_file:
        json.dump(data, json_file)
        print(data)
    count +=1
    text = str(count) + " - " + str(datetime.now().strftime("%x %X")) + " " + name + " " + skill
    print(text)
    return text, count
    
class opencvgui(QDialog):

    def __init__(self):
        super(opencvgui, self).__init__()
        loadUi('Navigator.ui', self)
        self.count = 0
        self.feedback = ''
        self.assets = []
        self.data_dynamic_list =['']
        #counter variables for number of demos:
        self.demo_cnt = 0
        self.red_cnt = 0
        self.yellow_cnt = 0
        self.brown_cnt = 0
        self.crash_cnt = 0
        self.asset_updated_cnt = 0
        self.accuracy = 0
        #csv row count
        self.learnable_count = 1
        self.learnt_count = 2
        self.extrapolated_skills_count = 3
        #buttons
        self.RunBtn.setEnabled(True)
        self.NotOKBtn.setEnabled(True)
        self.CantTellBtn.setEnabled(True)
        self.OKBtn.setEnabled(True)
        self.exitBtn.setEnabled(True)
        #comboBox
        self.skillcomboBox.setEnabled(True)
        self.ItCBox.setEnabled(True)
        self.FCBox.setEnabled(True)
        #TextBox
        self.nameBox.setEnabled(True)
        self.DictionaryBox.setEnabled(True)
        #setting values from the click of run button:
        self.skill = None
        self.iteration = None
        self.frames = None
        self.feedback = None
        
        self.name = None
        self.a = None
        self.b = None
        self.c = None
        self.now = None
        self.then = None
        self.diff = None
        self.days = "0 days"
        #Mapping button clicks with proper functions:
        self.RunBtn.clicked.connect(self.runSkill)
        self.NotOKBtn.clicked.connect(self.NOKBtn)
        self.CantTellBtn.clicked.connect(self.CTBtn)
        self.OKBtn.clicked.connect(self.OkBtn)
        self.exitBtn.clicked.connect(sys.exit)
    
    @pyqtSlot()
    def runSkill(self):
        #call skill BHIRL to play
        self.now = datetime.now()
        # Getting skill name and adding it to a list to keep a track of unique skills(assets) updated
        self.skill = str(self.skillcomboBox.currentText())
        #updating count for unique assets updated
        if(self.skill not in self.assets):
            self.asset_updated_cnt += 1
            #time details:
            self.a = datetime.now()
        #time details:
        elif(self.skill in self.assets):
            #time details:
            self.b = datetime.now()
            self.c = self.b - self.a
            # Days since last update
            self.days = str(self.c.days) + " days"

        self.assets.append(self.skill)
        #Updating the demos count based on the skill name:
        if(self.skill == "red"):
            self.red_cnt += 1
            self.demo_cnt = self.red_cnt
        elif(self.skill == "yellow"):
            self.yellow_cnt += 1
            self.demo_cnt = self.yellow_cnt
        elif(self.skill == "brown"):
            self.brown_cnt += 1
            self.demo_cnt = self.brown_cnt
        elif(self.skill == "bumping"):
            self.crash_cnt += 1
            self.demo_cnt = self.crash_cnt
           
        self.iteration = str(self.ItCBox.currentText())
        self.frames = str(self.FCBox.currentText())
        subprocess.call(['bash', 'start.sh', self.skill, self.iteration, self.frames])    
        print("give feedback")
        self.accuracy = read_txt()
        # Time taking for one run in minutes
        self.then = datetime.now()
        self.diff = self.then - self.now
        self.diff = str(round(self.diff / timedelta(minutes=1), 4)) + " min"
        print(self.diff)

    def NOKBtn(self):
        self.feedback = 'NOT OK'
        self.name = self.nameBox.document().toPlainText()
        self.skill = str(self.skillcomboBox.currentText())
        self.iteration = str(self.ItCBox.currentText())
        text, cnt = write_json(self.feedback, self.count, self.name, self.skill)
        self.count = cnt
        self.DictionaryBox.append(text + " : " + self.feedback)
        #building rows and writing rows
        self.data_dynamic_list = update_row(self.data_dynamic_list, self.skill, str(int(self.demo_cnt)), self.accuracy, self.diff, \
                   str(int(self.asset_updated_cnt)), str(int(self.frames)), self.days, self.feedback, self.iteration)
        write_csv(self, self.data_dynamic_list, self.skill, self.feedback)
        # setting the row list as empty for next demo
        self.data_dynamic_list = ['']
        self.demo_cnt = 0

    def CTBtn(self):
        self.feedback = 'CANT TELL'
        self.name = self.nameBox.document().toPlainText()
        self.skill = str(self.skillcomboBox.currentText())
        self.iteration = str(self.ItCBox.currentText())
        text, cnt = write_json(self.feedback, self.count, self.name, self.skill)
        self.count = cnt
        self.DictionaryBox.append(text + " : " + self.feedback)
        #building rows and writing rows
        self.data_dynamic_list = update_row(self.data_dynamic_list, self.skill, str(int(self.demo_cnt)), self.accuracy, self.diff, \
                   str(int(self.asset_updated_cnt)), str(int(self.frames)), self.days, self.feedback, self.iteration)
        # setting the row list as empty for next demo
        self.data_dynamic_list = ['']
        self.demo_cnt = 0

    def OkBtn(self):
        self.feedback = 'OK'
        self.name = self.nameBox.document().toPlainText()
        self.skill = str(self.skillcomboBox.currentText())
        self.iteration = str(self.ItCBox.currentText())
        text, cnt = write_json(self.feedback, self.count, self.name, self.skill)
        self.count = cnt
        self.DictionaryBox.append(text + " : " + self.feedback)
        #building rows and writing rows
        self.data_dynamic_list = update_row(self.data_dynamic_list, self.skill, str(int(self.demo_cnt)), self.accuracy, self.diff, \
                   str(int(self.asset_updated_cnt)), str(int(self.frames)), self.days, self.feedback, self.iteration)
        write_csv(self, self.data_dynamic_list, self.skill, self.feedback)
        # setting the row list as empty for next demo
        self.data_dynamic_list = ['']
        self.demo_cnt = 0

#runnning Qt App
app = QApplication(sys.argv)
window = opencvgui()
window.setWindowTitle("Demonstrations Dictionary")
window.show()
sys.exit(app.exec_())