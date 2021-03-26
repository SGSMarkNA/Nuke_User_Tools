# README #

This adds these global function callbacks for the Write node Class:

# Create the ICC Knobs when a script makes a Write node...
nuke.addOnCreate(createICCKnobs, (), {}, 'Write')

# Add the knobChanged functions, including adding the AfterFrameRender callback...
nuke.addKnobChanged(knobChanged, (), {}, 'Write')

# Force the addAfterFrameRender callback to be "sticky", by setting it each time the script is loaded...
nuke.addOnCreate(initialize_ICC_Profile_Knob_Callback, (), {}, 'Write')