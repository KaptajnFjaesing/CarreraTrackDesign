import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for non-interactive plotting

import math
import numpy as np
from tqdm import tqdm
import time
from shapely.geometry import LineString, Point
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Polygon
from matplotlib.lines import Line2D
from typing import List, Set, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Set the logging level for matplotlib to WARNING to suppress detailed debug messages
matplotlib_logger = logging.getLogger('matplotlib')
matplotlib_logger.setLevel(logging.WARNING)

class TrackGenerator:
    """
    Class to generate unique track maps for Carrera slot car tracks.
    The track is defined by a sequence of 'L' (left turn), 'R' (right turn), and 'S' (straight) sections.
    The track is generated by recursively backtracking through all possible track maps.
    The track is considered complete if the car returns to the starting position and orientation.
    The track is considered valid if it does not self-intersect and has a minimum distance between track sections.
    """

    def __init__(
        self,
        turn_section_radius: float = 0.3,
        straight_section_length: float = 0.345,
        track_width: float = 0.198,
        lap_tolerance: float = 0.05,
        orientation_tolerance: float = 0.01,
    ) -> None:
        """
        Initialize the TrackGenerator.

        :param turn_section_radius: Radius of the turn sections measured in meter.
        :param straight_section_length: Length of the straight sections measured in meter.
        :param lap_tolerance: Tolerance for completing a lap.
        :param orientation_tolerance: Tolerance for the orientation at the end of a lap.
        """
        self.turn_section_radius = turn_section_radius
        self.straight_section_length = straight_section_length
        self.track_width = track_width
        self.minimum_track_intersection_distance = straight_section_length * 0.6
        self.lap_tolerance = lap_tolerance
        self.orientation_tolerance = orientation_tolerance
        self.unique_track_set: Set[str] = set()
        logging.info("TrackGenerator initialized with turn_section_radius=%s, straight_section_length=%s, lap_tolerance=%s, orientation_tolerance=%s",
                     turn_section_radius, straight_section_length, lap_tolerance, orientation_tolerance)

    @staticmethod
    def get_cyclic_equivalent(string: str) -> str:
        """
        Get the cyclic equivalent of a string by finding the lexicographically smallest string
        that can be obtained by rotating the input string.

        :param string: Input string.
        :return: Lexicographically smallest cyclic equivalent string.
        """
        return min(string[i:] + string[:i] for i in range(len(string)))

    def get_unique_cyclic_strings(self, strings: List[str]) -> Set[str]:
        """
        Get the set of unique cyclic equivalents of a list of strings.
        This is useful for generating unique track maps.

        :param strings: List of input strings.
        :return: Set of unique cyclic equivalent strings.
        """
        return {self.get_cyclic_equivalent(string) for string in strings}

    @staticmethod
    def check_self_intersection(coordinates: List[Tuple[float, float]]) -> bool:
        """
        Check if a list of coordinates self-intersects.

        :param coordinates: List of (x, y) coordinates.
        :return: True if the coordinates do not self-intersect, False otherwise.
        """
        return LineString(coordinates).is_simple
    
    def check_min_distance_to_self(self, coordinates: List[Tuple[float, float]]) -> bool:
        """
        Check if a list of coordinates has a minimum distance between points.

        :param coordinates: List of (x, y) coordinates.
        :return: True if the minimum distance between any two points is greater than the minimum track intersection distance, False otherwise.
        """
        for i, coord in enumerate(coordinates):
            point = Point(coord)
            distances = [point.distance(Point(c)) for j, c in enumerate(coordinates) if j != i]
            if min(distances) < self.minimum_track_intersection_distance:
                return False
        return True

    def lap_completed(self, track_map: str) -> bool:
        """
        Check if a lap is completed given a track map.

        :param track_map: String representing the track map.
        :return: True if the lap is completed, False otherwise.
        """
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

    def track_coordinates(self, track_map: str) -> List[Tuple[float, float]]:
        """
        Get the coordinates of a track given a track map.

        :param track_map: String representing the track map.
        :return: List of (x, y) coordinates representing the track.
        """
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

    def generate_turn_splits(self, number_of_turn_sections: int) -> List[Tuple[int, int]]:
        """
        Generate all valid splits of total_turns into left (L) and right (R).

        :param number_of_turn_sections: Total number of turn sections.
        :return: List of tuples representing the splits of left and right turns.
        """
        return [(left, number_of_turn_sections - left) for left in range(number_of_turn_sections // 2 + 1, number_of_turn_sections + 1)]

    def generate_unique_tracks(
        self,
        number_of_straight_sections: int,
        number_of_turn_sections: int,
        starting_sequence: str = "",
        allow_intersections: bool = False,
        maximum_number_of_tracks: int = 10,
        max_time_per_split: int = 10
    ) -> None:
        """
        Generate all unique track maps given the number of straight and turn sections.

        :param number_of_straight_sections: Number of straight sections.
        :param number_of_turn_sections: Number of turn sections.
        :param starting_sequence: Initial sequence of track sections.
        :param allow_intersections: Whether to allow self-intersections in the track.
        :param maximum_number_of_tracks: Maximum number of tracks to generate.
        :param max_time_per_split: Maximum time to spend generating tracks for each split.
        """
        self.unique_track_set.clear()
        turn_splits = self.generate_turn_splits(number_of_turn_sections=number_of_turn_sections)
        all_unique_tracks = []  # Store a set for each split

        for number_of_right_sections, number_of_left_sections in tqdm(turn_splits, desc="Generating Tracks"):
            segments = {'R': number_of_right_sections, 'L': number_of_left_sections, 'S': number_of_straight_sections}
            initial_segments = {i: segments[i] - starting_sequence.count(i) for i in segments}

            if any(count < 0 for count in initial_segments.values()):
                all_unique_tracks.append(set())  # Keep alignment in results
                logging.info("Starting sequence is not feasible for split: %s", (number_of_right_sections, number_of_left_sections))
                continue

            consecutive_straight_condition = (math.floor(segments['S'] / 2) + 1) * "S"
            if number_of_right_sections > number_of_left_sections:
                consecutive_turn_condition = (math.floor(segments['R'] / 2) + 1) * "R"
            else:
                consecutive_turn_condition = (math.floor(segments['L'] / 2) + 1) * "L"

            tracks_for_split = set()  # Separate set for this split
            start_time = time.time()

            def backtrack(track_so_far: str, segment_counts_left: dict, consecutive_counts: dict) -> None:
                if time.time() - start_time > max_time_per_split:  # Stop if time limit exceeded
                    return
                if len(track_so_far) > 0 and self.lap_completed(track_map=track_so_far):
                    if allow_intersections or self.check_self_intersection(self.track_coordinates(track_map=track_so_far[:-1])):
                        if allow_intersections or self.check_min_distance_to_self(self.track_coordinates(track_map=track_so_far[:-1])):
                            tracks_for_split.add(track_so_far)
                            return
                for segment, count in segment_counts_left.items():
                    if len(tracks_for_split) >= maximum_number_of_tracks:
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
            logging.warning("No track maps could be generated given the settings.")

    def get_track_set(self) -> Set[str]:
        """
        Return the set of unique track maps.

        :return: Set of unique track maps.
        """
        return self.unique_track_set

    def generate_track_figures(self, path: str) -> None:
        """
        Generate figures of the unique track maps.

        :param path: Path to save the generated figures.
        """
        if len(self.unique_track_set) > 0:
            # Number of columns in the subfigure layout
            ncols = int(np.floor(np.sqrt(len(self.unique_track_set))))
            nrows = int(np.ceil(len(self.unique_track_set) / ncols))

            fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(5 * ncols, 5 * nrows))
            axes = np.ravel(axes)  # Flatten the axes array for easier iteration

            for ax, track_map in zip(axes, list(self.unique_track_set)):
                orientation = 0
                position = np.array([0.0, 0.0])
                center_patches = []  # Store center lines
                fill_patches = []  # Store filled regions
                track_points = [position.copy()]  # Store track positions for axis limits

                for i, section in enumerate(track_map):
                    if section == "L":
                        orientation_new = orientation + np.pi / 3
                        center = position - self.turn_section_radius * np.array([np.cos(orientation), np.sin(orientation)])
                        center_patch = Arc(center, 2 * self.turn_section_radius, 2 * self.turn_section_radius, theta1=np.degrees(orientation), theta2=np.degrees(orientation_new), color='w', linestyle='dashed')
                        # Interpolate points along the arcs
                        theta = np.linspace(orientation, orientation_new, 20)
                        outer_arc = center + (self.turn_section_radius + self.track_width / 2) * np.array([np.cos(theta), np.sin(theta)]).T
                        inner_arc = center + (self.turn_section_radius - self.track_width / 2) * np.array([np.cos(theta), np.sin(theta)]).T
                        
                        # Combine the two arcs into a filled polygon
                        track_fill = np.vstack([outer_arc, inner_arc[::-1]])
                        fill_patches.append(Polygon(track_fill, closed=True, color='black'))

                        position += [-self.turn_section_radius * (1 - np.cos(orientation_new)) + self.turn_section_radius * (1 - np.cos(orientation)), 
                                    self.turn_section_radius * np.sin(orientation_new) - self.turn_section_radius * np.sin(orientation)]
                        orientation = orientation_new

                        # Add red line at the end of the segment
                        end_normal = np.array([np.cos(orientation), np.sin(orientation)])
                        red_line_start = position - 1.2 * self.track_width / 2 * end_normal
                        red_line_end = position + 1.2 * self.track_width / 2 * end_normal
                        ax.plot([red_line_start[0], red_line_end[0]], [red_line_start[1], red_line_end[1]], color='red')

                    elif section == "R":
                        orientation_new = orientation - np.pi / 3
                        center = position + self.turn_section_radius * np.array([np.cos(orientation), np.sin(orientation)])
                        center_patch = Arc(center, 2 * self.turn_section_radius, 2 * self.turn_section_radius, theta1=180 + np.degrees(orientation_new), theta2=180 + np.degrees(orientation), color='w', linestyle='dashed')
                        # Interpolate points along the arcs
                        theta = np.linspace(orientation_new, orientation, 20)+np.pi
                        outer_arc = center + (self.turn_section_radius + self.track_width / 2) * np.array([np.cos(theta), np.sin(theta)]).T
                        inner_arc = center + (self.turn_section_radius - self.track_width / 2) * np.array([np.cos(theta), np.sin(theta)]).T

                        # Combine the two arcs into a filled polygon
                        track_fill = np.vstack([outer_arc, inner_arc[::-1]])
                        fill_patches.append(Polygon(track_fill, closed=True, color='black'))

                        position += -(-self.turn_section_radius * (1 - np.cos(orientation_new)) + self.turn_section_radius * (1 - np.cos(orientation))), \
                                    -(self.turn_section_radius * np.sin(orientation_new) - self.turn_section_radius * np.sin(orientation))
                        orientation = orientation_new

                        # Add red line at the end of the segment
                        end_normal = np.array([np.cos(orientation), np.sin(orientation)])
                        red_line_start = position - 1.2 * self.track_width / 2 * end_normal
                        red_line_end = position + 1.2 * self.track_width / 2 * end_normal
                        ax.plot([red_line_start[0], red_line_end[0]], [red_line_start[1], red_line_end[1]], color='red')

                    elif section == "S":
                        start_point = position.copy()
                        position += [-self.straight_section_length * np.sin(orientation), self.straight_section_length * np.cos(orientation)]
                        center_patch = Line2D([start_point[0], position[0]], [start_point[1], position[1]], linewidth=1, color='w', linestyle='dashed')

                        direction = position - start_point
                        direction_normalized = direction / np.linalg.norm(direction)  # Normalize

                        # Compute normal vector (perpendicular to direction)
                        normal = np.array([-direction_normalized[1], direction_normalized[0]])  # Rotate 90 degrees

                        # Compute parallel line segment
                        start_point1_parallel = start_point + (self.track_width / 2) * normal
                        position1_parallel = position + (self.track_width / 2) * normal
                        start_point2_parallel = start_point - (self.track_width / 2) * normal
                        position2_parallel = position - (self.track_width / 2) * normal

                        # Create a filled polygon for the straight segment
                        fill_patches.append(Polygon([start_point1_parallel, position1_parallel, position2_parallel, start_point2_parallel], closed=True, color='black'))

                        # Add red line at the end of the segment
                        end_normal = np.array([np.cos(orientation), np.sin(orientation)])
                        red_line_start = position - 1.2 * self.track_width / 2 * end_normal
                        red_line_end = position + 1.2 * self.track_width / 2 * end_normal
                        ax.plot([red_line_start[0], red_line_end[0]], [red_line_start[1], red_line_end[1]], color='red')

                    track_points.append(position.copy())
                    center_patches.append(center_patch)

                # Add filled polygons to the plot
                for patch in fill_patches:
                    ax.add_patch(patch)

                for patch in center_patches:
                    if isinstance(patch, Arc):
                        ax.add_patch(patch)
                    elif isinstance(patch, Line2D):
                        ax.add_line(patch)

                # Adjust axis limits dynamically
                track_points = np.array(track_points)
                x_min, x_max = track_points[:, 0].min(), track_points[:, 0].max()
                y_min, y_max = track_points[:, 1].min(), track_points[:, 1].max()
                ax.set_xlim(x_min - 0.2, x_max + 0.2)
                ax.set_ylim(y_min - 0.2, y_max + 0.2)

                ax.set_aspect('equal')
                ax.set_xlabel('X [m]')
                ax.set_ylabel('Y [m]')
                ax.set_title(f'Track Map: {track_map}')

            # Hide any unused subplots
            for ax in axes[len(self.unique_track_set):]:
                ax.axis("off")

            plt.tight_layout()
            fig.savefig(path)
            logging.info("Plot saved to %s", path)
        else:
            logging.warning("No track maps, run the function 'generate_unique_tracks' to yield a non-empty set first.")

