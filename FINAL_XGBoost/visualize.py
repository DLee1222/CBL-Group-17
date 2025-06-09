import matplotlib
matplotlib.use('Agg')  # Safe backend for script rendering

import pandas as pd
import matplotlib.pyplot as plt

# Load your predictions file
df = pd.read_csv("../test_predictions_with_covid.csv")

# Scatter plot: Actual vs Predicted
plt.figure(figsize=(10, 6))
plt.scatter(
    df['Burglary_Count'], df['Predicted_Burglary_Count'], alpha=0.5, edgecolors='k'
)
max_val = max(df['Burglary_Count'].max(), df['Predicted_Burglary_Count'].max())
plt.plot([0, max_val], [0, max_val], 'r--', label='Perfect Prediction')

plt.xlabel("Actual Burglary Count")
plt.ylabel("Predicted Burglary Count")
plt.title("Predicted vs Actual Burglary Counts")
plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()  ← remove or comment this
plt.savefig("test_predictions.png")

