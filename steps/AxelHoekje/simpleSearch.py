import os

import pymeshlab as ml # this import has to be over here, even though it appears like its not being used

import pandas as pd
import numpy as np

from tkinter import Tk
from tkinter.filedialog import askopenfilename

from fullNormalize import ShapeNormalizer
from dataResampleFinal import resample
from singleObjectCalcFinal import ObjectCalculations

from scipy.stats import wasserstein_distance

# 1. ask for INPUT .obj file
# 2. resample and normalize INPUT
# 3. extract INPUT features
# 4. create feature vector for INPUT

# 5. calculate similarity between INPUT and DATASET by normalization [0, &] or [0, 1]


class searchObject:
    def __init__(self, bins, n, search_object_features):
        self.bins = bins
        self.n = n

        self.single_val_features = ["surfaceAreaObj","compactnessObj","rectangularityObj","diameterObj","convexityObj","eccentricityObj"]
        self.hist_features = ["A3","D1","D2","D3","D4"]

        self.file_path = ""
        self.temp_file_path = ""
        self.features = {}

        self.distances = {}

        self.load(search_object_features)


    def load(self, search_object_features):
        # Hide the main tkinter window
        root = Tk()
        root.withdraw()
        
        if search_object_features == None:

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

            # prepare object for comparison task
            self.preprocess()
            self.normalizedfeatures()
        else:
            # fill in self.features with search_object_features
            self.features = {
                "surfaceAreaObj": search_object_features[0],
                "compactnessObj": search_object_features[1],
                "rectangularityObj": search_object_features[2],
                "diameterObj": search_object_features[3],
                "convexityObj": search_object_features[4],
                "eccentricityObj": search_object_features[5],
                "A3": search_object_features[6],
                "D1": search_object_features[7],
                "D2": search_object_features[8],
                "D3": search_object_features[9],
                "D4": search_object_features[10]
            }
            print("[Info] features: search object features extracted for search task!")

            
        # compare object to dataset
        self.compare()

        # get a single distance score per object
        self.combineFeatureDistances()

    def preprocess(self):
        file_path_list = self.file_path.split("/")
        obj_name = file_path_list[-1]
        obj_class = file_path_list[-2]
        
        resample(obj_name, obj_class, aim=4000, deviation=0.9, searchTask=True)
        
        temp_file_path_in = os.path.join(os.getcwd(), "steps\\step4\\temp.obj")
        temp_file_path_out = os.path.join(os.getcwd(), "steps\\step4")

        self.temp_file_path = temp_file_path_in

        normalizer = ShapeNormalizer()
        normalizer.select_and_normalize_single_file(temp_file_path_out, temp_file_path_in) 


    def normalizedfeatures(self):

        # sget features of preprocessed search object
        calculations = ObjectCalculations(self.temp_file_path, self.bins, self.n)
        self.features = calculations.get_descriptors()
        
        del self.features['convex_hull_volume']
        del self.features['eigenvalues']
        del self.features['obb_volume']

        # load values to standardize with
        df_features_means_stds = pd.read_csv("MultimediaRetrieval\steps\AxelHoekje\searchStandardizationData.csv")

        # standardize single-value features (hist features already done)
        for single_val_feature in self.single_val_features:
            mean = df_features_means_stds.at[0, single_val_feature]
            std = df_features_means_stds.at[1, single_val_feature]

            # update the value itself
            self.features[single_val_feature] = abs((self.features[single_val_feature] - mean) / std)

        print(self.features)

        print(f"[Finished] features: search object feature extraction and normalization complete")


    def compare(self):
        df = pd.read_csv("MultimediaRetrieval\steps\AxelHoekje\dataBaseFinal.csv")

        # euclidean distance (hist features)
        # distance_features = {}
        # for hist_feature in self.hist_features:
        #     source = np.array(self.features[hist_feature])
        #     targets = df[hist_feature]

        #     # iterate every object from the dataset
        #     distance_feature = []
        #     for target in targets:
        #         target = np.array(eval(target))
                
        #         combined = source - target
        #         ss = np.dot(combined.T, combined)
                
        #         distance_feature.append(np.sqrt(ss))
            
        #     distance_features[hist_feature] = distance_feature

        # earth movers distance (hist features)
        distance_features = {}
        for hist_feature in self.hist_features:
            source = np.array(self.features[hist_feature])
            targets = df[hist_feature]

            # iterate every object from the dataset
            distance_feature = []
            for target in targets:
                target = np.array(eval(target))
                
                d = wasserstein_distance(source, target)
                
                distance_feature.append(np.sqrt(d))
            
            distance_features[hist_feature] = distance_feature


        # distance single-value features
        for single_val_feature in self.single_val_features:
            source = self.features[single_val_feature]
            targets = df[single_val_feature]

            # iterate every object from the dataset
            distance_feature = []
            for target in targets:
                distance_feature.append(abs(source - target))

            distance_features[single_val_feature] = distance_feature

        # standardize hist features so they can be compared properly
        standardized_distance_features = {"name": df["name"].to_list(),
                                          "class": df["class"].to_list()}
        for distance_feature_key, distance_feature_values in distance_features.items():
            if distance_feature_key in self.hist_features:
                mean = np.mean(distance_feature_values)
                std = np.std(distance_feature_values)

                # iterate every single value of a single feature
                standardized_distance_feature = []
                for distance_feature_value in distance_feature_values:
                    standardized_distance_feature.append((distance_feature_value - mean) / std)

                standardized_distance_features[distance_feature_key] = standardized_distance_feature
            # ignore single-value features since they have already been normalized
            else:
                standardized_distance_features[distance_feature_key] = distance_feature_values


        # save the data
        self.distances = standardized_distance_features

    def combineFeatureDistances(self):
        df_distances = pd.DataFrame(self.distances)

        # make all distance values positive
        df_distances = pd.concat([df_distances[["name", "class"]], df_distances.iloc[ :, 2:13].abs()], axis=1)
        
        # df_distances = df_distances.drop(["D1"], axis=1)

        # grab mean distance from all features of a single object (row mean)
        df_distances["closeness"] = df_distances.iloc[ :, 2:13].mean(axis=1) # 7 to skip hist features
        # print(df_distances)
        # update distances
        self.distances = df_distances[["name", "class", "closeness"]]
        self.distances = self.distances.sort_values(["closeness"], ascending=True)
        self.distances.to_csv("searchResult.csv", index=False)

        print("[Finished] distances: feature distance computations done")
