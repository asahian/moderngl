# CHUNK_SIZE: (width, height, depth)
CHUNK_SIZE = (16, 16, 16) # x, y, z

class Chunk:
    def __init__(self, position):
        """
        Initializes a Chunk at a given world position.
        Position is in chunk coordinates, e.g., (0,0,0), (1,0,0) corresponding to
        world block coordinates (0,0,0), (16,0,0) if CHUNK_SIZE[0] is 16.
        """
        self.position = position # Chunk's position in chunk coordinates

        # Initialize blocks with nested lists: blocks[x][y][z]
        # Using 0 for air, 1 for stone as per requirements
        self.blocks = [[[0 for _ in range(CHUNK_SIZE[2])]
                        for _ in range(CHUNK_SIZE[1])]
                       for _ in range(CHUNK_SIZE[0])]

        # Fill bottom layer with stone (ID 1)
        for x in range(CHUNK_SIZE[0]):
            for z in range(CHUNK_SIZE[2]):
                self.blocks[x][0][z] = 1 # y=0 is the bottom layer

    def get_block(self, x, y, z):
        """
        Get block ID at local chunk coordinates (x, y, z).
        Assumes x, y, z are within CHUNK_SIZE bounds.
        """
        if 0 <= x < CHUNK_SIZE[0] and 0 <= y < CHUNK_SIZE[1] and 0 <= z < CHUNK_SIZE[2]:
            return self.blocks[x][y][z]
        return 0 # Return air if out of bounds (should ideally not happen with correct logic)

    def set_block(self, x, y, z, block_id):
        """
        Set block ID at local chunk coordinates (x, y, z).
        Assumes x, y, z are within CHUNK_SIZE bounds.
        """
        if 0 <= x < CHUNK_SIZE[0] and 0 <= y < CHUNK_SIZE[1] and 0 <= z < CHUNK_SIZE[2]:
            self.blocks[x][y][z] = block_id

class World:
    def __init__(self):
        self.chunks = {}  # Key: (cx, cy, cz) chunk coordinates, Value: Chunk object

        # Create a 3x1x3 area of chunks for a basic ground plane
        # y=0 for chunks, so they are all at the same vertical level
        for cx in range(-1, 2): # Creates chunks at x = -1, 0, 1
            for cz in range(-1, 2): # Creates chunks at z = -1, 0, 1
                # For now, world only has one layer of chunks vertically
                self.add_chunk((cx, 0, cz))

    def add_chunk(self, chunk_position_tuple):
        """
        Adds a new chunk at the given chunk_position_tuple (cx, cy, cz).
        If a chunk already exists at that position, it's replaced.
        """
        if chunk_position_tuple not in self.chunks:
            new_chunk = Chunk(chunk_position_tuple)
            self.chunks[chunk_position_tuple] = new_chunk
            return new_chunk
        return self.chunks[chunk_position_tuple] # Return existing if for some reason it's called again

    def get_chunk(self, chunk_position_tuple):
        """
        Returns the Chunk object at the given chunk_position_tuple (cx, cy, cz), or None.
        """
        return self.chunks.get(chunk_position_tuple)

    def _world_to_chunk_coords(self, world_x, world_y, world_z):
        """
        Converts world block coordinates to (chunk_coord_tuple, local_block_coord_tuple).
        """
        chunk_x = world_x // CHUNK_SIZE[0]
        chunk_y = world_y // CHUNK_SIZE[1]
        chunk_z = world_z // CHUNK_SIZE[2]

        local_x = world_x % CHUNK_SIZE[0]
        local_y = world_y % CHUNK_SIZE[1]
        local_z = world_z % CHUNK_SIZE[2]

        return (chunk_x, chunk_y, chunk_z), (local_x, local_y, local_z)

    def get_block(self, world_x, world_y, world_z):
        """
        Get block ID at world coordinates (world_x, world_y, world_z).
        Returns 0 (air) if the chunk containing the block doesn't exist.
        """
        chunk_pos, local_pos = self._world_to_chunk_coords(world_x, world_y, world_z)
        chunk = self.get_chunk(chunk_pos)

        if chunk:
            return chunk.get_block(local_pos[0], local_pos[1], local_pos[2])
        return 0 # Air if chunk doesn't exist

    def set_block(self, world_x, world_y, world_z, block_id):
        """
        Set block ID at world coordinates.
        If the chunk doesn't exist, it's created.
        """
        chunk_pos, local_pos = self._world_to_chunk_coords(world_x, world_y, world_z)
        chunk = self.get_chunk(chunk_pos)

        if not chunk:
            chunk = self.add_chunk(chunk_pos)

        chunk.set_block(local_pos[0], local_pos[1], local_pos[2], block_id)

if __name__ == '__main__':
    # Basic test
    world = World()
    print(f"Created {len(world.chunks)} chunks.")

    # Test get_block for a stone block (should be 1)
    print(f"Block at (0,0,0): {world.get_block(0,0,0)}") # Should be 1 (stone)
    print(f"Block at (0,1,0): {world.get_block(0,1,0)}") # Should be 0 (air)

    # Test set_block and then get_block
    world.set_block(0, 5, 0, 2) # Set a block to ID 2 (e.g. dirt)
    print(f"Block at (0,5,0) after set: {world.get_block(0,5,0)}") # Should be 2

    # Test setting a block in a potentially new chunk (edge of pre-generated area)
    # Chunk (1,0,1) max local x is 15. World x=31 is in chunk (1,0,z).
    # World x=32 is in chunk (2,0,z).
    # Initial chunks are -1 to 1. So chunk (2,0,1) would be new.
    world.set_block(CHUNK_SIZE[0] * 2, 0, CHUNK_SIZE[0] * 1, 3) # x=32, y=0, z=16
    print(f"Block at ({CHUNK_SIZE[0]*2}, 0, {CHUNK_SIZE[0]*1}) after set in new chunk: {world.get_block(CHUNK_SIZE[0]*2, 0, CHUNK_SIZE[0]*1)}")
    print(f"Number of chunks now: {len(world.chunks)}")

    # Test getting a block from a non-existent chunk far away
    print(f"Block at (1000,0,1000): {world.get_block(1000,0,1000)}") # Should be 0 (air)

    # Test camera interaction point: Camera is at (0,0,3) by default in main.py
    # What's directly under it?
    print(f"Block at (0,0,3) world coords (camera initial xz, world y=0): {world.get_block(0,0,3)}") # Stone
    print(f"Block at (0,1,3) world coords (camera initial xz, world y=1): {world.get_block(0,1,3)}") # Air
    print(f"Block at (0,2,3) world coords (camera initial xz, world y=2): {world.get_block(0,2,3)}") # Air

    # Test chunk boundaries
    # Chunk (0,0,0) spans world x = 0 to 15
    # Chunk (1,0,0) spans world x = 16 to 31
    print(f"Block at (15,0,0) in chunk (0,0,0): {world.get_block(15,0,0)}") # Stone
    print(f"Block at (16,0,0) in chunk (1,0,0): {world.get_block(16,0,0)}") # Stone (new chunk also has stone base)
    chunk_info = world._world_to_chunk_coords(15,0,0)
    print(f"World (15,0,0) -> Chunk {chunk_info[0]}, Local {chunk_info[1]}")
    chunk_info = world._world_to_chunk_coords(16,0,0)
    print(f"World (16,0,0) -> Chunk {chunk_info[0]}, Local {chunk_info[1]}")
