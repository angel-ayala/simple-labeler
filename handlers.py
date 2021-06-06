#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 00:51:40 2020

@author: Angel Ayala <angel4ayala [at] gmail.com>
"""
import os
import ast
import pandas as pd


class SearchHandler:
    """Handler class for searching files inside a root folder."""

    def __init__(self, root_path):
        """Initialize the search handler.

        Parameters
        ----------
        root_path : string
            The root path where search file.

        """
        self.root_path = root_path
        self.elements = []
        self.elements_path = []

    def search(self, folder_path=None, level=0, valid_extensions=None):
        """Search all the files inside the root_path.

        Parameters
        ----------
        folder_path : string, optional
            The path where start or continue the searching.
            The default is None.
        level : int, optional
            The subfolder level. The default is 0.

        Returns
        -------
        list
            the elements found.
        list
            The subfolder of the elements if there is the case.

        """
        if folder_path is None:
            folder_path = self.root_path

        current_path = folder_path.replace(self.root_path, '')
        folder_elems = os.listdir(folder_path)
        # sorting for leave the subfolder at the final
        folder_elems.sort()

        if level == 0:
            print('Navigating', str(os.path.sep).join(
                self.root_path.split(os.path.sep)[-3:]))
        else:
            print('-'*level, current_path.split(os.path.sep)[-1])

        for elem in folder_elems:
            elem_path = os.path.join(folder_path, elem)

            # if is file
            if os.path.isfile(elem_path):
                extension = elem_path.lower().split(".")[-1]

                if (extension in valid_extensions
                   or valid_extensions is None):
                    # filter extension file if must apply
                    self.elements.append(elem)
                    _elm_path = current_path.replace(os.path.sep, '', 1)
                    if _elm_path == '':
                        _elm_path = '.'
                    self.elements_path.append(_elm_path)

            elif os.path.isdir(elem_path):
                # if dir go deeper
                self.search(elem_path, level+1,
                            valid_extensions=valid_extensions)

        return self.elements, self.elements_path

    def searchImages(self):
        """Search only images.

        Valid images considers ['jpg', 'jpeg', 'png', 'gif',
                'tiff', 'bmp'] extensions.

        Returns
        -------
        list
            the images found.
        list
            The subfolder of the images if there is the case.
        """
        valid_extensions = ['jpg', 'jpeg', 'png',
                            'gif', 'tiff', 'bmp']
        return self.search(valid_extensions=valid_extensions)


class DataHandler:
    """Handler class for csv data."""

    def __init__(self, filepath):
        """Initialize the handler.

        Parameters
        ----------
        filepath : string
            The csv file target to write or read the data.
        """
        file_path = filepath.split(os.path.sep)
        self.csv_file = file_path[-1]
        self.root_path = str(os.path.sep).join(file_path[:-1])
        self.loaded = False
        self.data = []

    def __len__(self):
        """Length of the pandas dataframe."""
        return len(self.data)

    def __getitem__(self, idx):
        """Get the image path and label of an element data."""
        # read image
        img_path = os.path.join(self.data.iloc[idx]['folder_path'],
                                self.data.iloc[idx]['image_id'])

        # read label
        label = self.data.iloc[idx]['class']

        return img_path, label

    def __setitem__(self, idx, label):
        """Set the label of an element data."""
        # set label
        self.data.iloc[idx]['class'] = label

        return self[idx]

    def read(self):
        """Load the csv as pandas.DataFrame."""
        # if already loaded, do nothing
        if self.loaded:
            return False

        csv_path = os.path.join(self.root_path, self.csv_file)
        print('Reading', str(os.path.sep).join(
            csv_path.split(os.path.sep)[-2:]))
        dataset_df = pd.read_csv(csv_path)

        self.data = dataset_df
        self.loaded = True

        return self.data

    def create(self, have_labels=False):
        """Create the pandas.DataFrame from the container folder.

        Populate the data from the folder containing the csv file defined in
        the constructor.
        The folder can contain subfolders organizing the images' labels.

        Parameters
        ----------
        have_labels : bool, optional
            if have subfolder organizing the images in labels.
            The default is False.

        Returns
        -------
        pandas.DataFrame
            The dataframe with the images as dataset.

        """
        # search
        searcher = SearchHandler(self.root_path)
        searcher.searchImages()

        # save
        dataset_df = pd.DataFrame(data=searcher.elements, columns=['image_id'])
        dataset_df.insert(0, 'folder_path', searcher.elements_path)

        if have_labels:
            images_path = [p.lower() for p in searcher.elements_path]
            dataset_df.insert(2, 'class', images_path)
        else:
            dataset_df.insert(2, 'class', 'unset')

        self.data = dataset_df.sort_values(
            ['folder_path', 'class', 'image_id'])
        self.loaded = True
        return self.data

    def save(self):
        """Save the pandas.DataFrame into csv."""
        # save file
        csv_path = os.path.join(self.root_path, self.csv_file)
        print('Saving', str(os.path.sep).join(
            csv_path.split(os.path.sep)[-2:]))
        self.data.to_csv(csv_path, index=None)

    def get_stats(self):
        """Get current information about classes of csv file."""
        val_stats = self.data['class'].value_counts()
        labels = map(lambda x: ast.literal_eval(x) if "[" in x else x,
                     val_stats.index)
        qt_by_label = val_stats.to_list()
        val_stats = list(zip(labels, qt_by_label))
        val_stats.sort(key=lambda x: x[0][0] if type(x[0]) is list else x[0])

        return val_stats
