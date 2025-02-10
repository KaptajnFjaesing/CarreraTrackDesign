#%%
from carreratrackdesign.TrackGenerator import TrackGenerator

# Tolerance for checking if a lap is completed
lap_tolerance = 0.05
orientation_tolerance = 0.01

# Physical dimensions (in meters) for Carrera 1:32 and 1:24 
turn_section_radius = 0.3
straight_section_length = 0.345

# Initialize the TrackGenerator class
track_gen = TrackGenerator(
    turn_section_radius = turn_section_radius,
    straight_section_length = straight_section_length,
    lap_tolerance = lap_tolerance,
    orientation_tolerance = orientation_tolerance,
    )

#%%

# The maximum number of tracks for a given split of turns into left/right (to control the computational load)
maximum_number_of_tacks = 20

# The maximum time (in seconds) spent on each split of turns into left/right (to further control the computational load)
max_time_per_split = 30

# User specified input of available track sections
number_of_turn_sections = 12
number_of_straight_sections = 16

# User specified sequence the track is required to begin with
starting_sequence = "RRRR"

# Generate the set of unique tracks
track_gen.generate_unique_tracks(
    number_of_turn_sections = number_of_turn_sections,
    number_of_straight_sections = number_of_straight_sections,
    starting_sequence =  starting_sequence,
    maximum_number_of_tacks = maximum_number_of_tacks,
    max_time_per_split = max_time_per_split
    )

# %%
# Generate figures of the generated tracks

path = './test/figures/generated_tracks.png'

track_gen.generate_track_figures(path)

# %%
