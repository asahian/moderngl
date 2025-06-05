# Using Python lists as numpy might not be available due to pip issues.
# 36 vertices for 6 faces, 2 triangles per face, 3 vertices per triangle.
# Each vertex: (x, y, z, nx, ny, nz, u, v) - 8 components
# Positions: -0.5 to 0.5 cube centered at origin.
# Normals: Per face.
# UVs: (0,0) to (1,1) per face.

raw_vertices = [
    # Face 1: Front (+Z) - Normal (0,0,1)
    # Triangle 1
    -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  0.0, 0.0, # Bottom-left
     0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  1.0, 0.0, # Bottom-right
     0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  1.0, 1.0, # Top-right
    # Triangle 2
     0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  1.0, 1.0, # Top-right
    -0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  0.0, 1.0, # Top-left
    -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  0.0, 0.0, # Bottom-left

    # Face 2: Back (-Z) - Normal (0,0,-1)
    # Triangle 1
    -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 0.0, # Bottom-left (UV adjusted)
    -0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 1.0, # Top-left (UV adjusted)
     0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 1.0, # Top-right (UV adjusted)
    # Triangle 2
     0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 1.0, # Top-right (UV adjusted)
     0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 0.0, # Bottom-right (UV adjusted)
    -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 0.0, # Bottom-left (UV adjusted)

    # Face 3: Left (-X) - Normal (-1,0,0)
    # Triangle 1
    -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  0.0, 0.0, # Bottom-back
    -0.5, -0.5,  0.5, -1.0,  0.0,  0.0,  1.0, 0.0, # Bottom-front
    -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,  1.0, 1.0, # Top-front
    # Triangle 2
    -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,  1.0, 1.0, # Top-front
    -0.5,  0.5, -0.5, -1.0,  0.0,  0.0,  0.0, 1.0, # Top-back
    -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  0.0, 0.0, # Bottom-back

    # Face 4: Right (+X) - Normal (1,0,0)
    # Triangle 1
     0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  1.0, 0.0, # Bottom-back (UV adjusted)
     0.5,  0.5, -0.5,  1.0,  0.0,  0.0,  1.0, 1.0, # Top-back (UV adjusted)
     0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  0.0, 1.0, # Top-front (UV adjusted)
    # Triangle 2
     0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  0.0, 1.0, # Top-front (UV adjusted)
     0.5, -0.5,  0.5,  1.0,  0.0,  0.0,  0.0, 0.0, # Bottom-front (UV adjusted)
     0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  1.0, 0.0, # Bottom-back (UV adjusted)

    # Face 5: Bottom (-Y) - Normal (0,-1,0)
    # Triangle 1
    -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0, 1.0, # Back-left (UV adjusted for top view)
     0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  1.0, 1.0, # Back-right
     0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0, 0.0, # Front-right
    # Triangle 2
     0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0, 0.0, # Front-right
    -0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  0.0, 0.0, # Front-left
    -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0, 1.0, # Back-left

    # Face 6: Top (+Y) - Normal (0,1,0)
    # Triangle 1
    -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0, 0.0, # Back-left
    -0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  0.0, 1.0, # Front-left
     0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0, 1.0, # Front-right
    # Triangle 2
     0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0, 1.0, # Front-right
     0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  1.0, 0.0, # Back-right
    -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0, 0.0  # Back-left
]

# For ModernGL, it's often easier to work with vertices if they are already
# in a format that can be directly put into a buffer, e.g., list of floats.
# If numpy were available and working:
# import numpy as np
# vertices_np = np.array(raw_vertices, dtype='f4')

# For now, just provide the raw list.
# This 'vertices' variable can be removed if get_face_vertices becomes the sole provider.
# However, keeping it might be useful for a full cube VBO for other purposes (like an inventory icon).
# For chunk meshing, we'll use get_face_vertices.
_full_cube_vertices = raw_vertices # Renamed to avoid confusion

def get_full_cube_vertices():
    """Returns the raw list of vertex data floats for a full cube."""
    return _full_cube_vertices

def get_full_cube_vertices_bytes():
    """Packs the full cube vertex data into bytes."""
    import struct
    if not _full_cube_vertices:
        return b''
    return struct.pack(f'{len(_full_cube_vertices)}f', *_full_cube_vertices)

# Face indices (example mapping, can be any consistent convention)
# 0: +Z (Front)
# 1: -Z (Back)
# 2: -X (Left)
# 3: +X (Right)
# 4: -Y (Bottom)
# 5: +Y (Top)

# Each face has 6 vertices (2 triangles), each vertex has 8 components (pos, normal, uv)
# Total components per face = 6 * 8 = 48
_face_vertex_data = {
    # Front face (+Z), Normal (0,0,1)
    0: [
        -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  0.0, 0.0,
         0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  1.0, 0.0,
         0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  1.0, 1.0,
         0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  1.0, 1.0,
        -0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  0.0, 1.0,
        -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  0.0, 0.0,
    ],
    # Back face (-Z), Normal (0,0,-1)
    1: [
        -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 0.0,
        -0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 1.0,
         0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 1.0,
         0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 1.0,
         0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 0.0,
        -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 0.0,
    ],
    # Left face (-X), Normal (-1,0,0)
    2: [
        -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  0.0, 0.0,
        -0.5, -0.5,  0.5, -1.0,  0.0,  0.0,  1.0, 0.0,
        -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,  1.0, 1.0,
        -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,  1.0, 1.0,
        -0.5,  0.5, -0.5, -1.0,  0.0,  0.0,  0.0, 1.0,
        -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  0.0, 0.0,
    ],
    # Right face (+X), Normal (1,0,0)
    3: [
         0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  1.0, 0.0,
         0.5,  0.5, -0.5,  1.0,  0.0,  0.0,  1.0, 1.0,
         0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  0.0, 1.0,
         0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  0.0, 1.0,
         0.5, -0.5,  0.5,  1.0,  0.0,  0.0,  0.0, 0.0,
         0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  1.0, 0.0,
    ],
    # Bottom face (-Y), Normal (0,-1,0)
    4: [
        -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0, 1.0,
         0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  1.0, 1.0,
         0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0, 0.0,
         0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0, 0.0,
        -0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  0.0, 0.0,
        -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0, 1.0,
    ],
    # Top face (+Y), Normal (0,1,0)
    5: [
        -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0, 0.0,
        -0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  0.0, 1.0,
         0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0, 1.0,
         0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0, 1.0,
         0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  1.0, 0.0,
        -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0, 0.0,
    ]
}

def get_face_vertices(face_index: int, block_x: int, block_y: int, block_z: int, uv_rect: tuple[float, float, float, float]) -> list[float]:
    """
    Returns vertex data for a specific face of a cube, offset by block_x, block_y, block_z,
    and with UVs mapped according to uv_rect.
    Each vertex is (pos_x, pos_y, pos_z, norm_x, norm_y, norm_z, final_u, final_v).
    Args:
        face_index: 0-5, corresponding to a specific face.
        block_x, block_y, block_z: World position of the block (integer coords).
        uv_rect: A tuple (u_start, v_start, u_width, v_height) for UV mapping.
    Returns:
        A list of floats representing the vertices for that face with mapped UVs.
    """
    if face_index not in _face_vertex_data:
        raise ValueError(f"Invalid face_index: {face_index}")

    base_face_verts = _face_vertex_data[face_index] # Raw vertices for the face, UVs are 0-1 for that face
    offset_face_verts = []

    u_start, v_start, u_width, v_height = uv_rect

    for i in range(0, len(base_face_verts), 8): # Iterate over each vertex (8 components)
        # Position components
        vx, vy, vz = base_face_verts[i], base_face_verts[i+1], base_face_verts[i+2]
        # Normal components
        nx, ny, nz = base_face_verts[i+3], base_face_verts[i+4], base_face_verts[i+5]
        # Original UV components (s, t) for the face (0.0 to 1.0 range)
        s, t = base_face_verts[i+6], base_face_verts[i+7]

        # Map UVs using the provided uv_rect
        final_u = u_start + s * u_width
        final_v = v_start + t * v_height # Standard UV: (0,0) is bottom-left or top-left.
                                         # If V is flipped (e.g. t=0 is top), adjust as needed.
                                         # Assuming standard OpenGL UVs (0,0 is bottom-left of texture region).

        offset_face_verts.extend([
            vx + block_x, vy + block_y, vz + block_z, # Offset position
            nx, ny, nz, # Normal
            final_u, final_v  # Mapped UV
        ])
    return offset_face_verts

if __name__ == '__main__':
    print(f"Number of float components for full cube: {len(get_full_cube_vertices())}")
    print(f"Number of vertices for full cube: {len(get_full_cube_vertices()) // 8}")
    assert len(get_full_cube_vertices()) == 36 * 8
    print("Full cube mesh data defined.")

    vertex_bytes = get_full_cube_vertices_bytes()
    print(f"Length of byte array for full cube: {len(vertex_bytes)}")
    assert len(vertex_bytes) == 288 * 4
    print("Full cube vertex data successfully packed into bytes.")

    # Test get_face_vertices
    face0_verts_at_origin = get_face_vertices(0, 0, 0, 0)
    default_uv_rect = (0.0, 0.0, 1.0, 1.0) # Full texture area
    face0_verts_at_origin = get_face_vertices(0, 0, 0, 0, default_uv_rect)
    print(f"Face 0 (Front) at (0,0,0) - first vertex X: {face0_verts_at_origin[0]}, U: {face0_verts_at_origin[6]}, V: {face0_verts_at_origin[7]}")
    assert face0_verts_at_origin[0] == -0.5
    assert len(face0_verts_at_origin) == 48

    face0_verts_at_111 = get_face_vertices(0, 1, 1, 1, default_uv_rect)
    print(f"Face 0 (Front) at (1,1,1) - first vertex X: {face0_verts_at_111[0]}")
    assert face0_verts_at_111[0] == 0.5

    # Test with a different UV rect, e.g., using only the top-left quarter of the texture
    quarter_uv_rect = (0.0, 0.0, 0.5, 0.5)
    face0_verts_quarter_uv = get_face_vertices(0, 0, 0, 0, quarter_uv_rect)
    # Original UVs for first vertex of a face are (0,0). Mapped: (0,0)
    # Original UVs for second vertex are (1,0). Mapped: (0.5,0)
    # Original UVs for third vertex are (1,1). Mapped: (0.5,0.5)
    print(f"Face 0 with quarter UV - UV of 1st vert: ({face0_verts_quarter_uv[6]:.2f}, {face0_verts_quarter_uv[7]:.2f})") # Expected (0.00, 0.00)
    assert abs(face0_verts_quarter_uv[6] - 0.0) < 0.01 and abs(face0_verts_quarter_uv[7] - 0.0) < 0.01

    # UV of 2nd vertex (original 1,0)
    print(f"Face 0 with quarter UV - UV of 2nd vert: ({face0_verts_quarter_uv[8*1 + 6]:.2f}, {face0_verts_quarter_uv[8*1 + 7]:.2f})") # Expected (0.50, 0.00)
    assert abs(face0_verts_quarter_uv[8*1 + 6] - 0.5) < 0.01 and abs(face0_verts_quarter_uv[8*1 + 7] - 0.0) < 0.01

    # UV of 3rd vertex (original 1,1)
    print(f"Face 0 with quarter UV - UV of 3rd vert: ({face0_verts_quarter_uv[8*2 + 6]:.2f}, {face0_verts_quarter_uv[8*2 + 7]:.2f})") # Expected (0.50, 0.50)
    assert abs(face0_verts_quarter_uv[8*2 + 6] - 0.5) < 0.01 and abs(face0_verts_quarter_uv[8*2 + 7] - 0.5) < 0.01

    print("get_face_vertices with UV mapping seems to work.")
