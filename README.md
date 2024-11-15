# MultimediaRetrieval
Multimedia Retrieval course
IMPORTANT TO NOTE: most files in AxelHoekje are deleted from the comments due to the nature of the final product being based on the created code for each step. Below you can see where the files originated from. The files there do contain comments explaining the code for each step as this is how we worked on the project and in the end one of us created a safe code space where everything could be combined; Thus resulting in "AxelHoekje". 

### Important file discriptions
```
Multimediaretrieval
|
|
steps
└───AxelHoekje (the used files for the final application) 
    |   objLoaderFinal.py --> the final GUI interface combining all steps --> origin step 1
    |   dataResampleFinal.py --> resampling step 2
    |   fullNormalize.py --> normalisation step 3
    |   singleObjectCalcFinal --> feature extraction ObjectCalculatorWithThreads step 3
    |   simpleSearch.py --> simple search step 4
    |   searchANN --> scalability step 5 KNN
    |   advancedSearch.py --> scalability step 5 ANN
    |   All evaluations are done in python notebooks --> evaluation step 6
    |   Multiple csvs containting the dataBaseFinal and completely Normalised version for the descriptors.
└───step1
│   │   objLoaderV2.py -> program to view .obj files
└───step2
│   │   datasetResampling.py -> creates a dataset where vertices deviate less
│   │   datasetAnalyzer.py -> creates a .csv with info on both datasets
│   │   datasetStats.py -> visualizes vertices or faces of a certain .obj class
└───step3
│   | Contains the descriptor calculations using threads and without. Also contains the multiple attempts at creating databases.
└───step4
│   | Contains the files for the simple search
└───step5
│   | Contains the scalability advanced search of KNN and ANN which are used in Axel Hoekje later for the final result. 
└───step6
│   | Contains the files for evaluation of the 2 advanced search that are used later on in Axel Hoekje were all the final results and usages are located.
└───Testing grounds 
    | Contain files which we used to attempt and improve our result by calculating new metrics and swapping them witht the existing like the trimesh volume.
```
