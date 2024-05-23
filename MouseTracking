import pynput
from pynput.mouse import Listener
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

#lists to store x and y coordinates
x_coords = []
y_coords = []

#capture mouse movement
def on_move(x, y):
    x_coords.append(x)
    y_coords.append(y)

# mouse listener
listener = Listener(on_move=on_move)
listener.start()

print("Mouse tracking started. Press Ctrl+C to stop.")

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Mouse tracking stopped.")
    listener.stop()

    # Create a heatmap 
    heatmap_data, xedges, yedges = np.histogram2d(x_coords, y_coords, bins=(150, 150))
    heatmap_data = np.rot90(heatmap_data)
    heatmap_data = np.flipud(heatmap_data)

    plt.figure(figsize=(8, 6))
    sns.heatmap(heatmap_data, cmap='viridis')
    plt.title('Mouse Movement Heatmap')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.show()
