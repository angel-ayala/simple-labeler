#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 00:14:34 2020

@author: Angel Ayala <angel4ayala [at] gmail.com>
"""

import os
import sys
import cv2
import ast
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QToolBar
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QListWidget

from handlers import DataHandler
from dialogs import CsvNameDialog
from dialogs import MessageDialog


class LabelerWindow(QMainWindow):
    """A simple GUI to label dataset for classification tasks."""
    
    def __init__(self, *args, **kwargs):
        super(LabelerWindow, self).__init__(*args, **kwargs)
        self.data = None
        self.current = -1
        self.isLabeling = False
        self.changesSaved = True
        
        # labels
        self.labels = []
        self.labels_id = ['none', 'fire', 'smoke']
        self.labels_name = ['None', 'Fire', 'Smoke']
        self.labels_default = 0 #none
        
        self.setWindowTitle("Simple Labeler")        
        # self.setApplicationDisplayName('Simple Labeler')
        self.setWindowIcon(QIcon('assets/task-icon.png'))
        self.embedToolBar()
        
        self.mainWidget = QWidget(self)        
        self.mainLayout = QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)        
        self.setCentralWidget(self.mainWidget)
        self.resize(450, 550)
                
        label = QLabel("Labels")
        label.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(label)
        
        self.embedCheckBox()
        
        self.imagesInfo = QLabel("Images")
        self.imagesInfo.setAlignment(Qt.AlignCenter)
        self.mainLayout.addWidget(self.imagesInfo)
        
        self.embedList()
        
        self.embedButtons()
        
    @property
    def haveLabels(self):
        return len(self.labels) > 0
    
    @property 
    def isMultiLabel(self):
        return len(self.labels) > 1
    
    @property
    def isSingleLabel(self):
        return len(self.labels) == 1
        
    def embedList(self):
        
        self.listWidget = QListWidget(self.mainWidget)
        self.listWidget.itemSelectionChanged.connect(self.onSelectItem)
        
        self.mainLayout.addWidget(self.listWidget)
        
    def embedButtons(self):   
        # image navigation buttons
        layout = QHBoxLayout()
        
        prev_button = QPushButton(self.mainWidget)
        prev_button.setIcon(QIcon("assets/arrow-prev.png"))
        prev_button.setStatusTip("See previous image")
        prev_button.setShortcut("A")
        prev_button.clicked.connect(self.onPrevImage)
        layout.addWidget(prev_button)
        
        next_button = QPushButton(self.mainWidget)
        next_button.setIcon(QIcon("assets/arrow-next.png"))
        next_button.setStatusTip("See next image")
        next_button.setShortcut("D")
        next_button.clicked.connect(self.onNextImage)        
        layout.addWidget(next_button)
        
        self.mainLayout.addLayout(layout)
        
        
    def embedToolBar(self):
        toolbar = QToolBar("Main Toolbar", self)
        self.addToolBar(toolbar)
        
        # read
        button_action = QAction(QIcon("assets/database.png"), "Read CSV File", self)
        button_action.setStatusTip("Choose dataset's CSV file")
        button_action.triggered.connect(self.onImportCsv)
        toolbar.addAction(button_action)
        
        # create
        button_action = QAction(QIcon("assets/database--plus.png"), "Generate CSV File", self)
        button_action.setStatusTip("Choose folder which contains the images, or subfolder with images.")
        button_action.triggered.connect(self.onCreateCsv)
        toolbar.addAction(button_action)
        
        toolbar.addSeparator()
        
        # write
        button_action = QAction(QIcon("assets/disk.png"), "Save CSV File", self)
        button_action.setStatusTip("Write changes to dataset CSV file")
        button_action.triggered.connect(self.onSaveCsv)
        toolbar.addAction(button_action)
        
        toolbar.addSeparator()
                
        self.setStatusBar(QStatusBar(self))
        
        
    def embedCheckBox(self):
        layout = QVBoxLayout()
        self.checkboxes = []
        
        for label, c in enumerate(self.labels_name):
            checkbox = QCheckBox(c, self.mainWidget)
            checkbox.setChecked(label in self.labels)
            # checkbox.stateChanged.connect(self.onCheckboxChange)
            self.checkboxes.append(checkbox)
            layout.addWidget(checkbox)
        
        self.mainLayout.addLayout(layout)
        
    def onImportCsv(self, s):        
        dialog = QFileDialog.getOpenFileName(self, 'Open file', '',
                                                    "CSV files (*.csv)")
        
        if os.path.isfile(dialog[0]):
            # reset if was labeling
            if self.isLabeling:
                self.stopLabeling()
            # load data
            self.data = DataHandler(dialog[0])
            # start labeling
            self.startLabeling()
            
    def onCreateCsv(self, s):
        main_folder = str(QFileDialog.getExistingDirectory(self, 
                                            "Choose dataset directory"))
        
        # if there is no folder, do nothing
        if not os.path.isdir(main_folder):
            return False
        
        optDialog = CsvNameDialog()
        
        # get desired filename and if images are organized from user
        if optDialog.exec_() == CsvNameDialog.Accepted:
            filename, have_labels = optDialog.getValues()
        else:
            # if cancel, do nothing
            return False
        
        # reset if was labeling
        if self.isLabeling:
            self.stopLabeling()
        
        # initialize data handler
        self.data = DataHandler(os.path.join(main_folder, filename))
        self.data.create(have_labels)
                
        if len(self.data) > 0:
            message = "{} images found, save to file?".format(len(self.data))
            title = "Images found"
        else:
            message = "No image were found!"
            title = "No images in folder"
        
        dlg = MessageDialog(title, message)
        
        if dlg.exec_():
            # save csv
            self.data.save()
            # start labeling
            self.startLabeling()
        else:
            self.data = None
            
    def onSaveCsv(self, button):
        self.changesSaved = True
        self.data.save()
            
    def onNextImage(self, s):
        if self.current +1 < len(self.data):
            self.listWidget.setCurrentRow(self.current +1)        
        
    def onPrevImage(self, s):        
        if self.current >= 1:
            self.listWidget.setCurrentRow(self.current -1)
    
    def onSelectItem(self):
        if self.current > -1:
            self.processLabels()
            # update labels
            self.updateItem()
        self.current = self.listWidget.currentRow()
        self.processImage()

    def startLabeling(self):
        # init data and pointer
        self.data.read()
        self.current = -1
        # populate list for selection
        self.populateList()
        # initiate image visor
        cv2.namedWindow("Image", cv2.WINDOW_NORMAL)            
        # process first image
        self.listWidget.setCurrentRow(0)
        self.changesSaved = True
        self.isLabeling = True        
        
    def stopLabeling(self):
        self.launchSaveChanges()
        # images presenter and info
        self.imagesInfo.setText("Images")
        self.listWidget.clear()
        cv2.destroyAllWindows()
        # reset data
        self.data = None
        self.labels = []
        self.isLabeling = False    
        
    def parseLabel(self, label_name):        
        label = []
        
        def label_idx(l):
            if l in self.labels_id:
                return self.labels_id.index(l)
            else:
                return l
        
        if isinstance(label_name, str) and '[' in label_name: # is a list
            label_name = ast.literal_eval(label_name)
            
        if isinstance(label_name, list):
            label = []
            for l in label_name:
                label.append(label_idx(l))
        else:
            label.append(label_idx(label_name))
            
        return label
        
    def id2label(self, label_id):
        labels = None
        
        def label_name(label):
            if isinstance(label, int):
                return self.labels_id[label]
            elif isinstance(label, str) or label.isNull():
                return "Undefined: {}".format(label)
        
        if isinstance(label_id, list):
            labels = []
            for i in label_id:
                labels.append(label_name(i))
        else:
            labels = label_name(label_id)
            
        # reduce to single label
        if len(labels) == 1:
            return labels[0]
        else:
            return labels
        
    def row2text(self, idx):
        impath, label = self.data[idx]
        labels = self.parseLabel(label)
        item_class = self.id2label(labels)
        item_text = "{} -> label: {}".format(impath, item_class)
        return item_text
    
    def populateList(self):
        for i in range(len(self.data)):
            item = self.row2text(i)
            self.listWidget.addItem(item)
            
    def updateItem(self):
        itemText = self.row2text(self.current)
        item = self.listWidget.item(self.current)
        
        if item.text() != itemText:
            self.changesSaved = False
            item.setText(itemText)       
    
    def refreshCheckboxes(self):
        if self.haveLabels:
            for label, checkbox in enumerate(self.checkboxes):
                if label in self.labels:
                    checkbox.setChecked(True)
                else:
                    checkbox.setChecked(False)
                    
    def getValidLabels(self):
        self.labels = [i for i, c in enumerate(self.checkboxes) if c.isChecked()]
        
        if not self.haveLabels:
            self.labels.append(self.labels_default)
        
        return self.labels
    
    def processLabels(self):
        self.getValidLabels()
        self.refreshCheckboxes()
        out_labels = []
        
        if self.isMultiLabel: #multi label
            for l in self.labels:
                out_labels.append(self.labels_id[l])
        elif self.isSingleLabel:
            out_labels = self.labels_id[self.labels[0]]
        
        # self.dataset.iloc[self.current]['class'] = out_labels
        self.data[self.current] = out_labels
            
    def updateImageInfo(self):
        image_summ = "Image Nro. {} of {}".format(self.current +1, 
                                                  len(self.data))
        self.imagesInfo.setText(image_summ)
        
    def showImage(self):
        img_path, label = self.data[self.current]
        
        # idx = self.current
        # row = self.dataset.iloc[idx]
        impath = os.path.join(self.data.root_path, img_path)
        text_height = 20
        self.labels = self.parseLabel(label)
        
        # check if image exist
        if not os.path.isfile(impath):
            print('Error!', impath, 'Not Found!')
            return False
    
        img = cv2.imread(impath)
        #define the screen resulation
        screen_res = 800, 600
        # must resize?
        # if img.shape[1] > screen_res[0] or img.shape[0] > screen_res[1]: 
        scale_width = screen_res[0] / img.shape[1]
        scale_height = screen_res[1] / img.shape[0]
        scale = min(scale_width, scale_height)
     
        #resized window width and height
        window_width = int(img.shape[1] * scale)
        window_height = int(img.shape[0] * scale)
     
        #resize the window according to the screen resolution
        cv2.resizeWindow("Image", window_width, window_height)
     
        # draw labels
        if self.haveLabels:
            for i, l in enumerate(self.labels):
                if not isinstance(l, int):
                    continue
                y_pos = text_height + (text_height *i) + (5 *i)
                cv2.putText(img, text=self.labels_name[l], org=(3, y_pos), 
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=0.70, color=(255, 0, 0), thickness=2)
        
        cv2.imshow("Image", img)
        
    def processImage(self):
        self.updateImageInfo()
        self.showImage()
        self.refreshCheckboxes()
        
    def launchSaveChanges(self):
        if not self.changesSaved:
            saveDialog = MessageDialog('Not saved changes!', 
                        'Some labeled images were not saved, do you want to save the changes?')
            if saveDialog.exec_():
                # save csv
                self.data.save()
        
    def closeEvent(self, event):
        # stop process
        self.stopLabeling()                
        event.accept() # let the window close
        
    
def main():
   app = QApplication(['Simple Labeler'])
   labeler = LabelerWindow()
   labeler.show()
   app.exec_()
   cv2.destroyAllWindows()
	
if __name__ == '__main__':
   main()
