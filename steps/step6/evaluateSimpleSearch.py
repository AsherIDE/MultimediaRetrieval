import os

from simpleSearch import searchObject

import pandas as pd




df = pd.read_csv("steps/AxelHoekje/dataBaseFinal.csv")

results = {
    0: 0,
    1: 0,
    2: 0,
    3: 0,
    4: 0,
    5: 0,
    6: 0,
    7: 0,
    8: 0,
    9: 0,
    10: 0
}
iteration = 0
for object in df.iterrows():
    # create the features for the search query
    object_features = []
    # print(object[1]["name"]) # name of class
    object_features.append(object[1]["surfaceAreaObj"])
    object_features.append(object[1]["compactnessObj"])
    object_features.append(object[1]["rectangularityObj"])
    object_features.append(object[1]["diameterObj"])
    object_features.append(object[1]["convexityObj"])
    object_features.append(object[1]["eccentricityObj"])
    object_features.append(eval(object[1]["A3"]))
    object_features.append(eval(object[1]["D1"]))
    object_features.append(eval(object[1]["D2"]))
    object_features.append(eval(object[1]["D3"]))
    object_features.append(eval(object[1]["D4"]))

    object_class = object[1]["class"]
    
    # fetch results
    result = searchObject(100000, 93, object_features)

    top10_classes = result.distances.head(10)["class"].tolist()
    class_overlap = top10_classes.count("AircraftBuoyant")

    results[class_overlap] += 1

    iteration += 1
    print(f"[Info]: {iteration} / 2483 items done ({round((iteration / 2483) * 100, 2)}%) --> {results}")

print("\n--------------------------------------------------------------------------------------------")
print(results)


# [Info]: 213 / 2483 items done (8.58%) --> {0: 200, 1: 8, 2: 1, 3: 3, 4: 1, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
# [Info]: 942 / 2483 items done (37.94%) --> {0: 894, 1: 34, 2: 7, 3: 6, 4: 1, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}

# zonder standardization
# [Info]: 213 / 2483 items done (8.58%) --> {0: 187, 1: 13, 2: 11, 3: 2, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
# [Info]: 274 / 2483 items done (11.04%) --> {0: 242, 1: 16, 2: 13, 3: 3, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}