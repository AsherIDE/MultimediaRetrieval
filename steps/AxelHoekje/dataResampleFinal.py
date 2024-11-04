import os
import pathlib
import pymeshlab as ml

############################################################################################
# Downsampling through cluster decimation and upsamplinh through catmull-clark
############################################################################################
# meshFile --> file path to object file from root folder
# aim --> desired amount of vertices that the object will end up having
# deviation --> tolerated amount of deviation from the aim (decimal)
def resample(meshFile, meshClass, aim=4000, deviation=0.9, searchTask=False):

    # mesh initiation
    ms = ml.MeshSet()
    ms.load_new_mesh("ShapeDatabase_INFOMR-master/" + meshClass + "/" + meshFile)

    vertices =  ms.current_mesh().vertex_number()

    # ------ Upsampling ------
    def upsample():
        upsampling_possible = True

        vertices =  ms.current_mesh().vertex_number()

        # print(f"[Started] upsample: {meshFile} with {vertices} vertices")
        
        # create more vertices and faces
        previous_vertices = vertices
        while vertices < (aim * deviation) and previous_vertices <= vertices:
            
            # connect non-connected parts of the mesh
            ms.apply_filter("meshing_repair_non_manifold_edges")
            ms.apply_filter("meshing_repair_non_manifold_vertices")

            ms.apply_filter("meshing_surface_subdivision_midpoint", iterations=1)

            # cluster vertices together again (to patch holes that prevent this program from saving)
            # ms.apply_filter("meshing_decimation_clustering")
        
            # break loop if further upsampling impossible
            vertices =  ms.current_mesh().vertex_number()
            if previous_vertices == vertices:
                upsampling_possible = False
                break

            previous_vertices = vertices
            
            # print(f"[While] upsample: {vertices} vertices")
        
        # print(f"[Finished] upsample: {meshFile} with {vertices} vertices")

        return upsampling_possible


    # ------ Downsampling ------
    def downsample():
        vertices =  ms.current_mesh().vertex_number()
        
        # print(f"[Started] downsample: {meshFile} with {vertices} vertices")

        numFaces = 100 + 2* aim

        # keep on downsampling until aim is reached
        while vertices > ((aim * (1 - deviation)) + aim):
            ms.apply_filter('meshing_decimation_quadric_edge_collapse', targetfacenum=numFaces, preservenormal=True)

            vertices =  ms.current_mesh().vertex_number()
            # print(f"[While] downsample: {vertices} vertices")

            # only decimate if we are looping again
            if vertices > ((aim * (1 - deviation)) + aim):
                
                # cluster vertices together again (to patch holes that prevent this program from saving)
                ms.apply_filter("meshing_decimation_clustering")

            # keep on reestimating the number of faces
            numFaces = numFaces - (ms.current_mesh().vertex_number() - aim)

            vertices =  ms.current_mesh().vertex_number()
        # print(f"[Finished] downsample: {meshFile} with {vertices} vertices")


    # keep on up- and downsampling until threshold or if its impossible just stop
    prev_resampling_func = ""
    iteration = 0
    while True:
        vertices =  ms.current_mesh().vertex_number()
        
        if vertices < (aim * deviation):
            up_possible = upsample()
            prev_resampling_func = "up"

            if up_possible == False:
                break

        elif vertices > ((aim * (1 - deviation)) + aim):

            if prev_resampling_func in ["", "down"]:
                # connect non-connected parts of the mesh
                ms.apply_filter("meshing_repair_non_manifold_edges")
                ms.apply_filter("meshing_repair_non_manifold_vertices")

            downsample()
            prev_resampling_func = "down"

        else:
           break

        iteration += 1
        if iteration == 5:
            break

    # save the resampled shape
    if searchTask == False:
        ms.save_current_mesh("ShapeDatabase_INFOMR-resampledV2/" + meshClass + "/" + meshFile)
    else:
        ms.save_current_mesh("steps/step4/temp.obj")
    
    vertices =  ms.current_mesh().vertex_number()
    print(f"[Finished] resample: {meshFile} with {vertices} vertices")


############################################################################################
# The resampling engine (resamples every object file from the dataset)
############################################################################################

# extremely small birb object example (requires multiple upsampling loops)
# test_obj_name = "m43.obj"
# test_class_name = "Bird"
# resample(test_obj_name, test_class_name, aim=4000, deviation=0.9, searchTask=True)

# extremely large tree object example  (requires multiple downsampling loops)
# test_obj_name = "D00096.obj"
# test_class_name = "Tree"
# resample(test_obj_name, test_class_name, aim=4000, deviation=0.9)

# small bike example for paper
# test_obj_name = "m1472.obj"
# test_class_name = "Bicycle"
# resample(test_obj_name, test_class_name, aim=4000, deviation=0.9)

# item that was resampled to a way too low value (quadric edge collapses only once, so we can not help it)
# test_obj_name = "D00683.obj"
# test_class_name = "Spoon"
# resample(test_obj_name, test_class_name, aim=4000, deviation=0.9)







# RUNNING ERRORS V2
# test_obj_name = "D00536.obj"
# test_class_name = "Bicycle"
# resample(test_obj_name, test_class_name, aim=4000, deviation=0.9)





# # create main resampled folder if there isnt one
# pathlib.Path("ShapeDatabase_INFOMR-resampledV2").mkdir(exist_ok=True) 

# # access dataset folder with class folders
# dataset = os.listdir("ShapeDatabase_INFOMR-master")
# dataset.remove("class_sizes_plot.png")
# dataset.remove("stats.txt")

# for idx, class_name in enumerate(dataset):
#     # create class resampled folder if there isnt one
#     classfolderPath = os.path.join("ShapeDatabase_INFOMR-resampledV2", class_name)
#     pathlib.Path(classfolderPath).mkdir(exist_ok=True) 

#     class_folder = os.listdir("ShapeDatabase_INFOMR-master/" + class_name)

#     print(f"----------------------------[ Class {class_name} ({idx + 1}/{len(dataset)}) ]----------------------------")
    
#     new_class_folder = os.listdir("ShapeDatabase_INFOMR-resampledV2/" + class_name)
#     for obj_name in class_folder:
#         if obj_name not in new_class_folder:
#             resample(obj_name, class_name, aim=4000, deviation=0.9)

#     print("\n")
    
# print(f"[Finished] resample: script done")