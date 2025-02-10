#%%
from carreratrackdesign.TrackGenerator import TrackGenerator

# Initialize the TrackGenerator class
track_gen = TrackGenerator()

#%%
number_of_turn_sections = 12
number_of_straight_sections = 16

track_gen.generate_unique_tracks(
    starting_sequence =  "SSSS",
    number_of_turn_sections = number_of_turn_sections,
    number_of_straight_sections = number_of_straight_sections
    )

# %%

track_gen.generate_track_figures()

# %%
