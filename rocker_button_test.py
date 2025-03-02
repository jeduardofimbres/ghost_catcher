from gpiozero import Button
from signal import pause

# Define the GPIO pins for Up and Down
up_button = Button(23, pull_up=True, bounce_time=0.2)
down_button = Button(22, pull_up=True, bounce_time=0.2)

# Define callback functions for button presses
def on_up_pressed():
    print("Up pressed!")

def on_down_pressed():
    print("Down pressed!")

# Define callback functions for when the button is released
def on_up_released():
    print("Up released!")

def on_down_released():
    print("Down released!")

# Assign the callbacks to the buttons
up_button.when_pressed = on_up_pressed
up_button.when_released = on_up_released

down_button.when_pressed = on_down_pressed
down_button.when_released = on_down_released

print("Waiting for button presses. Press Ctrl+C to exit.")
pause()  # Keeps the program running and listening for events
