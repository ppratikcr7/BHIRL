import sys
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QImage, QPixmap
from datetime import datetime
import playing
import json

data = {}
data['demo'] = []
feedback = ''
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
        #buttons
        self.count = 0
        self.skill = str(self.skillcomboBox.currentText())
        self.RunBtn.setEnabled(True)
        self.NotOKBtn.setEnabled(True)
        self.CantTellBtn.setEnabled(True)
        self.OKBtn.setEnabled(True)
        self.exitBtn.setEnabled(True)
        #comboBox
        self.skillcomboBox.setEnabled(True)
        #TextBox
        self.nameBox.setEnabled(True)
        self.DictionaryBox.setEnabled(True)
        
        #Mapping button clicks with proper functions:
        self.RunBtn.clicked.connect(self.runSkill)
        self.NotOKBtn.clicked.connect(self.NOKBtn)
        self.CantTellBtn.clicked.connect(self.CTBtn)
        self.OKBtn.clicked.connect(self.OkBtn)
        self.exitBtn.clicked.connect(sys.exit)
    
    @pyqtSlot()
    def runSkill(self):
        #call skill BHIRL to play
        self.skill = str(self.skillcomboBox.currentText())
        playing.read(self.skill, 2, 3000)
        print("give feedback")
        
    def NOKBtn(self):
        feedback = 'NOT OK'
        name = self.nameBox.document().toPlainText()
        self.skill = str(self.skillcomboBox.currentText())
        text, cnt = write_json(feedback, self.count, name, self.skill)
        self.count = cnt
        self.DictionaryBox.append(text + " : " + feedback)

    def CTBtn(self):
        feedback = 'CANT TELL'
        name = self.nameBox.document().toPlainText()
        self.skill = str(self.skillcomboBox.currentText())
        text, cnt = write_json(feedback, self.count, name, self.skill)
        self.count = cnt
        self.DictionaryBox.append(text + " : " + feedback)

    def OkBtn(self):
        feedback = 'OK'
        name = self.nameBox.document().toPlainText()
        self.skill = str(self.skillcomboBox.currentText())
        text, cnt = write_json(feedback, self.count, name, self.skill)
        self.count = cnt
        self.DictionaryBox.append(text + " : " + feedback)

#runnning Qt App
app = QApplication(sys.argv)
window = opencvgui()
window.setWindowTitle("Demonstrations Dictionary")
window.show()
sys.exit(app.exec_())
