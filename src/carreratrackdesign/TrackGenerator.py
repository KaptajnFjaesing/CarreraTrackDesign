import math
import numpy as np
from tqdm import tqdm
import time
from shapely.geometry import LineString, Point
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
from matplotlib.lines import Line2D

class TrackGenerator:
    def __init__(
            self,
            turn_section_radius=0.3,
            straight_section_length=0.345,
            maximum_number_of_tacks=10,
            lap_tolerance = 0.05,
            orientation_tolerance = 0.01,
            max_time_per_split = 10
            ):
        self.turn_section_radius = turn_section_radius
        self.straight_section_length = straight_section_length
        self.minimum_track_intersection_distance = straight_section_length*0.6
        self.maximum_number_of_tacks = maximum_number_of_tacks
        self.lap_tolerance = lap_tolerance
        self.orientation_tolerance = orientation_tolerance
        self.max_time_per_split = max_time_per_split
        self.unique_track_set = set()

    @staticmethod
    def get_cyclic_equivalent(string):
        return min(string[i:] + string[:i] for i in range(len(string)))

    def get_unique_cyclic_strings(self, strings):
        return {self.get_cyclic_equivalent(string) for string in strings}

    @staticmethod
    def check_self_intersection(coordinates):
        return LineString(coordinates).is_simple

    
    def check_min_distance_to_self(self, coordinates):
        for i, coord in enumerate(coordinates):
            point = Point(coord)
            distances = [point.distance(Point(c)) for j, c in enumerate(coordinates) if j != i]
            if min(distances) < self.minimum_track_intersection_distance:
                return False
        return True

    def lap_completed(self, track_map):
        orientation, x, y = 0, 0, 0
        for section in track_map:
            if section == "L":
                orientation += math.pi / 3
                x += self.turn_section_radius * (math.cos(orientation) - math.cos(orientation - math.pi / 3))
                y += self.turn_section_radius * (math.sin(orientation) - math.sin(orientation - math.pi / 3))
            elif section == "R":
                orientation -= math.pi / 3
                x -= self.turn_section_radius * (math.cos(orientation) - math.cos(orientation + math.pi / 3))
                y -= self.turn_section_radius * (math.sin(orientation) - math.sin(orientation + math.pi / 3))
            elif section == "S":
                x -= self.straight_section_length * math.sin(orientation)
                y += self.straight_section_length * math.cos(orientation)
        return (x ** 2 + y ** 2) ** 0.5 < self.lap_tolerance and abs(orientation % (2 * math.pi)) < self.orientation_tolerance

    def track_coordinates(self, track_map):
        orientation = 0
        points = [[0, 0]]
        position = [0, 0]
        for section in track_map:
            if section == "L":
                orientation += math.pi / 3
                position[0] += -self.turn_section_radius * (1 - math.cos(orientation)) + self.turn_section_radius * (1 - math.cos(orientation - math.pi / 3))
                position[1] += self.turn_section_radius * math.sin(orientation) - self.turn_section_radius * math.sin(orientation - math.pi / 3)
            elif section == "R":
                orientation -= math.pi / 3
                position[0] += self.turn_section_radius * (1 - math.cos(orientation)) - self.turn_section_radius * (1 - math.cos(orientation + math.pi / 3))
                position[1] -= self.turn_section_radius * math.sin(orientation) - self.turn_section_radius * math.sin(orientation + math.pi / 3)
            elif section == "S":
                position[0] += -self.straight_section_length * math.sin(orientation)
                position[1] += self.straight_section_length * math.cos(orientation)
            points.append(position[:])
        return points


    def generate_turn_splits(self, number_of_turn_sections):
        """Generate all valid splits of total_turns into left (L) and right (R)."""
        return [(left, number_of_turn_sections - left) for left in range(number_of_turn_sections // 2+1, number_of_turn_sections + 1)]

    def generate_unique_tracks(self, starting_sequence: str, number_of_straight_sections: int, number_of_turn_sections: int):
        turn_splits = self.generate_turn_splits(number_of_turn_sections=number_of_turn_sections)
        all_unique_tracks = []  # Store a set for each split

        for number_of_right_sections, number_of_left_sections in tqdm(turn_splits, desc="Generating Tracks"):
            segments = {'R': number_of_right_sections, 'L': number_of_left_sections, 'S': number_of_straight_sections}
            initial_segments = {i: segments[i] - starting_sequence.count(i) for i in segments}

            if any(count < 0 for count in initial_segments.values()):
                all_unique_tracks.append(set())  # Keep alignment in results
                continue  

            consecutive_straight_condition = (math.floor(segments['S'] / 2) + 1) * "S"
            if number_of_right_sections > number_of_left_sections:
                consecutive_turn_condition = (math.floor(segments['R'] / 2) + 1) * "R"
            else:
                consecutive_turn_condition = (math.floor(segments['L'] / 2) + 1) * "L"

            tracks_for_split = set()  # Separate set for this split
            start_time = time.time()

            def backtrack(track_so_far, segment_counts_left, consecutive_counts):
                if time.time() - start_time > self.max_time_per_split:  # Stop if time limit exceeded
                    return
                if len(track_so_far) > 0 and self.lap_completed(track_map=track_so_far):
                    if self.check_self_intersection(self.track_coordinates(track_map=track_so_far[:-1])):
                        if self.check_min_distance_to_self(self.track_coordinates(track_map=track_so_far[:-1])):
                            tracks_for_split.add(track_so_far)
                            return

                for segment, count in segment_counts_left.items():
                    if len(tracks_for_split) >= self.maximum_number_of_tacks:
                        return  

                    if count > 0 and consecutive_turn_condition not in track_so_far and consecutive_straight_condition not in track_so_far:
                        new_segment_counts = segment_counts_left.copy()
                        new_consecutive_counts = consecutive_counts.copy()
                        new_segment_counts[segment] -= 1
                        new_consecutive_counts[segment] += 1
                        backtrack(track_so_far + segment, new_segment_counts, new_consecutive_counts)

            backtrack(starting_sequence, initial_segments, {segment: 0 for segment in segments})
            all_unique_tracks.append(tracks_for_split)  # Store this set
        self.unique_track_set.update(set.union(*all_unique_tracks))

        if len(self.unique_track_set) == 0:
            print("No track maps could be generated given the settings.")



    def generate_track_figures(self):
        
        if len(self.unique_track_set) > 0:

            # Number of columns in the subfigure layout
            ncols = 3  
            nrows = int(np.ceil(len(self.unique_track_set) / ncols))  # Compute number of rows dynamically

            fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(5 * ncols, 5 * nrows))
            axes = np.ravel(axes)  # Flatten the axes array for easier iteration

            for ax, j in zip(axes, list(self.unique_track_set)):
                orientation = 0
                position = np.array([0.0, 0.0])
                patches = []
                r = 0.3
                s = 0.345
                track_points = [position.copy()]  # Store track positions for axis limits

                for c in j:
                    if c == "L":
                        orientation_new = orientation + np.pi / 3
                        center = position - r * np.array([np.cos(orientation), np.sin(orientation)])
                        patch = Arc(center, 2 * r, 2 * r, theta1=np.degrees(orientation), theta2=np.degrees(orientation_new), color='k')
                        position += -r * (1 - np.cos(orientation_new)) + r * (1 - np.cos(orientation)), r * np.sin(orientation_new) - r * np.sin(orientation)
                        orientation = orientation_new
                    elif c == "R":
                        orientation_new = orientation - np.pi / 3
                        center = position + r * np.array([np.cos(orientation), np.sin(orientation)])
                        patch = Arc(center, 2 * r, 2 * r, theta1=180 + np.degrees(orientation_new), theta2=180 + np.degrees(orientation), color='k')
                        position += -(-r * (1 - np.cos(orientation_new)) + r * (1 - np.cos(orientation))), -(r * np.sin(orientation_new) - r * np.sin(orientation))
                        orientation = orientation_new
                    elif c == "S":
                        start_point = position.copy()
                        position += -s * np.sin(orientation), s * np.cos(orientation)
                        patch = Line2D([start_point[0], position[0]], [start_point[1], position[1]], linewidth=1, color='k')

                    patches.append(patch)
                    track_points.append(position.copy())

                # Add patches to the subplot
                for patch in patches:
                    if isinstance(patch, Arc):
                        ax.add_patch(patch)
                    elif isinstance(patch, Line2D):
                        ax.add_line(patch)

                # Adjust axis limits dynamically
                track_points = np.array(track_points)
                x_min, x_max = track_points[:, 0].min(), track_points[:, 0].max()
                y_min, y_max = track_points[:, 1].min(), track_points[:, 1].max()
                ax.set_xlim(x_min - 0.1, x_max + 0.1)
                ax.set_ylim(y_min - 0.1, y_max + 0.1)

                ax.set_aspect('equal')
                ax.set_xlabel('X [m]')
                ax.set_ylabel('Y [m]')
                ax.set_title(f'Track Map: {j}')

            # Hide any unused subplots
            for ax in axes[len(self.unique_track_set):]:
                ax.axis("off")

            plt.tight_layout()
            plt.show()
        else:
            print("No track maps, run the function 'generate_unique_tracks' to yield a non empty set first.")





