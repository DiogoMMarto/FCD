import json

from open_site import tfidf


with open("documents.txt", "r") as f:
    documents = json.loads(f.read())

tfi_mat , tfi_names = tfidf(documents,max_features=5000,min_df=5, max_df=0.9)
from sklearn.decomposition import TruncatedSVD

# Reduce dimensions to 300 components
svd = TruncatedSVD(n_components=3)
reduced_tfidf = svd.fit_transform(tfi_mat)
# plot
import matplotlib.pyplot as plt

# 3D plot
fig = plt.figure(figsize=(16, 9))
ax = fig.add_subplot(111, projection='3d')

# Scatter plot
ax.scatter(
    reduced_tfidf[:10000, 0],  # X-axis
    reduced_tfidf[:10000, 1],  # Y-axis
    reduced_tfidf[:10000, 2],  # Z-axis
    c='blue',             # Color
    marker='o',           # Marker style
    s=10                  # Marker size
)

# Label axes
ax.set_xlabel('SVD Component 1')
ax.set_ylabel('SVD Component 2')
ax.set_zlabel('SVD Component 3')
ax.set_title('3D Scatter Plot of Reduced TF-IDF Features')
plt.show()
