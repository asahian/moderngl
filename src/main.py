import pygame as pg
import moderngl as mgl
from pyrr import matrix44 # For projection matrix
import sys
from camera import Camera # Import the Camera class
from world import World, CHUNK_SIZE # Import the World class and CHUNK_SIZE
from graphics.renderer import Renderer # Import the Renderer class

class App:
    def __init__(self, window_size=(1280, 720), title="ModernGL Window"):
        pg.init()
        self.window_size = window_size
        self.aspect_ratio = self.window_size[0] / self.window_size[1]
        # Set OpenGL attributes
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        # Create a window
        pg.display.set_mode(self.window_size, flags=pg.OPENGL | pg.DOUBLEBUF)
        # Set the window title
        pg.display.set_caption(title)

        # Create a ModernGL context
        self.ctx = mgl.create_context()
        self.ctx.enable(mgl.DEPTH_TEST | mgl.CULL_FACE)
        self.ctx.cull_face = 'back' # Standard back-face culling

        # World
        self.world = World()

        # Camera
        self.camera = Camera()
        # Initialize view_matrix and projection_matrix attributes
        self.view_matrix = self.camera.get_view_matrix()
        self.projection_matrix = matrix44.create_perspective_projection_matrix(
            45.0, self.aspect_ratio, 0.1, 100.0
        )


        # Renderer
        try:
            self.renderer = Renderer(self.ctx)
        except Exception as e:
            print(f"Failed to initialize Renderer: {e}")
            self.running = False
            return

        # Initial chunk mesh generation
        if self.running: # Only if renderer initialized successfully
            print("Building initial chunk meshes...")
            for chunk_coord_key, chunk in self.world.chunks.items():
                chunk.build_mesh() # world_context=self.world would be for advanced neighbor lookup
                self.renderer.update_chunk_mesh(chunk_coord_key, chunk.mesh_vertices)
            print("Initial chunk meshes built.")


        # Mouse control
        self.last_mouse_x, self.last_mouse_y = pg.mouse.get_pos()
        self.mouse_captured = False # Start with mouse visible
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)

        # Timing
        self.clock = pg.time.Clock()
        self.delta_time = 0

        self.running = True

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if self.mouse_captured:
                        self.mouse_captured = False
                        pg.mouse.set_visible(True)
                        pg.event.set_grab(False)
                    else:
                        self.running = False # Quit if escape pressed and mouse not captured
                if event.key == pg.K_TAB: # Toggle mouse capture with Tab
                    self.mouse_captured = not self.mouse_captured
                    pg.mouse.set_visible(not self.mouse_captured)
                    pg.event.set_grab(self.mouse_captured)
                    if self.mouse_captured:
                        self.last_mouse_x, self.last_mouse_y = pg.mouse.get_pos()
                        # Center mouse for better subsequent capture
                        pg.mouse.set_pos((self.window_size[0] // 2, self.window_size[1] // 2))
                        self.last_mouse_x, self.last_mouse_y = self.window_size[0] // 2, self.window_size[1] // 2


            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1 and not self.mouse_captured: # Left click to capture
                    self.mouse_captured = True
                    pg.mouse.set_visible(False)
                    pg.event.set_grab(True)
                    self.last_mouse_x, self.last_mouse_y = event.pos
                    # Center mouse for better subsequent capture
                    pg.mouse.set_pos((self.window_size[0] // 2, self.window_size[1] // 2))
                    self.last_mouse_x, self.last_mouse_y = self.window_size[0] // 2, self.window_size[1] // 2


            if event.type == pg.MOUSEMOTION and self.mouse_captured:
                mouse_x, mouse_y = event.pos
                delta_x = mouse_x - self.last_mouse_x
                delta_y = self.last_mouse_y - mouse_y # Inverted Y for standard camera controls

                self.camera.process_mouse_movement(delta_x, delta_y)

                # Warp mouse to center to prevent leaving window
                pg.mouse.set_pos((self.window_size[0] // 2, self.window_size[1] // 2))
                self.last_mouse_x, self.last_mouse_y = self.window_size[0] // 2, self.window_size[1] // 2

    def handle_keyboard_input(self):
        keys = pg.key.get_pressed()
        if not self.mouse_captured: # Only process movement if mouse is captured (i.e. game is active)
            return

        if keys[pg.K_w]:
            self.camera.process_keyboard("FORWARD", self.delta_time)
        if keys[pg.K_s]:
            self.camera.process_keyboard("BACKWARD", self.delta_time)
        if keys[pg.K_a]:
            self.camera.process_keyboard("LEFT", self.delta_time)
        if keys[pg.K_d]:
            self.camera.process_keyboard("RIGHT", self.delta_time)
        if keys[pg.K_SPACE]:
            self.camera.process_keyboard("UP", self.delta_time)
        if keys[pg.K_LSHIFT] or keys[pg.K_LCTRL]: # Use LSHIFT or LCTRL for down
            self.camera.process_keyboard("DOWN", self.delta_time)


    def run(self):
        while self.running:
            self.delta_time = self.clock.tick(60) / 1000.0 # FPS limit and get delta time in seconds

            self.handle_events()
            self.handle_keyboard_input()

            # Update matrices
            self.view_matrix = self.camera.get_view_matrix()
            # Projection matrix usually doesn't change per frame unless window resizes
            # self.projection_matrix = matrix44.create_perspective_projection_matrix(
            #     45.0, self.aspect_ratio, 0.1, 100.0
            # )

            # Clear the screen
            self.ctx.clear(color=(0.08, 0.16, 0.18, 1.0), depth=1.0) # Added alpha and depth

            # Render world blocks
            # Iterate over a small section of the world for now
            # For example, one chunk (0 to CHUNK_SIZE -1 in each world dimension)
            # The world chunks are already created from -1 to 1 in world.py constructor
            # Let's render the chunk at (0,0,0) world chunk coordinates
            # which corresponds to world block coordinates 0..15 for x, 0..15 for y, 0..15 for z

            # Define render range (e.g., one chunk around origin, or specific chunks)
            # Since world generates chunks from cx=-1 to 1, cz=-1 to 1, at cy=0 by default:
            # This covers world x from -16 to 31, z from -16 to 31, y from 0 to 15.
            # Let's render a 32x16x32 block area starting from world origin (0,0,0)
            # This will cover parts of chunk (0,0,0) and potentially (1,0,0), (0,0,1), (1,0,1) etc.

            # Update meshes for chunks that need it
            for chunk_coord_key, chunk in self.world.chunks.items():
                if chunk.needs_remesh:
                    # print(f"Remeshing chunk {chunk_coord_key}...")
                    chunk.build_mesh() # world_context=self.world for advanced neighbors
                    self.renderer.update_chunk_mesh(chunk_coord_key, chunk.mesh_vertices)
                    # chunk.needs_remesh is set to False inside build_mesh()

            # Render all chunks
            for chunk_coord_key, chunk in self.world.chunks.items():
                # Calculate chunk's world position in pixels/units for the model matrix
                # chunk_coord_key is (cx, cy, cz) in chunk coordinates.
                # CHUNK_SIZE is (width, height, depth) in blocks per chunk.
                world_pixel_pos = (
                    chunk_coord_key[0] * CHUNK_SIZE[0],
                    chunk_coord_key[1] * CHUNK_SIZE[1],
                    chunk_coord_key[2] * CHUNK_SIZE[2]
                )
                self.renderer.render_chunk(
                    chunk_coord_key,    # Key for the renderer to find VAO/VBO
                    world_pixel_pos,    # Actual world position for model matrix
                    self.view_matrix,
                    self.projection_matrix
                )

            # Swap buffers
            pg.display.flip()

        self.quit()

    def destroy(self):
        print("Destroying App resources...")
        if hasattr(self, 'renderer') and self.renderer:
            self.renderer.destroy()
        # Any other app-specific resources to clean up would go here

    def quit(self):
        self.destroy() # Call destroy before quitting pg
        pg.quit()
        sys.exit()

if __name__ == '__main__':
    app = App()
    if hasattr(app, 'running') and app.running: # Check if init failed
        app.run()
    else:
        print("App failed to initialize properly. Exiting.")
        # Ensure pg.quit is called if pg.init() was successful but app failed later
        if pg.get_init(): # Check if Pygame was initialized
            pg.quit()
        sys.exit(1)
