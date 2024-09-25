import matplotlib.pyplot as plt
import numpy as np

# Data from the table
models = [
    'coremark (base)', 'coremark (custom op)',
    'lstm2 (base)', 'lstm2 (custom op)',
    'magic_wand (base)', 'magic_wand (custom op)',
    'micro_kws_m_fp32 (base)', 'micro_kws_m_fp32 (custom op)',
    'simple_mnist (base)', 'simple_mnist (custom op)',
    'sine_model (base)', 'sine_model (custom op)',
    'text_class (base)', 'text_class (custom op)',
    'umatest (base)', 'umatest (custom op)'
]

total_instructions = [
    3877474, 3805746,
    1296461, 1294461,
    267505, 267804,
    18279566, 18286449,
    85649, 85439,
    1313, 1312,
    43223, 43222,
    2742063, 2742418
]

# Set up figure with subplots
num_models = len(models) // 2
fig, axs = plt.subplots(num_models, 2, figsize=(12, num_models * 3))
axs = axs.flatten()  # Flatten the array for easy indexing

# Plotting bars for each model in separate axes
for i in range(num_models):
    ax = axs[i]
    ax.bar([0, 1], [total_instructions[i * 2], total_instructions[i * 2 + 1]], color=['blue', 'orange'])
    ax.set_title(models[i * 2].split(' (')[0])  # Set the title as the model name
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Base', 'Custom Op'])
    ax.set_ylabel('Total Instructions')

# Adjust layout
plt.tight_layout()

# Save the plot to a file
plt.savefig('./total_instructions_subplots_chart.png')
