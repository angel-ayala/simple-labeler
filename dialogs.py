#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 22:46:06 2020

@author: Angel Ayala <angel4ayala [at] gmail.com>
"""
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QSpacerItem


class CsvNameDialog(QDialog):
    
    def __init__(self):
        super(CsvNameDialog, self).__init__()
        self.createForm()
        
        self.setWindowTitle("Create CSV file")
        
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        
        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.formGroup)
        self.layout.addWidget(buttonBox)
        self.setLayout(self.layout)
        
        
    def createForm(self):
        layout = QFormLayout()
        
        self.filename = QLineEdit('dataset.csv')
        self.have_labels = QCheckBox()
        
        layout.addRow('Filename', self.filename)
        layout.addRow('Subfolders are labels', self.have_labels)
        
        self.formGroup = QGroupBox('Options')
        self.formGroup.setLayout(layout)
        
    def accept(self):        
        self._output = self.filename.text(), self.have_labels.isChecked()
        super(CsvNameDialog, self).accept()
    
    def getValues(self):
        return self._output


class MessageDialog(QDialog):

    def __init__(self, title, msg):
        super(MessageDialog, self).__init__()
        
        self.setWindowTitle(title)
        self.layout = QVBoxLayout()
        
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        # vertival space
        self.layout.addItem(QSpacerItem(10, 10))
        
        label = QLabel(msg)
        self.layout.addWidget(label)
        
        # vertival space
        self.layout.addItem(QSpacerItem(10, 10))
        
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)