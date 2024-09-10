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

# get bounding box from vertices
def vertices_to_bbox(vertices):
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    zs = [v[2] for v in vertices]

    return str(min(xs)) + " " + str(max(xs)) + " " + str(min(ys)) + " " + str(max(ys)) + " " + str(min(zs)) + " " + str(max(zs))

# access dataset folder with class folders
dataset = os.listdir("ShapeDatabase_INFOMR-master")
dataset.remove("class_sizes_plot.png")
dataset.remove("stats.txt")

# temporarily store [name, class, faces, vertices, bounding box]
dataset_analyzed = []

# analyze shapes -> name, class, vertices, faces, bounding box [xmin, xmax, ymin, ymax, zmin, zmax]
for class_name in dataset:
    class_folder = os.listdir("ShapeDatabase_INFOMR-master/" + class_name)

    for obj_name in class_folder:
        vertices, faces = load_obj("ShapeDatabase_INFOMR-master/" + class_name + "/" + obj_name)
        
        dataset_analyzed.append([obj_name, class_name, len(vertices), len(faces), vertices_to_bbox(vertices)])

# create the objStats.csv file
df = pd.DataFrame(dataset_analyzed, columns=["name", "class", "vertices", "faces", "bbox"])
df.to_csv("steps/step2/objStats.csv", index=False)

# read the objStats.csv file
df_found = pd.read_csv("steps/step2/objStats.csv")
print(df_found)