import flywheel

# Copy your id here.
user_id = ''
fw = flywheel.Client(user_id)

# Get the Flywheel Example Utility gear
gear = fw.lookup('gears/pbrt-gear-analysis/0.3.2')
gear.print_details()

# This part is used for testing analysis gear
session = fw.lookup('wandell/Graphics test/test subject/test session') # Change what you want to test.
inputs = {}
config = {}
analysis_id = gear.run(analysis_label = 'no filter test', config=config, inputs=inputs, destination=session)
print(analysis_id)
# print(session)
# Here are just use some examples.
session = fw.lookup('wandell/Graphics test/batchtest/batchtest')
inputs = {}
config = {'scene_type':'complicate', 'pbrt_select':'depth', 'keyword':'suburb'}
# 'analysis_id' could be change as well.
analysis_id = gear.run(analysis_label = 'filter test', config=config, inputs=inputs, destination=session)
print(analysis_id)
