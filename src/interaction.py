# src/interaction.py
import numpy as np # Assuming numpy will be available

class RaycastResult:
    def __init__(self, block_pos, face_normal, hit_point):
        self.block_pos = block_pos # tuple (x,y,z) of the hit block
        self.face_normal = face_normal # tuple (nx,ny,nz) indicating the hit face
        self.hit_point = hit_point # tuple (x,y,z) of the actual intersection point

    def __repr__(self):
        return (f"RaycastResult(block_pos={self.block_pos}, "
                f"face_normal={self.face_normal}, hit_point={self.hit_point})")

def cast_ray(world, origin, direction, max_distance=5.0):
    # Ensure origin and direction are numpy arrays
    origin = np.array(origin, dtype=float)
    direction = np.array(direction, dtype=float)

    # Normalize direction vector
    dir_norm = np.linalg.norm(direction)
    if dir_norm == 0:
        return None # Cannot cast ray with zero direction
    direction = direction / dir_norm

    current_block_pos = np.floor(origin).astype(int)

    initial_block_id = world.get_block(current_block_pos[0], current_block_pos[1], current_block_pos[2])
    if initial_block_id != 0:
        # Started inside a block. For this simplified version, consider it an immediate hit.
        # Face normal determination is non-trivial here.
        # Approximate based on which face of the block the origin is closest to, pointing away from block center.
        block_center = current_block_pos + 0.5
        delta_to_center = origin - block_center # Vector from center to origin
        abs_delta = np.abs(delta_to_center)

        face_hit_normal = np.zeros(3, dtype=int)
        if np.any(abs_delta > 1e-9): # Check if not exactly at center
            max_comp_idx = np.argmax(abs_delta)
            # Normal should point outwards from the block, so it's opposite to delta_to_center's component
            face_hit_normal[max_comp_idx] = -int(np.sign(delta_to_center[max_comp_idx]))
            if face_hit_normal[max_comp_idx] == 0: # If on a plane going through center
                 face_hit_normal[max_comp_idx] = 1 # Default to positive normal on that axis
        else: # Exactly at center or very close, default to a normal (e.g. pointing up)
            face_hit_normal[1] = 1

        return RaycastResult(tuple(current_block_pos), tuple(face_hit_normal), tuple(origin))

    # Voxel traversal algorithm setup
    step = np.sign(direction).astype(int)

    next_voxel_boundary = np.where(direction > 0, np.floor(origin) + 1.0, np.floor(origin))
    on_boundary_neg_dir = (origin == np.floor(origin)) & (direction < 0)
    next_voxel_boundary[on_boundary_neg_dir] -= 1.0

    with np.errstate(divide='ignore', invalid='ignore'):
        t_max = (next_voxel_boundary - origin) / direction
        t_max[direction == 0] = np.inf

    with np.errstate(divide='ignore', invalid='ignore'):
        t_delta = np.abs(1.0 / direction)
        t_delta[direction == 0] = np.inf

    parametric_distance = 0.0 # This will store the parametric distance along the ray to the hit face

    while True:
        min_idx = np.argmin(t_max) # Dimension (0,1,or 2 for x,y,z) of the nearest voxel boundary

        # Parametric distance to the next boundary plane that is crossed in this dimension
        distance_to_boundary_in_dim = t_max[min_idx]

        if distance_to_boundary_in_dim > max_distance:
            return None # Exceeded max_distance

        # Advance current_block_pos to the voxel that is entered
        current_block_pos[min_idx] += step[min_idx]

        # Update the parametric distance to the point where the ray entered this new block
        parametric_distance = distance_to_boundary_in_dim

        # Update t_max for the dimension we just crossed to find the next boundary in that dim
        t_max[min_idx] += t_delta[min_idx]

        # Check block at the new current_block_pos
        block_id = world.get_block(current_block_pos[0], current_block_pos[1], current_block_pos[2])

        if block_id != 0: # Hit a non-air block
            hit_point = origin + direction * parametric_distance # Calculate actual hit point

            face_normal = np.zeros(3, dtype=int)
            face_normal[min_idx] = -step[min_idx] # Normal points out of the hit block face

            return RaycastResult(tuple(current_block_pos), tuple(face_normal), tuple(hit_point))

    return None # Should be unreachable if max_distance is handled, but as a safeguard.
