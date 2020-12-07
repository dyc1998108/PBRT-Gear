import flywheel

# Copy your id here.
user_id = ''
fw = flywheel.Client(user_id)

# Get the Flywheel Example Utility gear
gear = fw.lookup('gears/pbrt-gear-analysis/0.3.3')
gear.print_details()

# Without any additional configuration
session = fw.lookup('wandell/Graphics test/test subject/test session') # Change what you want to test.
inputs = {}
config = {}
# analysis_label could also be changed.
analysis_id = gear.run(analysis_label = 'no filter test', config=config, inputs=inputs, destination=session)
print(analysis_id)

# With configuration
session = fw.lookup('wandell/Graphics test/batchtest/batchtest') # same here
inputs = {}
config = {'scene_type':'complicate', 'pbrt_select':'mesh', 'keyword':'suburb'}
# analysis_label could also be changed.
analysis_id = gear.run(analysis_label = 'filter test', config=config, inputs=inputs, destination=session)
print(analysis_id)
