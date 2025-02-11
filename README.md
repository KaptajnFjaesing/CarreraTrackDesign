# CarreraTrackDesign

**CarreraTrackDesign** is a model that generates a subset of possible Carrera 1:32/1:24 slot car tracks based on user specified track sections. As the number of track segments increase, the permutations of possible track layouts explode and become computationally infeasible. For this reason, the result of the model should be viewed as a small subset of possible tracks, inspired by the user
provided starting point. The intention is for the user provided starting point to evolve iteratively as the model provides inspiration
and is re-run over and over.

Notes:
- The units of the axes in the figure is meter, meaning the figures accurately display the physical size of the different tracks. In realtion to this, note that the line, and consequently the dimensions of the track, represent the midpoint of the track. Hence, half the width of the track and potential additions should be kept in mind.


# Usage

## Initialize model
```python
from carreratrackdesign.TrackGenerator import TrackGenerator

"""
Note: The initialization parameters can be omitted in practical use
      but are included here for completeness.
"""

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
```
```python
2025-02-11 20:42:46,609 - INFO - TrackGenerator initialized with turn_section_radius=0.3, straight_section_length=0.345, lap_tolerance=0.05, orientation_tolerance=0.01
```

## Generate track layouts
```python

"""
Note: The model is not required to use all track sections, so -- unless
      user has a limited track in mind -- the number
      of track sections should be set to the maximum available to the user.
      
      The inputs maximum_number_of_tacks and max_time_per_split can be increased
      to generate additional and more different track suggestions.

      The input starting_sequence is a track section the generate track is required to
      begin with. The format is a string on the form

      starting_sequence = "SSRRRSSRRR"
      
      where each letter represent a track segment, the first letter represent the 'first track segment'
      and S, R, L represent straight, right and left track segments, respectively. The turn track
      segments are 60 degrees, so the above track is a closed 0-shape.
      If the user has no required track segment that should be included in the generated tracks, set

      starting_sequence = ""
      
      Upon studying the generated tracks, the user may decide on a particular section the 
      generated track should include. The user can specify this as starting_sequence and re-run
      the code.
"""
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
```
```python
Generating Tracks: 100%|██████████| 6/6 [04:19<00:00, 43.28s/it]
```

## Generate track figures
```python
# Generate figures of the generated tracks
path = './test/figures/generated_tracks.png'

track_gen.generate_track_figures(path)
```
```python
2025-02-11 20:47:29,169 - INFO - Plot saved to ./test/figures/generated_tracks.png
```

![Forecasts](test/figures/generated_tracks.png)