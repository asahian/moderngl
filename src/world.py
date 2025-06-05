from src.graphics.cube_mesh import get_face_vertices
from src.block_data import get_block_uvs # Import for getting UV rects per block/face

# CHUNK_SIZE: (width, height, depth)
CHUNK_SIZE = (16, 16, 16) # x, y, z (local chunk coordinates)

class Chunk:
    def __init__(self, position):
        """
        Initializes a Chunk at a given world position.
        Position is in chunk coordinates, e.g., (0,0,0), (1,0,0).
        """
        self.position = position # Chunk's position in chunk coordinates (e.g., (0,0,0), (1,0,0))

        self.blocks = [[[0 for _ in range(CHUNK_SIZE[2])]
                        for _ in range(CHUNK_SIZE[1])]
                       for _ in range(CHUNK_SIZE[0])]

        # Populate with some test blocks using new IDs
        for lx_ in range(CHUNK_SIZE[0]):
            for lz_ in range(CHUNK_SIZE[2]):
                self.blocks[lx_][0][lz_] = 1 # Stone base at y=0

                # Layer y=1 with varied blocks
                if 0 <= 1 < CHUNK_SIZE[1]:
                    if lx_ % 4 == 0: self.blocks[lx_][1][lz_] = 2 # Dirt
                    elif lx_ % 4 == 1: self.blocks[lx_][1][lz_] = 3 # Grass
                    elif lx_ % 4 == 2: self.blocks[lx_][1][lz_] = 4 # Wood Plank
                    else: self.blocks[lx_][1][lz_] = 5 # Wood Log

                # Layer y=2 with Leaves on one half of the chunk
                if 0 <= 2 < CHUNK_SIZE[1]:
                    if lx_ < CHUNK_SIZE[0] // 2 :
                        self.blocks[lx_][2][lz_] = 6 # Leaves


        self.mesh_vertices = []    # List to store vertex data for this chunk's mesh
        # self.vbo = None # VBO/VAO Management moved to Renderer
        # self.vao = None
        self.needs_remesh = True   # Flag to indicate if the mesh needs to be rebuilt

    def get_block(self, x, y, z): # x,y,z are local chunk coordinates
        """
        Get block ID at local chunk coordinates (x, y, z).
        Assumes x, y, z are within CHUNK_SIZE bounds.
        """
        if 0 <= x < CHUNK_SIZE[0] and 0 <= y < CHUNK_SIZE[1] and 0 <= z < CHUNK_SIZE[2]:
            return self.blocks[x][y][z]
        return 0 # Should not happen if access is managed by World or internally checked

    def set_block(self, x, y, z, block_id): # x,y,z are local chunk coordinates
        """
        Set block ID at local chunk coordinates (x, y, z).
        Marks chunk for remeshing if block changes.
        """
        if 0 <= x < CHUNK_SIZE[0] and 0 <= y < CHUNK_SIZE[1] and 0 <= z < CHUNK_SIZE[2]:
            if self.blocks[x][y][z] != block_id:
                self.blocks[x][y][z] = block_id
                self.needs_remesh = True
        else:
            # This case should ideally be prevented by World class logic
            print(f"Warning: Chunk.set_block called with out-of-bounds local coords ({x},{y},{z}) for chunk {self.position}")

    def build_mesh(self, world_context=None): # world_context is placeholder for accessing neighbor chunks
        """
        Builds the vertex mesh for this chunk based on its blocks.
        Checks neighbors within the chunk; for neighbors outside, it assumes they are transparent.
        A full implementation would use world_context to query actual neighbor chunks.
        """
        self.mesh_vertices.clear()

        # Face indices from cube_mesh.py: 0:+Z, 1:-Z, 2:-X, 3:+X, 4:-Y, 5:+Y
        # (dx, dy, dz, face_index)
        face_checks = [
            (0, 0, 1, 0), (0, 0, -1, 1), (-1, 0, 0, 2), (1, 0, 0, 3),
            (0, -1, 0, 4), (0, 1, 0, 5)
        ]

        for lx in range(CHUNK_SIZE[0]):
            for ly in range(CHUNK_SIZE[1]):
                for lz in range(CHUNK_SIZE[2]):
                    block_id = self.blocks[lx][ly][lz]
                    if block_id == 0:  # Air block, no mesh
                        continue

                    # World position of the current block for get_face_vertices is just lx,ly,lz
                    # as these are local offsets within the chunk's own space.
                    # The final world position of the chunk is handled by the model matrix in rendering.

                    for dx, dy, dz, face_idx in face_checks:
                        nlx, nly, nlz = lx + dx, ly + dy, lz + dz # Neighbor local coordinates

                        is_face_visible = False
                        if not (0 <= nlx < CHUNK_SIZE[0] and \
                                0 <= nly < CHUNK_SIZE[1] and \
                                0 <= nlz < CHUNK_SIZE[2]):
                            # Neighbor is outside this chunk.
                            # TODO: Use world_context.get_block(world_nx, world_ny, world_nz) == 0
                            # For now, assume exposed to air if outside chunk boundaries.
                            is_face_visible = True
                        else:
                            neighbor_block_id = self.blocks[nlx][nly][nlz]
                            if neighbor_block_id == 0: # Neighbor is air
                                # TODO: Could add more sophisticated transparency checks here later
                                # e.g. if neighbor_block_id is water, glass etc.
                                is_face_visible = True

                        if is_face_visible:
                            # Get UV rectangle for this specific block type and face
                            uv_rect = get_block_uvs(block_id, face_idx)

                            # Pass local block coords (lx,ly,lz) and the uv_rect
                            face_v = get_face_vertices(face_idx, lx, ly, lz, uv_rect)
                            self.mesh_vertices.extend(face_v)

        self.needs_remesh = False

class World:
    def __init__(self):
        self.chunks = {}  # Key: (cx, cy, cz) chunk coordinates (world scale), Value: Chunk object
        for cx in range(-1, 2):
            for cz in range(-1, 2):
                self.add_chunk((cx, 0, cz))

    def add_chunk(self, chunk_coord_tuple):
        if chunk_coord_tuple not in self.chunks:
            new_chunk = Chunk(chunk_coord_tuple)
            self.chunks[chunk_coord_tuple] = new_chunk
            return new_chunk
        return self.chunks[chunk_coord_tuple]

    def get_chunk(self, chunk_coord_tuple):
        return self.chunks.get(chunk_coord_tuple)

    def _world_to_chunk_coords(self, world_x, world_y, world_z):
        chunk_x = int(world_x // CHUNK_SIZE[0])
        chunk_y = int(world_y // CHUNK_SIZE[1])
        chunk_z = int(world_z // CHUNK_SIZE[2])

        local_x = int(world_x % CHUNK_SIZE[0])
        local_y = int(world_y % CHUNK_SIZE[1])
        local_z = int(world_z % CHUNK_SIZE[2])

        return (chunk_x, chunk_y, chunk_z), (local_x, local_y, local_z)

    def get_block(self, world_x, world_y, world_z):
        chunk_coord, local_coord = self._world_to_chunk_coords(world_x, world_y, world_z)
        chunk = self.get_chunk(chunk_coord)

        if chunk:
            return chunk.get_block(local_coord[0], local_coord[1], local_coord[2])
        return 0

    def set_block(self, world_x, world_y, world_z, block_id):
        chunk_coord, local_coord = self._world_to_chunk_coords(world_x, world_y, world_z)
        chunk = self.get_chunk(chunk_coord)

        if not chunk:
            chunk = self.add_chunk(chunk_coord)

        chunk.set_block(local_coord[0], local_coord[1], local_coord[2], block_id)
        # chunk.needs_remesh = True is handled by Chunk.set_block

        # Mark neighboring chunks for remesh if the block is on a border
        # This is a simplified version. A full solution might need to be more precise.
        if local_coord[0] == 0:
            nc = self.get_chunk((chunk_coord[0] - 1, chunk_coord[1], chunk_coord[2]))
            if nc: nc.needs_remesh = True
        elif local_coord[0] == CHUNK_SIZE[0] - 1:
            nc = self.get_chunk((chunk_coord[0] + 1, chunk_coord[1], chunk_coord[2]))
            if nc: nc.needs_remesh = True

        if local_coord[1] == 0:
            nc = self.get_chunk((chunk_coord[0], chunk_coord[1] - 1, chunk_coord[2]))
            if nc: nc.needs_remesh = True
        elif local_coord[1] == CHUNK_SIZE[1] - 1:
            nc = self.get_chunk((chunk_coord[0], chunk_coord[1] + 1, chunk_coord[2]))
            if nc: nc.needs_remesh = True

        if local_coord[2] == 0:
            nc = self.get_chunk((chunk_coord[0], chunk_coord[1], chunk_coord[2] - 1))
            if nc: nc.needs_remesh = True
        elif local_coord[2] == CHUNK_SIZE[2] - 1:
            nc = self.get_chunk((chunk_coord[0], chunk_coord[1], chunk_coord[2] + 1))
            if nc: nc.needs_remesh = True

if __name__ == '__main__':
    world = World()
    print(f"Created {len(world.chunks)} chunks.")

    test_chunk = world.get_chunk((0,0,0))
    if test_chunk:
        print(f"Chunk (0,0,0) initial needs_remesh: {test_chunk.needs_remesh}")
        test_chunk.build_mesh()
        print(f"Chunk (0,0,0) after build_mesh, needs_remesh: {test_chunk.needs_remesh}")
        num_vertices = len(test_chunk.mesh_vertices) // 8
        print(f"Chunk (0,0,0) mesh vertex count: {num_vertices}")
        # Expected for a 16x16x16 chunk with only y=0 filled (stone), and other blocks air:
        # Top faces of y=0 layer: 16*16 = 256 faces
        # Side faces for y=0 layer (exposed to air within chunk at y=1): 0 (no air at y=1 in this layer)
        # Side faces for y=0 layer (exposed to "outside chunk" if neighbor check is simplified):
        #   - X-normal faces: 2 * 16 = 32 (lx=0 and lx=15 exposed if outside is air)
        #   - Z-normal faces: 2 * 16 = 32 (lz=0 and lz=15 exposed if outside is air)
        # Total faces if only y=0 is stone and build_mesh considers borders as exposed:
        # 256 (tops) + (16*4) (sides of the layer, if exposed) = 256 + 64 = 320 faces.
        # (16 blocks on each of 4 sides of y=0 layer).
        # Each face = 6 vertices. So, 320 * 6 = 1920 vertices.
        # The test output will be the number of vertices.
        # The current build_mesh logic counts faces exposed to air *within the chunk* or *at chunk boundaries*.
        # For a chunk that is all stone at y=0 and all air above y=0:
        # - Each block at y=0 has its top face (at y=0.5) exposed to air at y=1. So 16*16 = 256 top faces.
        # - Blocks at y=0 and lx=0 have their -X face exposed (if boundary is air). 16 such faces.
        # - Blocks at y=0 and lx=15 have their +X face exposed. 16 such faces.
        # - Blocks at y=0 and lz=0 have their -Z face exposed. 16 such faces.
        # - Blocks at y=0 and lz=15 have their +Z face exposed. 16 such faces.
        # Total visible faces = 256 (tops) + 4*16 (sides) = 256 + 64 = 320 faces.
        # Total vertices = 320 * 6 = 1920.
        print(f"Expected vertices for single layer chunk (exposed boundaries): 1920. Got: {num_vertices}")


    # Test set_block marking neighbors
    chunk_n100 = world.get_chunk((-1,0,0))
    if chunk_n100: chunk_n100.needs_remesh = False # Reset for test

    world.set_block(0, 0, 0, 0) # world_x=0 is on border of chunk (0,0,0) and (-1,0,0)
                                # local_x inside chunk (0,0,0) is 0.

    print(f"Chunk (0,0,0) needs_remesh after set_block(0,0,0,..): {world.get_chunk((0,0,0)).needs_remesh}")
    if chunk_n100:
        print(f"Chunk (-1,0,0) needs_remesh after set_block(0,0,0,..): {chunk_n100.needs_remesh}")

    # Test build_mesh on a more complex scenario (e.g. a 2x2x2 cube of stone in middle of chunk)
    solid_chunk = Chunk((10,10,10)) # Test chunk, not added to world
    for x in range(2):
        for y in range(2):
            for z in range(2):
                solid_chunk.set_block(x,y,z, 1) # Create a 2x2x2 stone cube at corner
    solid_chunk.build_mesh()
    # This 2x2x2 cube should have 6 faces * 4 blocks_per_face = 24 faces exposed.
    # 24 faces * 6 vertices/face = 144 vertices.
    print(f"Isolated 2x2x2 cube mesh vertex count: {len(solid_chunk.mesh_vertices)//8}")
    assert len(solid_chunk.mesh_vertices)//8 == 144

    print("World.py tests completed (basic).")
