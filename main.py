#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 00:14:34 2020

@author: Angel Ayala <angel4ayala [at] gmail.com>
"""

import os
import cv2
import ast
import pandas as pd
from PyQt5.QtCore import Qt
# from PyQt5.QtCore import QSize
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


class LabelerWindow(QMainWindow):
    
    def __init__(self, *args, **kwargs):
        super(LabelerWindow, self).__init__(*args, **kwargs)
        self.csv_path = None
        self.filename = None
        self.current = 0
        self.labels = []
        self.labels_id = ['none', 'fire', 'smoke']
        self.labels_name = ['None', 'Fire', 'Smoke']
        
        self.setWindowTitle("Simple Labeler")
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
        
    def embedList(self):
        
        self.listWidget = QListWidget(self.mainWidget)
        self.listWidget.itemSelectionChanged.connect(self.onSelectImage)
        
        self.mainLayout.addWidget(self.listWidget)
        
    def embedButtons(self):   
        # image navigation buttons
        layout = QHBoxLayout()
        
        prev_button = QPushButton(self.mainWidget)
        prev_button.setIcon(QIcon("assets/arrow-180.png"))
        prev_button.setStatusTip("See previous image")
        prev_button.setShortcut("A")
        prev_button.clicked.connect(self.onPrevImage)
        layout.addWidget(prev_button)
        
        next_button = QPushButton(self.mainWidget)
        next_button.setIcon(QIcon("assets/arrow.png"))
        next_button.setStatusTip("See next image")
        next_button.setShortcut("D")
        next_button.clicked.connect(self.onNextImage)        
        layout.addWidget(next_button)
        
        self.mainLayout.addLayout(layout)
        
        
    def embedToolBar(self):
        toolbar = QToolBar("Main Toolbar", self)
        self.addToolBar(toolbar)
        
        # read
        button_action = QAction(QIcon("assets/database--arrow.png"), "CSV File", self)
        button_action.setStatusTip("Choose dataset CSV file")
        button_action.triggered.connect(self.onImportCsv)
        toolbar.addAction(button_action)
        
        # write
        button_action = QAction(QIcon("assets/disk.png"), "Save CSV File", self)
        button_action.setStatusTip("Write changes to dataset CSV file")
        button_action.triggered.connect(self.onSave)
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
        
    def onSave(self, button):
        file_path = os.path.join(self.base_path, self.filename)
        self.dataset.to_csv(file_path, index=None)
        # self.reset
        
    def onImportCsv(self, s):
        self.reset()
        
        dialog = QFileDialog.getOpenFileName(self, 'Open file', 
                                                    os.path.expanduser("~"),
                                                    "CSV files (*.csv)")
        
        if os.path.isfile(dialog[0]):
            self.csv_path = dialog[0]
            # get dataframe
            self.dataset = pd.read_csv(self.csv_path)
            # get images base path
            self.base_path = self.csv_path.split(os.path.sep)
            self.filename = self.base_path[-1]
            self.base_path = str(os.path.sep).join(self.base_path[:-1])
            # populate list for selection
            self.populateList()
            # initiate image visor
            cv2.namedWindow("Image", cv2.WINDOW_NORMAL)            
            # process first image
            self.listWidget.setCurrentRow(0)
            
            
    def onNextImage(self, s):
        if self.current +1 < len(self.dataset):
            self.listWidget.setCurrentRow(self.current +1)        
        
    def onPrevImage(self, s):        
        if self.current >= 1:
            self.listWidget.setCurrentRow(self.current -1)
    
    def onSelectImage(self):
        if self.current > -1:
            self.processLabels()
            # update labels
            self.updateItem()
        self.current = self.listWidget.currentRow()
        self.processImage()
        self.onSave(None)
        
    def populateList(self):
        for idx, row in self.dataset.iterrows():
            item = "{} -> label: {}".format(
                os.path.join(row['folder_path'], row['image_id']),
                row['class'])
            self.listWidget.addItem(item)
            
    def updateItem(self):
        idx = self.current
        row = self.dataset.iloc[idx]
        itemText = "{} -> label: {}".format(
                os.path.join(row['folder_path'], row['image_id']),
                row['class'])
        
        item = self.listWidget.item(idx)
        
        if item.text() != itemText:
            item.setText(itemText)       
    
    def refreshCheckboxes(self):
        if len(self.labels) > 0:
            for label, checkbox in enumerate(self.checkboxes):
                if label in self.labels:
                    checkbox.setChecked(True)
                else:
                    checkbox.setChecked(False)
                    
    def getValidLabels(self):
        self.labels = [i for i, c in enumerate(self.checkboxes) if c.isChecked()]
        
        if len(self.labels) > 1 and (0 in self.labels):
            self.labels.remove(0)
        
        return self.labels
    
    def processLabels(self):
        self.getValidLabels()
        self.refreshCheckboxes()
        out_labels = []
        
        if len(self.labels) > 1:
            for l in self.labels:
                out_labels.append(self.labels_id[l])
        elif len(self.labels) == 1:
            out_labels = self.labels_id[self.labels[0]]
        
        self.dataset.iloc[self.current]['class'] = out_labels
            
    def updateImageInfo(self):
        self.imagesInfo.setText(
                "Image Nro. {} of {}".format(self.current +1,
                                             len(self.dataset))
                )
        
    def showImage(self):
        idx = self.current
        row = self.dataset.iloc[idx]
        impath = os.path.join(self.base_path, row['folder_path'],
                              row['image_id'])
        text_height = 20
        self.labels = self.parseLabel(row['class'])
        
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
     
        # write labels
        for i, l in enumerate(self.labels):
            y_pos = text_height + (text_height *i) + (5 *i)
            cv2.putText(img, text=self.labels_name[l], org=(3, y_pos), 
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.70, color=(255, 0, 0), thickness=2)
        
        cv2.imshow("Image", img)
        
    def parseLabel(self, label_name):
        if label_name is None:
            return [0]
        
        if isinstance(label_name, str) and '[' in label_name: # is a list
            label_name = ast.literal_eval(label_name)
            
        if isinstance(label_name, list):
            label = []
            for l in label_name:
                label.append(self.labels_id.index(l))
        else:
            label = [self.labels_id.index(label_name)]
            
        return label
        
    def processImage(self):
        self.updateImageInfo()
        self.showImage()
        self.refreshCheckboxes()
        
    def reset(self):
        self.csv_path = None
        self.filename = None
        self.current = -1
        self.labels = []
        self.csv_path = None
        self.dataset = None
        self.base_path = None
        self.imagesInfo.setText("Images")
        cv2.destroyAllWindows()
        

def main():
   app = QApplication([])
   labeler = LabelerWindow()
   labeler.show()
   app.exec_()
   cv2.destroyAllWindows()
	
if __name__ == '__main__':
   main()
