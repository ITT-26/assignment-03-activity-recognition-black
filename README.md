[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/QwFWBwI4)

# Task 1 Gathering Training Data
## How to run
 - run `python .\gather_data.py`
 - follow the console instructions
    - 1st enter your name (will be used in outputted file name)
    - 2nd enter the sensor placement (1 = hand, 2 = pocket)
    - follow through the process the programm will tell you on the console which activity comes next
    - when you want to start an activity you need to press button 1 on the DIPPID device
    - after pressing the button you have 3 seconds to set up and start the acitivity before the recording starts
    - after 10 seconds of recording the recording is stopped and it will automatically continue with either the next set, the next sampling rate or the next acitivity
 - files will be generated in the directory `.\gathered_data\your_name\` 
 - you need to run the programm twice (1x sensor placement = hand and 1x sensor placement = pocket) to capture all data for the assignment
 - after that the folder with your name should include everything you need and you can upload it to the data collection 