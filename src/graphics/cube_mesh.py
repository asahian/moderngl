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
vertices = raw_vertices

def get_vertices():
    """Returns the raw list of vertex data floats."""
    return vertices

def get_vertices_bytes():
    """Packs the vertex data into bytes."""
    import struct
    if not vertices:
        return b''
    return struct.pack(f'{len(vertices)}f', *vertices)

if __name__ == '__main__':
    print(f"Number of float components: {len(get_vertices())}")
    print(f"Number of vertices: {len(get_vertices()) // 8}")
    # Expected: 36 vertices * 8 components/vertex = 288 floats
    assert len(get_vertices()) == 36 * 8
    print("Cube mesh data defined.")

    # Test bytes conversion
    vertex_bytes = get_vertices_bytes()
    print(f"Length of byte array: {len(vertex_bytes)}")
    # Expected: 288 floats * 4 bytes/float = 1152 bytes
    assert len(vertex_bytes) == 288 * 4
    print("Vertex data successfully packed into bytes.")
