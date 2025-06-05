# src/block_data.py

# For now, texture coordinates can be conceptual indices or simple placeholders.
# Later, these could be (atlas_x, atlas_y) tile coordinates or direct (s0,t0,s1,t1) UVs.
# Let's assume for now each block uses the *same* texture on all faces,
# and this texture is represented by a simple ID or a single UV rect.
# A more complex system would have per-face texture definitions.

# Placeholder: (u_offset, v_offset, u_width, v_height) relative to a hypothetical atlas unit
# Or, just an index into a list of textures. For simplicity, let's use a single
# placeholder UV rect for the entire block for now.
# (0,0,1,1) would mean it uses the whole area of whatever texture is bound.

# If we had a texture atlas, e.g. 16x16 textures in a 256x256 image (16 textures per row/col)
# tex_coords_grass_top = (0/16, 0/16, 1/16, 1/16) # x, y, width, height in normalized atlas coords
# tex_coords_grass_sides = (1/16, 0/16, 1/16, 1/16)
# tex_coords_dirt = (2/16, 0/16, 1/16, 1/16)

# For this subtask, let's define a simple dictionary for block properties.
# Key: block_id
# Value: dict with 'name' and 'face_uvs'
# 'face_uvs' will be a list of 6 UV rectangles [top, bottom, front, back, left, right]
# The order of faces in 'face_uvs' should match face_idx used in cube_mesh and world.py
# Assuming face_idx mapping: 0:+Z(Front), 1:-Z(Back), 2:-X(Left), 3:+X(Right), 4:-Y(Bottom), 5:+Y(Top)
# Each UV rectangle is (u_start, v_start, u_width, v_height) - normalized (0.0-1.0)
# These will map to the UVs for a single face. For now, they'll be identical as if
# we only have one texture for the whole block.

# Atlas constants
ATLAS_DIMENSIONS_TILES = (16, 16) # Atlas is 16 textures wide, 16 textures high
TILE_UV_WIDTH = 1.0 / ATLAS_DIMENSIONS_TILES[0]
TILE_UV_HEIGHT = 1.0 / ATLAS_DIMENSIONS_TILES[1]

def get_uv_rect_for_tile(tile_x, tile_y):
    """Helper function to generate UV rects for a tile coordinate."""
    u_start = tile_x * TILE_UV_WIDTH
    v_start = tile_y * TILE_UV_HEIGHT # Assuming (0,0) in atlas is top-left; adjust if bottom-left
    return (u_start, v_start, TILE_UV_WIDTH, TILE_UV_HEIGHT)

# Define tile coordinates for specific block faces
# (column, row) in the texture atlas grid, assuming (0,0) is top-left tile
STONE_TILE = (0, 0)
DIRT_TILE = (1, 0)
GRASS_TOP_TILE = (2, 0)
GRASS_SIDE_TILE = (3, 0)
WOOD_PLANK_TILE = (4,0)
WOOD_LOG_SIDE_TILE = (5,0) # Side of log
WOOD_LOG_TOP_TILE = (6,0)  # Top/bottom of log
LEAVES_TILE = (7,0)

# Generate UV rectangles from tile coordinates
STONE_UV = get_uv_rect_for_tile(*STONE_TILE)
DIRT_UV = get_uv_rect_for_tile(*DIRT_TILE)
GRASS_TOP_UV = get_uv_rect_for_tile(*GRASS_TOP_TILE)
GRASS_SIDE_UV = get_uv_rect_for_tile(*GRASS_SIDE_TILE)
WOOD_PLANK_UV = get_uv_rect_for_tile(*WOOD_PLANK_TILE)
WOOD_LOG_SIDE_UV = get_uv_rect_for_tile(*WOOD_LOG_SIDE_TILE)
WOOD_LOG_TOP_UV = get_uv_rect_for_tile(*WOOD_LOG_TOP_TILE)
LEAVES_UV = get_uv_rect_for_tile(*LEAVES_TILE)


# Face order: Front (+Z), Back (-Z), Left (-X), Right (+X), Bottom (-Y), Top (+Y)
# This must be consistent with how face_idx is used in Chunk.build_mesh and cube_mesh.py
BLOCK_TYPES = {
    0: {"name": "Air", "face_uvs": None},
    1: {"name": "Stone", "face_uvs": [STONE_UV] * 6},
    2: {"name": "Dirt", "face_uvs": [DIRT_UV] * 6},
    3: {"name": "Grass", "face_uvs": [
            GRASS_SIDE_UV,  # Front (+Z)
            GRASS_SIDE_UV,  # Back (-Z)
            GRASS_SIDE_UV,  # Left (-X)
            GRASS_SIDE_UV,  # Right (+X)
            DIRT_UV,        # Bottom (-Y)
            GRASS_TOP_UV    # Top (+Y)
        ]},
    4: {"name": "WoodPlank", "face_uvs": [WOOD_PLANK_UV] * 6},
    5: {"name": "WoodLog", "face_uvs": [
            WOOD_LOG_SIDE_UV, # Front (+Z)
            WOOD_LOG_SIDE_UV, # Back (-Z)
            WOOD_LOG_SIDE_UV, # Left (-X)
            WOOD_LOG_SIDE_UV, # Right (+X)
            WOOD_LOG_TOP_UV,  # Bottom (-Y)
            WOOD_LOG_TOP_UV   # Top (+Y)
        ]},
    6: {"name": "Leaves", "face_uvs": [LEAVES_UV] * 6}, # Could be transparent later
}


# Example of more detailed UVs (ensure face_uvs list order is consistent)
# GRASS_TOP_UV = (0.0, 0.75, 0.25, 0.25) # Example: Top-left quarter of a texture for top
# GRASS_SIDE_UV = (0.25, 0.75, 0.25, 0.25) # Example: Second quarter for sides
# DIRT_UV = (0.50, 0.75, 0.25, 0.25) # Example: Third quarter for bottom
# BLOCK_TYPES_DETAILED = {
#     3: {"name": "Grass", "face_uvs": [
#             GRASS_SIDE_UV, # Front (+Z)
#             GRASS_SIDE_UV, # Back (-Z)
#             GRASS_SIDE_UV, # Left (-X)
#             GRASS_SIDE_UV, # Right (+X)
#             DIRT_UV,       # Bottom (-Y)
#             GRASS_TOP_UV   # Top (+Y)
#         ]
#     },
# }


def get_block_uvs(block_id, face_index):
    """
    Retrieves the UV rectangle for a given block ID and face index.
    Args:
        block_id: The ID of the block.
        face_index: The index of the face (0-5).
    Returns:
        A tuple (u_start, v_start, u_width, v_height) for the UV mapping.
        Returns a default full UV rectangle if the block or specific face UV is not defined.
    """
    block_data = BLOCK_TYPES.get(block_id)
    if not block_data or not block_data["face_uvs"]:
        # Default UVs (e.g., for undefined blocks or if 'face_uvs' is missing)
        return (0.0, 0.0, 1.0, 1.0)

    if 0 <= face_index < len(block_data["face_uvs"]):
        return block_data["face_uvs"][face_index]
    else:
        # Default UVs if face_index is out of bounds for this block's definition
        return (0.0, 0.0, 1.0, 1.0)

if __name__ == '__main__':
    print("Block data defined.")
    print(f"Stone (ID 1), Front face (idx 0) UVs: {get_block_uvs(1, 0)}")
    print(f"Grass (ID 3), Top face (idx 5) UVs: {get_block_uvs(3, 5)}")
    # print(f"Grass (Detailed), Top face (idx 5) UVs: {BLOCK_TYPES_DETAILED[3]['face_uvs'][5]}") # If using a different dict
    print(f"Air (ID 0) UVs: {get_block_uvs(0, 0)}")
    print(f"Undefined block (ID 99) UVs: {get_block_uvs(99, 0)}")

    # Test new block types
    print(f"Grass (ID 3), Top face (+Y, idx 5) UVs: {get_block_uvs(3, 5)}") # Should be GRASS_TOP_UV
    assert get_block_uvs(3, 5) == GRASS_TOP_UV
    print(f"Grass (ID 3), Front face (+Z, idx 0) UVs: {get_block_uvs(3, 0)}") # Should be GRASS_SIDE_UV
    assert get_block_uvs(3, 0) == GRASS_SIDE_UV
    print(f"Grass (ID 3), Bottom face (-Y, idx 4) UVs: {get_block_uvs(3, 4)}") # Should be DIRT_UV
    assert get_block_uvs(3, 4) == DIRT_UV

    print(f"WoodLog (ID 5), Top face (+Y, idx 5) UVs: {get_block_uvs(5, 5)}") # Should be WOOD_LOG_TOP_UV
    assert get_block_uvs(5, 5) == WOOD_LOG_TOP_UV
    print(f"WoodLog (ID 5), Side face (-X, idx 2) UVs: {get_block_uvs(5, 2)}") # Should be WOOD_LOG_SIDE_UV
    assert get_block_uvs(5, 2) == WOOD_LOG_SIDE_UV
