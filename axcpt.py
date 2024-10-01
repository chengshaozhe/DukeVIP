from psychopy import visual, core, event, data, gui
import random

# Set up a window
win = visual.Window(size=(800, 600), color=(1, 1, 1), units='pix')

# Define stimuli as images (Make sure the image files are in the same directory or provide full paths)
stimuli_images = {
    'A': 'A.png',
    'B': 'B.png',
    'X': 'X.png',
    'Y': 'Y.png'
}

# Instructions
instruction_text = visual.TextStim(win, text="Press space when 'X' follows 'A'. Press any key to start.", color=(-1, -1, -1))
instruction_text.draw()
win.flip()
event.waitKeys()

# Trial structure (AX trials and non-AX trials)
trials = [
    {'cue': 'A', 'probe': 'X', 'correct_response': 'space'},  # AX trial
    {'cue': 'A', 'probe': 'Y', 'correct_response': None},     # AY trial
    {'cue': 'B', 'probe': 'X', 'correct_response': None},     # BX trial
    {'cue': 'B', 'probe': 'Y', 'correct_response': None}      # BY trial
]

# Repeat trials for practice (adjust number of repetitions if needed)
trials *= 5  # 5 repetitions of each trial type

# Randomize trial order
random.shuffle(trials)

# Prepare response storage
response_data = []

# Start the trial loop
for trial in trials:
    # Present the cue as an image
    cue_image = visual.ImageStim(win, image=stimuli_images[trial['cue']])
    cue_image.draw()
    win.flip()
    core.wait(0.5)  # Cue duration (500ms)
    
    # Inter-stimulus interval (ISI)
    win.flip()
    core.wait(0.2)  # ISI (200ms)
    
    # Present the probe as an image
    probe_image = visual.ImageStim(win, image=stimuli_images[trial['probe']])
    probe_image.draw()
    win.flip()
    
    # Record response
    response = event.waitKeys(maxWait=1.0, keyList=['space', 'escape'], timeStamped=core.Clock())  # Probe duration (1s)
    
    # Check for exit
    if response and response[0][0] == 'escape':
        break
    
    # Determine correctness
    if response:
        key, rt = response[0]
        if trial['correct_response'] and key == trial['correct_response']:
            correct = True
        else:
            correct = False
    else:
        correct = trial['correct_response'] is None
    
    # Store the result
    response_data.append({
        'cue': trial['cue'],
        'probe': trial['probe'],
        'response': key if response else 'no_response',
        'reaction_time': rt if response else None,
        'correct': correct
    })
    
    # Inter-trial interval (ITI)
    win.flip()
    core.wait(0.5)

# End the experiment
end_text = visual.TextStim(win, text="Task complete. Thank you!", color=(-1, -1, -1))
end_text.draw()
win.flip()
core.wait(2.0)

# Close everything
win.close()
core.quit()

# Print the response data (or save to file)
for trial in response_data:
    print(trial)
