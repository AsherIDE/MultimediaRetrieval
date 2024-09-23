import os
import numpy as np
import pandas as pd

############################################################################################
# Load object file (from step1)
############################################################################################
def load_obj(filename):
    vertices = []
    faces = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('v '):
                vertices.append(list(map(float, line.strip().split()[1:])))
            elif line.startswith('f '):
                face = [int(val.split('/')[0]) - 1 for val in line.strip().split()[1:]]
                faces.append(face)
    return np.array(vertices, dtype=np.float32), np.array(faces, dtype=np.int32)

############################################################################################
# Create a dataframe with object information (step 2.1)
############################################################################################
def analyze_dataset(dataset, folder):
    # get bounding box from vertices
    def vertices_to_bbox(vertices):
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        zs = [v[2] for v in vertices]

        return str(min(xs)) + " " + str(max(xs)) + " " + str(min(ys)) + " " + str(max(ys)) + " " + str(min(zs)) + " " + str(max(zs))

    # temporarily store [name, class, faces, vertices, bounding box]
    dataset_analyzed = []

    # analyze shapes -> name, class, vertices, faces, bounding box [xmin, xmax, ymin, ymax, zmin, zmax]
    for class_name in dataset:
        class_folder = os.listdir(folder + "/" + class_name)

        for obj_name in class_folder:
            vertices, faces = load_obj(folder + "/" + class_name + "/" + obj_name)
            
            dataset_analyzed.append([obj_name, class_name, len(vertices), len(faces), vertices_to_bbox(vertices)])

    df = pd.DataFrame(dataset_analyzed, columns=["name", "class", "vertices", "faces", "bbox"])

    return df


# # ------ Original dataset ------

# # access dataset folder with class folders
# folder = "ShapeDatabase_INFOMR-master"
# dataset = os.listdir(folder)
# dataset.remove("class_sizes_plot.png")
# dataset.remove("stats.txt")

# # create the objStats.csv file
# df = analyze_dataset(dataset, folder)
# df.to_csv("steps/step2/objStats.csv", index=False)

# # read the objStats.csv file
# df_found = pd.read_csv("steps/step2/objStats.csv")
# print(df_found)



# # ------ Resampled dataset ------

# # access dataset folder with class folders
# folder = "ShapeDatabase_INFOMR-resampled"
# dataset = os.listdir(folder)

# # create the objStats.csv file
# df = analyze_dataset(dataset, folder)
# df.to_csv("steps/step2/objStatsResampled.csv", index=False)

# # read the objStats.csv file
# df_found = pd.read_csv("steps/step2/objStatsResampled.csv")
# print(df_found)