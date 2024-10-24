import pandas as pd
import numpy as np

df = pd.read_csv("objDescriptors.csv")

# data collection point for the normalized/standardized data
data = {"name": [name.replace("_normalized", "") for name in df["name"].to_list()], 
        "class": df["class"].to_list()}

standaridization_data = {}

#  standardize all single value features
single_val_features = ["surfaceAreaObj","compactnessObj","rectangularityObj","diameterObj","convexityObj","eccentricityObj"]
for single_val_feature in single_val_features:
    feature_range = df[single_val_feature].to_list()

    feature_range_mean = np.mean(feature_range)
    feature_range_std = np.std(feature_range)

    standaridization_data[single_val_feature] = {"mean": feature_range_mean, "std": feature_range_std}

    print(f"[Before] {single_val_feature}: mean={feature_range_mean} std={feature_range_std}")

    # apply the standardization formula
    standardized_feature_range = []
    for i in feature_range:
        standardized_feature_range.append((i - feature_range_mean) / feature_range_std)
    
    # add standardized feature values to the new dataset
    data[single_val_feature] = standardized_feature_range

    print(f"[After] {single_val_feature}: mean={np.mean(standardized_feature_range)} std={np.std(standardized_feature_range)}")
    
# NOTE: This part has been disabled, since it has already been done before, so it is replaced with this
hist_features = ["A3","D1","D2","D3","D4"]
for hist_feature_name in hist_features:
    hist_feature = df[hist_feature_name].to_list()

    data[hist_feature_name] = hist_feature

# # normalize all histogram data
# hist_features = ["A3","D1","D2","D3","D4"]
# for hist_feature_name in hist_features:
#     hist_feature = df[hist_feature_name].to_list()

#     # iterate a single histogram for a single feature
#     normalized_hist_feature = [] # new hist of all objects of a single feature
#     for hist_i in hist_feature:
#         hist_i = eval(hist_i)

#         sum_hist_i = np.sum(hist_i)
        
#         # iterate single value in histogram
#         normalized_hist_i = [] # new hist of a single object of a single feature
#         for i in hist_i:
#             normalized_hist_i.append(i / sum_hist_i)

#         normalized_hist_feature.append(normalized_hist_i)

#     data[hist_feature_name] = normalized_hist_feature


# construct the normalized dataframe
df_features_normalized = pd.DataFrame(data)

# construct standardization information dataframe to standardize the search input feature
df_standardization_data = pd.DataFrame(standaridization_data)

print(df_features_normalized)
print(df_standardization_data)

df_features_normalized.to_csv("steps/step4/searchDescriptorsNormalized.csv", index=False)
df_standardization_data.to_csv("steps/step4/searchStandardizationData.csv", index=False)