import pickle
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import numpy as np

# Load model from pickle file
with open("model.pkl", "rb") as f:
    model: NearestNeighbors = pickle.load(f)

# Load user data
user_df = pd.read_parquet("user.parquet")

# Load restaurant data
restaurant_df = pd.read_parquet("restaurant.parquet").set_index("index")

import os

os.environ["ARROW_MEMORY_KLASS"] = "pyarrow._memory.PyMallocAllocator"
os.environ["ARROW_PREALLOCATE"] = "true"