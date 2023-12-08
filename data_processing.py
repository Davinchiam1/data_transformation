import numpy as np
import pandas as pd
import os
from data_loading import Data_loading


# Obtaining data in the upload format and combining them by months with the addition of a timestamp
def marker(column, keywords, row=''):
    """
    Base func for marking rows Dataframe by the presence of keywords.
    Args:
        column (): name of target column.
        keywords (list): list of keywords.
        row (): row in Dataframe

    Returns:
        val (int): returns 0 if no keys detected and 1 if at least 1 is in target column.
    """
    val = 0
    # row = row.lower()
    for keyword in keywords:
        if type(row[column]) is not str:
            val = 0
        else:
            if row[column].lower().find(keyword) == -1:
                val = 0
            else:
                val = 1
                break
    return val


def single_marker(column, key, keywords, row=''):
    """
    Mark a row in a DataFrame by key if any of its keywords detected.
    Args:
        column (str): name of the target column.
        key: keyname for group of keywords.
        keywords (list): list of keywords.
        row (): row in Dataframe

    Returns:
        val: returns 'No mark' if none of the keywords are found,
             or the specified 'key' value if at least one keyword is found in the target column.
    """
    val = marker(column, keywords, row)
    if val == 0:
        val = 'No mark'
    else:
        val = key
    return val




class Data_process:
    """Class for data marking and filtering"""
    def __init__(self):
        self.final_frame = None

    def _filter(self,col_name="", values=[], sort_type='Include'):
        """
            Func for filtering data in dataframe by 1 selected column
            Args:
                col_name (str): name of column in frame to apply filter.
                values (list): list of values to filter
                sort_type (str): Type of sorting, if include - frame will include data with/within values, exclude -
                will exclude data with|within values. Default Include

            Returns:
                None
        """
        data_type=str(self.final_frame[col_name].dtype)
        if data_type == 'int64' or data_type == 'float64':
            if sort_type == 'Include':
                if len(values)==2:
                    self.final_frame=self.final_frame[(self.final_frame[col_name] >= int(values[0])) & (self.final_frame[col_name] <= int(values[1]))]
                elif len(values)==1:
                    self.final_frame = self.final_frame[(self.final_frame[col_name] >= int(values[0]))]
            elif sort_type == 'Exclude':
                if len(values)==2:
                    self.final_frame=self.final_frame[(self.final_frame[col_name] <= int(values[0])) & (self.final_frame[col_name] >= int(values[1]))]
                elif len(values)==1:
                    self.final_frame = self.final_frame[(self.final_frame[col_name] <= int(values[0]))]

        elif data_type == 'object':
            if sort_type == 'Include':
                mask = ~self.final_frame[col_name].isin(values)
            elif sort_type == 'Exclude':
                mask = self.final_frame[col_name].isin(values)
            self.final_frame=self.final_frame[mask]

    def _get_makers(self, column, markers_file, single=False):
        """
            Marking data according to list of markers in .txt file

            Args:
                column (): name of target column.
                markers_file (str): list of keywords.
                single (bool): row in Dataframe

            Returns:
                None
        """
        markers = {}
        # load and process markers from file
        with open(markers_file, "r", encoding='utf8') as file:
            for line in file:
                if line is not None:
                    temp_line = line.split(':')
                    key = temp_line[0][0:-1] if temp_line[0][-1] == ' ' else temp_line[0]
                    keywords_temp = temp_line[1].split(',')
                    keywords = []
                    for keyword in keywords_temp:
                        if keyword[0] == ' ' and keyword[-1] != '\n':
                            keyword = keyword[1:]
                        elif keyword[-1] == '\n' and keyword[0] == ' ':
                            keyword = keyword[1:-1]
                        keywords.append(keyword)
                    markers[key] = keywords

        # choose marking method
        if single:
            for key in markers:
                self.final_frame['marks'] = self.final_frame.apply(
                    lambda row: single_marker(row=row, column=column, keywords=markers[key], key=key), axis=1)
        else:
            for key in markers:
                self.final_frame[key] = self.final_frame.apply(
                    lambda row: marker(row=row, column=column, keywords=markers[key]), axis=1)

    def _to_zero(self):
        """Service function to clear frame"""
        self.final_frame = None

    def use_script(self, read_xlsx=False, directory=None, finalname='./final.xlsx', set_dates=True, markers_file=None,
                   column=None, temp_frame=None, single=False, filepath=None, filter_col=None, values=None, sort_type=None):
        """
            Function for executing a script loading data and marking if necessary.
            Most parameters determine loading method.
            Args:
                read_xlsx (bool): determines whether to read xlsx files. Default False.
                directory (string): path to directory with target files to load.
                finalname (sting): path to save file.
                set_dates (bool): determines whether to set dates from filenames. Default True.
                markers_file (str): list of keywords.
                column (): name of target column.
                temp_frame (pd.Dataframe): passes the dataframe if the method is called in conjunction with others in the
                                           data processing chain.
                single (bool): determines marking method. Default False.
                filepath (string): path to file for loading data from single file.

            Returns:
                None
        """
        if __name__ == "__main__":
            dl = Data_loading()
            self.final_frame = dl.get_data(read_xlsx=read_xlsx, directory=directory, set_dates=set_dates,
                                           filepath=filepath)
        else:
            self.final_frame = temp_frame
        if filter_col is not None:
            self._filter(col_name=filter_col, values=values, sort_type=sort_type)

        if markers_file is not None:
            self._get_makers(column=column, markers_file=markers_file,single=single)
        if self.final_frame.shape[0]>250000:
            self.final_frame.to_csv(finalname+'.csv',index=False, sep=';',encoding='utf-8-sig')
        else:
            self.final_frame.to_excel(finalname+'.xlsx', sheet_name='list1', index=False)
        self._to_zero()

# test = Data_process()

