import pynput
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener, Key
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import threading
from screeninfo import get_monitors

# Get the screen resolution
monitor = get_monitors()[0]
screen_width, screen_height = monitor.width, monitor.height

# Initialize lists to store x and y coordinates
x_coords = []
y_coords = []

# Counters
mouse_clicks = 0
view_swaps = 0
general_inputs = 0
ping_count = 0

# Set to track pressed keys
pressed_keys = set()

# Define the on_move function to capture mouse movement
def on_move(x, y):
    x_coords.append(x)
    y_coords.append(y)

# Define the on_click function to count mouse clicks
def on_click(x, y, button, pressed):
    global mouse_clicks
    if pressed:
        mouse_clicks += 1

# Define the on_press function to count key presses
def on_press(key):
    global view_swaps, general_inputs, ping_count
    if key not in pressed_keys:  # Only count if the key was not already pressed
        pressed_keys.add(key)
        try:
            if key.char in {'a', 'q', 'w', 'e', 'r', 'd', 'f', '1', '2', '3', '4', '5', '6'}:
                general_inputs += 1
            elif key.char == ' ':
                general_inputs += 1
            elif key.char == '\t':
                general_inputs += 1
            elif key.char == 'v':
                ping_count += 1
        except AttributeError:
            if key in {Key.f1, Key.f2, Key.f3, Key.f4, Key.f5}:
                view_swaps += 1
            elif key == Key.ctrl_l:
                ping_count += 1

# Define the on_release function to remove keys from the set of pressed keys
def on_release(key):
    if key in pressed_keys:
        pressed_keys.remove(key)

# Function to stop the listener gracefully
def stop_listener():
    stop_event.set()
    mouse_listener.stop()
    keyboard_listener.stop()

# Create an event to signal stopping the listener
stop_event = threading.Event()

# Set up the mouse and keyboard listeners
mouse_listener = MouseListener(on_move=on_move, on_click=on_click)
keyboard_listener = KeyboardListener(on_press=on_press, on_release=on_release)
mouse_listener.start()
keyboard_listener.start()

print("Mouse and keyboard tracking started. Press Ctrl+C to stop.")

try:
    # Wait for the stop event
    while not stop_event.is_set():
        stop_event.wait(1)
except KeyboardInterrupt:
    print("Mouse and keyboard tracking stopped.")
    stop_listener()

    # Create a heatmap using seaborn
    heatmap_data, xedges, yedges = np.histogram2d(x_coords, y_coords, bins=(64, 64), range=[[0, screen_width], [0, screen_height]])
    heatmap_data = np.rot90(heatmap_data)
    heatmap_data = np.flipud(heatmap_data)

    # Save the heatmap data to a list of lists
    heatmap_values = heatmap_data.tolist()
    
    # Normalize the heatmap values
    max_value = np.max(heatmap_data)
    normalized_heatmap_values = (heatmap_data / max_value).tolist()

    # Extract border values (2-pixel border)
    border_values = []
    
    # Top and bottom borders
    border_values.extend(heatmap_values[:2])  # Top 2 rows
    border_values.extend(heatmap_values[-2:])  # Bottom 2 rows
    
    # Left and right borders (excluding corners already included)
    for row in heatmap_values[2:-2]:
        border_values.append(row[:2])  # First 2 columns
        border_values.append(row[-2:])  # Last 2 columns

    # Flatten border values list
    flattened_border_values = [val for sublist in border_values for val in sublist]

    # Normalize border values
    max_border_value = max(flattened_border_values)
    normalized_flattened_border_values = [val / max_border_value for val in flattened_border_values]

    # Extract minimap values for the specified range
    minimap = []
    for y in range(46, 61):  # y from 46 to 60
        for x in range(52, 63):  # x from 52 to 62
            minimap.append((x, y, heatmap_values[y][x]))

    # Sum of all inputs
    total_inputs = mouse_clicks + view_swaps + general_inputs + ping_count

    # Calculate averages
    avg_heatmap = np.mean([val for row in heatmap_values for val in row])
    avg_normalized_heatmap = np.mean([val for row in normalized_heatmap_values for val in row])
    
    avg_border = np.mean(flattened_border_values)
    avg_normalized_border = np.mean(normalized_flattened_border_values)
    
    avg_minimap = np.mean([value for _, _, value in minimap])
    avg_normalized_minimap = np.mean([value / max_value for _, _, value in minimap])

    # Print the normalized heatmap values list
    print("Normalized heatmap values (saved to list):")
    for row in normalized_heatmap_values:
        print(' '.join(f'{val:0.2f}' for val in row))

    # Print the normalized border values list
    print("\nNormalized border values (saved to list):")
    print(normalized_flattened_border_values)

    # Print the minimap values
    print("\nMinimap values (saved to list):")
    for x, y, value in minimap:
        print(f"({x}, {y}): {value:.2f}")

    # Print the averages
    print(f"\nAverage heatmap value: {avg_heatmap:.2f} (original), {avg_normalized_heatmap:.2f} (normalized)")
    print(f"Average border value: {avg_border:.2f} (original), {avg_normalized_border:.2f} (normalized)")
    print(f"Average minimap value: {avg_minimap:.2f} (original), {avg_normalized_minimap:.2f} (normalized)")

    # Print the counters and the sum of all inputs
    print(f"\nMouse clicks: {mouse_clicks}")
    print(f"View swaps: {view_swaps}")
    print(f"General inputs: {general_inputs}")
    print(f"Ping count: {ping_count}")
    print(f"Total inputs: {total_inputs}")

    # Plot the heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(heatmap_data, cmap='viridis')
    plt.title('Mouse Movement Heatmap')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.show()

    # AI to determine activity level
    def determine_activity_level(avg_heatmap, avg_border, avg_minimap):

        if avg_heatmap < 0.3:
            print( "Your general movements in the game were not that many. ")
        elif avg_heatmap < 0.7:
            print ("Your general movements in the game were higher than the average. ")
        else:
            print ("Your general movements in the game were very high. ")
        
        if avg_border < 0.3:
            print( "You didnt move your camera that often. ")
        elif avg_border < 0.7:
            print( "You moved your camera often")
        else:
            print( "You moved your camera very often")
        
        if avg_minimap < 0.3:
            print( "You didnt move your camera through minimap very often")
        elif avg_minimap < 0.7:
            print( "You moved your camera through minimap often")
        else:
            print( "You moved your camera through minimap very often")

    # Print the activity level
    determine_activity_level(avg_normalized_heatmap, avg_normalized_border, avg_normalized_minimap)


