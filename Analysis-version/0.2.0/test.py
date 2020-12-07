import flywheel

# Copy your id here.
user_id = ''
fw = flywheel.Client(user_id)

# Get the Flywheel Example Utility gear
gear = fw.lookup('gears/pbrt-gear-analysis/0.1.0')
gear.print_details()

# This part is used for testing analysis gear
session = fw.lookup('wandell/Graphics test/scenes/suburb') # Change what you want to test.
print(session)
# Same as above, nothing there.
inputs = {}
config = {}
# 'analysis_id' could be change as well.
analysis_id = gear.run(analysis_label = 'suburb_analysis', config=config, inputs=inputs, destination=session)
