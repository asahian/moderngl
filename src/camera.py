import numpy as np
from pyrr import matrix44, Vector3, vector
from src.interaction import cast_ray, RaycastResult # Assuming interaction.py is in src/

class Camera:
    def __init__(self, position=np.array([0.0, 0.0, 3.0], dtype=np.float32),
                 yaw=-90.0, pitch=0.0):
        self.position = np.array(position, dtype=np.float32)
        self.yaw = np.float32(yaw)
        self.pitch = np.float32(pitch)

        self.world_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)

        self.front = np.array([0.0, 0.0, -1.0], dtype=np.float32) # Initialized during update_vectors
        self.right = np.array([1.0, 0.0, 0.0], dtype=np.float32) # Initialized during update_vectors
        self.up = np.array([0.0, 1.0, 0.0], dtype=np.float32)    # Initialized during update_vectors

        self.move_speed = 2.5  # units per second
        self.mouse_sensitivity = 0.1 # degrees per mouse unit

        self.update_camera_vectors()

    def update_camera_vectors(self):
        # Calculate the new Front vector
        fx = np.cos(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        fy = np.sin(np.radians(self.pitch))
        fz = np.sin(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        self.front = vector.normalise(np.array([fx, fy, fz], dtype=np.float32))

        # Recalculate the Right and Up vector
        self.right = vector.normalise(np.cross(self.front, self.world_up))
        self.up = vector.normalise(np.cross(self.right, self.front))

    def get_view_matrix(self):
        # Eye: camera position
        # Target: position + front vector
        # Up: camera's up vector
        # pyrr's create_look_at expects numpy arrays or lists, not raw Vector3 objects for all args
        # self.position and self.front are currently pyrr.Vector3
        # We need to ensure they are converted if necessary, or that pyrr handles them.
        # pyrr functions typically handle its own vector types correctly.
        return matrix44.create_look_at(self.position, self.position + self.front, self.up)

    def process_keyboard(self, direction, delta_time):
        velocity = self.move_speed * delta_time
        if direction == "FORWARD":
            self.position += self.front * velocity
        if direction == "BACKWARD":
            self.position -= self.front * velocity
        if direction == "LEFT":
            self.position -= self.right * velocity
        if direction == "RIGHT":
            self.position += self.right * velocity
        if direction == "UP":
            self.position += self.world_up * velocity # Use world_up for predictable up/down
        if direction == "DOWN":
            self.position -= self.world_up * velocity # Use world_up for predictable up/down

    def process_mouse_movement(self, xoffset, yoffset, constrain_pitch=True):
        self.yaw += xoffset * self.mouse_sensitivity
        self.pitch += yoffset * self.mouse_sensitivity

        # Constrain pitch to avoid flipping
        if constrain_pitch:
            if self.pitch > 89.0:
                self.pitch = 89.0
            if self.pitch < -89.0:
                self.pitch = -89.0

        self.update_camera_vectors()

    def get_raycast_target(self, world, max_distance=5.0):
        """
        Casts a ray from the camera's position in its front direction to find a target block.
        Args:
            world: The world object (with a get_block method).
            max_distance: Maximum distance for the raycast.
        Returns:
            A RaycastResult object if a block is hit, otherwise None.
        """
        # self.position and self.front are pyrr.Vector3 objects.
        # cast_ray expects numpy arrays or list-like objects that np.array() can convert.
        # pyrr.Vector3 can be converted to numpy array by np.array(vector_obj.tolist())
        # or sometimes directly np.array(vector_obj) if pyrr objects behave like sequences.
        # Let's assume np.array() handles pyrr.Vector3 directly or via their internal structure.

        # Explicit conversion to list for np.array might be safer if direct conversion is problematic:
        # origin_np = np.array(list(self.position))
        # direction_np = np.array(list(self.front))
        # return cast_ray(world, origin_np, direction_np, max_distance)

        # Simpler: pass pyrr vectors directly if np.array() in cast_ray handles them.
        # (pyrr vectors are often numpy-compatible or subclasses)
        return cast_ray(world, self.position, self.front, max_distance)
