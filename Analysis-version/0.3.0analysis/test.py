import flywheel

# Copy your id here.
user_id = ''
fw = flywheel.Client(user_id)

# Get the Flywheel Example Utility gear
gear = fw.lookup('gears/pbrt-gear-analysis/0.1.0')
gear.print_details()

# This part is used for testing analysis gear
session = fw.lookup('') # Change what you want to test.
print(session)
# Here are just use some examples.
inputs = {}
config = {'scene_type':'complicate', 'pbrt_select':'depth'}
# 'analysis_id' could be change as well.
analysis_id = gear.run(analysis_label = '', config=config, inputs=inputs, destination=session)
