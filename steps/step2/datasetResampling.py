import os
import pathlib

import pymeshlab as ml

############################################################################################
# Downsampling through cluster decimation and upsamplinh through catmull-clark
############################################################################################
# meshFile --> file path to object file from root folder
# aim --> desired amount of vertices that the object will end up having
# deviation --> tolerated amount of deviation from the aim (decimal)
def resample(meshFile, meshClass, aim=1000, deviation=0.9):
    # create class resampled folder if there isnt one
    classfolderPath = os.path.join("ShapeDatabase_INFOMR-resampled", meshClass)
    pathlib.Path(classfolderPath).mkdir(exist_ok=True) 

    # mesh initiation
    ms = ml.MeshSet()
    ms.load_new_mesh("ShapeDatabase_INFOMR-master/" + meshClass + "/" + meshFile)
    m = ms.current_mesh()

    vertices =  m.vertex_number()


    # ------ Upsampling ------
    if vertices < (aim * deviation):
        # print(f"[Started] upsample: {meshFile} with {vertices} vertices")

        # connect non-connected parts of the mesh
        ms.apply_filter("meshing_repair_non_manifold_edges")
        ms.apply_filter("meshing_repair_non_manifold_vertices")
        
        # create more vertices and faces
        # TODO: while weg?
        # while vertices < (aim * deviation):
        # print("test")
        ms.apply_filter("meshing_surface_subdivision_catmull_clark")
        
        vertices =  ms.current_mesh().vertex_number()
            # print(f"[While] upsample: {vertices} vertices")
        
    #     print(f"[Finished] upsample: {meshFile} with {vertices} vertices")

    # else:
    #      print(f"[Skipped] upsample: {meshFile} with {vertices} vertices")

    # cluster vertices together again (to patch holes that prevent this program from saving)
    ms.apply_filter("meshing_decimation_clustering")

    # ------ Downsampling ------
    if vertices > ((aim * (1 - deviation)) + aim):
        # print(f"[Started] downsample: {meshFile} with {vertices} vertices")

        numFaces = 100 + 2* aim

        # keep on downsampling until aim is reached
        while (ms.current_mesh().vertex_number() > aim):
            ms.apply_filter('meshing_decimation_quadric_edge_collapse', targetfacenum=numFaces, preservenormal=True)

            vertices =  ms.current_mesh().vertex_number()
            # print(f"[While] downsample: {vertices} vertices")

            # keep on reestimating the number of faces
            numFaces = numFaces - (ms.current_mesh().vertex_number() - aim)

        print(f"[Finished] downsample: {meshFile} with {vertices} vertices")
    
    else:
        print(f"[Skipped] downsample: {meshFile} with {vertices} vertices")

    # save the resampled shape
    ms.save_current_mesh("ShapeDatabase_INFOMR-resampled/" + meshClass + "/" + meshFile)



############################################################################################
# The resampling engine (resamples every object file from the dataset)
############################################################################################

# # extremely small birb object example
# test_obj_name = "m43.obj"
# test_class_name = "Bird"
# resample(test_obj_name, test_class_name, aim=1000, deviation=0.9)


# create main resampled folder if there isnt one
pathlib.Path("ShapeDatabase_INFOMR-resampled").mkdir(exist_ok=True) 

# access dataset folder with class folders
dataset = os.listdir("ShapeDatabase_INFOMR-master")
dataset.remove("class_sizes_plot.png")
dataset.remove("stats.txt")

for idx, class_name in enumerate(dataset):
    class_folder = os.listdir("ShapeDatabase_INFOMR-master/" + class_name)

    print(f"----------------------------[ Class {class_name} ({idx + 1}/{len(dataset)}) ]----------------------------")
    
    for obj_name in class_folder:
        resample(obj_name, class_name, aim=1000, deviation=0.9)

    print("\n")
    