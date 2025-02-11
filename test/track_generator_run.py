#%%
from carreratrackdesign.TrackGenerator import TrackGenerator

# Tolerance for the lap completion (how close the track ends where it started)
lap_tolerance = 0.05

# Tolerance for the orientation (how close the track's orientation is to the starting orientation)
orientation_tolerance = 0.01

# Radius of the turn sections in the track
turn_section_radius = 0.3

# Length of the straight sections in the track
straight_section_length = 0.345

# Initialize the TrackGenerator with the specified parameters
track_gen = TrackGenerator(
    turn_section_radius=turn_section_radius,
    straight_section_length=straight_section_length,
    lap_tolerance=lap_tolerance,
    orientation_tolerance=orientation_tolerance,
)

#%%
# Maximum number of unique tracks to generate
maximum_number_of_tracks = 50

# Maximum time allowed per split during track generation (in seconds)
max_time_per_split = 60

# Whether to allow intersections in the generated tracks
allow_intersections = False

# Number of turn sections to include in the track
number_of_turn_sections = 12

# Number of straight sections to include in the track
number_of_straight_sections = 16

# Starting sequence of the track (e.g., "RRRR" for four right turns)
starting_sequence = "SS"

# Generate unique tracks with the specified parameters
track_gen.generate_unique_tracks(
    number_of_turn_sections=number_of_turn_sections,
    number_of_straight_sections=number_of_straight_sections,
    starting_sequence=starting_sequence,
    allow_intersections=allow_intersections,
    maximum_number_of_tracks=maximum_number_of_tracks,
    max_time_per_split=max_time_per_split
)

#%%
# Path to save the generated track figures
path = './test/figures/generated_tracks.png'

# Generate and save the track figures to the specified path
track_gen.generate_track_figures(path)

# %%
