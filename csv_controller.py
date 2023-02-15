import csv
import os


class csv_read():

    def __init__(self,path):
            self.path = path


    def get_csv(self):
        res = []
        with open(self.path, "rt", encoding="utf-8") as f:
            csv_read = csv.reader(f)
            for line in csv_read:
                res.append(line)
        return res



class csv_write():

    def __init__(self,path):
            self.path = path


    def writerow_csv(self,data):
        if os.path.exists(self.path):
            key_word = "a+"
        else: 
            key_word = "wt"

        with open(self.path, key_word, encoding='utf-8', newline="") as f:
            csv_write = csv.writer(f)
            csv_write.writerow(data)
        return True
    

    def add_by_location(self, data, row, column):
        pass