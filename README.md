[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/QwFWBwI4)

# Task 1 Gathering Training Data
## How to run
 - run [gather_data.py](./gather_data.py) via `python .\gather_data.py` 
 - follow the console instructions
    - 1st enter your name (will be used in output file name)
    - 2nd enter the sensor placement (1 = hand, 2 = pocket)
    - follow through the process the programm will tell you on the console which activity comes next
    - when you want to start an activity you need to press button 1 on the DIPPID device
    - after pressing the button you have 3 seconds to set up and start the acitivity before the recording starts
    - after 10 seconds of recording the recording is stopped and it will automatically continue with either the next set, the next sampling rate or the next acitivity
 - files will be generated in the directory [`.\data\your_name\`](./data/marcel/) 
 - you need to run the programm twice (1x sensor placement = hand and 1x sensor placement = pocket) to capture all data for the assignment
 - after that the folder with your name should include everything you need and you can upload it to the data collection 

# Task 2
## Documentation
- you can find the model testing and documentation in the notebook [classifier_testing.ipynb](./classifier_testing.ipynb)
## How to run
- run [fitness_trainer.py](./fitness_trainer.py) via `python .\fitness_trainer.py`
   - you can also optionally add your name `python .\fitness_trainer.py your_name` so the programm checks if your gyroscope data needs radian conversion
   - names for radian conversion are hardcoded (lennart, maximilian)
- prepare the DIPPID app for sensor input the port should be `5700`
- when the programm runs and the loading text disappears you can simply start performing one of the exercises and the program will show you the detection and track the time performing the same exercise
- for lifiting and rowing you need to put your phone in your hand to capture the movement
- there is not further user interaction required
- if you fail (and another exercise is detected) or stop the timer will restart for the next acitivity you perform  