import os

import pandas as pd

from tkinter import Tk
from tkinter.filedialog import askopenfilename

from step3.fullNormalize import ShapeNormalizer
from step2.datasetResamplingV2 import resample

import time




# df = pd.read_csv("steps/descriptorsResampledNormalisedData.csv")

# print(df)

# 1. ask for INPUT .obj file
# 2. resample and normalize INPUT
# 3. extract INPUT features
# 4. create feature vector for INPUT

# 5. calculate similarity between INPUT and DATASET by normalization [0, &] or [0, 1]


class Engine:
    def __init__(self):
        self.file_path = ""

    def loadObject(self):
        # Hide the main tkinter window
        root = Tk()
        root.withdraw()

        # Open file dialog to select a file
        file_path = askopenfilename(
            filetypes=[("OBJ files", "*.obj")],
            title="Select an OBJ file"
        )

        if not file_path:
            print("[Error] preprocessing: No file selected!")
            return

        # Process the selected file
        print(f"[Started] preprocessing: {file_path}")

        self.file_path = file_path

        self.preprocessObject()
        

    def preprocessObject(self):
        file_path_list = self.file_path.split("/")
        obj_name = file_path_list[-1]
        obj_class = file_path_list[-2]

        resample(obj_name, obj_class, aim=4000, deviation=0.9, searchTask=True)
        time.sleep(5)
        temp_file_path_in = os.path.join(os.getcwd(), "steps\\step4\\temp.obj")
        temp_file_path_out = os.path.join(os.getcwd(), "steps\\step4")

        normalizer = ShapeNormalizer()
        normalizer.select_and_normalize_single_file(temp_file_path_out, temp_file_path_in) 

    def extractfeaturesObject(self):
        # input: file path
        # output: dict --> {feature: value(s)}


        
        return

engine = Engine()
engine.loadObject()









