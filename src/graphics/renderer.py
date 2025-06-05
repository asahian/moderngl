import moderngl
import pygame as pg # For texture loading, and image.tostring
from pyrr import matrix44 # For model matrix, matrix44.create_from_translation
import struct # For struct.pack in update_chunk_mesh
import os # For constructing absolute paths to shaders

# Local imports
# from .cube_mesh import get_vertices_bytes # This was for single cube, no longer needed directly here
from .shader_loader import load_shader_program, ShaderError

class Renderer:
    def __init__(self, ctx: moderngl.Context):
        self.ctx = ctx
        self.chunk_render_data = {} # Stores {'vbo': vbo, 'vao': vao, 'vertex_count': count}

        # Load shader program
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            vertex_shader_path = os.path.join(base_dir, 'shaders', 'default_vertex.glsl')
            fragment_shader_path = os.path.join(base_dir, 'shaders', 'default_fragment.glsl')

            self.program = load_shader_program(
                self.ctx,
                vertex_shader_path,
                fragment_shader_path
            )
        except (FileNotFoundError, ShaderError) as e:
            print(f"Error loading shader program: {e}")
            raise

        # Single cube VBO/VAO removed, individual chunks will have their own.

        # Placeholder texture loading (remains the same)
        self.texture = None
        try:
            # NOTE: The creation of 'assets/textures/placeholder.png' might fail due to tool limitations.
            # If the file is missing, pygame.image.load will raise an error.

            # Construct absolute path for texture as well for consistency, assuming assets dir is relative to project root
            # For renderer.py, __file__ is src/graphics/renderer.py
            # assets/ is typically ../../assets/ from src/graphics/
            assets_dir = os.path.join(base_dir, '..', '..', 'assets', 'textures')
            placeholder_texture_path = os.path.join(assets_dir, 'placeholder.png')

            texture_surface = pg.image.load(placeholder_texture_path).convert_alpha()
            texture_data = pg.image.tostring(texture_surface, 'RGBA', True) # Flipped for ModernGL
            self.texture = self.ctx.texture(texture_surface.get_size(), 4, texture_data)
            self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
            self.texture.swizzle = 'BGRA' # Pygame loads as BGR(A), convert to RGB(A) for shader
            print(f"Placeholder texture loaded successfully from {placeholder_texture_path}.")
        except pg.error as e:
            print(f"Pygame error loading texture '{placeholder_texture_path}': {e}")
            print("Renderer will proceed without texture, or with a fallback if implemented.")
            # Create a dummy 1x1 pink texture as a fallback if placeholder is missing
            try:
                dummy_data = struct.pack('4B', 255, 0, 255, 255) # RGBA: Pink
                self.texture = self.ctx.texture((1,1), 4, dummy_data)
                self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
                print("Created 1x1 pink fallback texture.")
            except Exception as fallback_e:
                print(f"Could not create fallback texture: {fallback_e}")
                self.texture = None # Ensure texture is None if all fails
        except Exception as e: # Catch other potential errors during texture loading
            print(f"General error loading texture '{placeholder_texture_path}': {e}")
            self.texture = None


        # Store uniform locations
        try:
            self.m_model_loc = self.program['model']
            self.m_view_loc = self.program['view']
            self.m_proj_loc = self.program['projection']
            self.u_texture_loc = self.program['u_texture_0']
        except KeyError as e:
            print(f"Error getting uniform location: {e}. Shader might be compiled incorrectly or uniform misspelled.")
            raise

    def update_chunk_mesh(self, chunk_world_pos_key: tuple, mesh_vertices_data: list):
        """
        Creates or updates VBO/VAO for a given chunk.
        chunk_world_pos_key: tuple (cx, cy, cz) identifying the chunk.
        mesh_vertices_data: Flat list of floats for the chunk's new mesh.
        """
        if chunk_world_pos_key in self.chunk_render_data:
            try:
                self.chunk_render_data[chunk_world_pos_key]['vbo'].release()
                self.chunk_render_data[chunk_world_pos_key]['vao'].release()
            except Exception as e:
                print(f"Error releasing old VBO/VAO for chunk {chunk_world_pos_key}: {e}")
            del self.chunk_render_data[chunk_world_pos_key]

        if not mesh_vertices_data: # Empty list or None
            # Ensure entry is removed if mesh becomes empty
            if chunk_world_pos_key in self.chunk_render_data:
                 del self.chunk_render_data[chunk_world_pos_key]
            return

        try:
            # struct module should be imported at the top of the file
            vertex_bytes = struct.pack(f'{len(mesh_vertices_data)}f', *mesh_vertices_data)
            vbo = self.ctx.buffer(vertex_bytes)
            # Assuming shader program 'self.program' is already loaded
            # and 'aPos', 'aNormal', 'aTexCoord' are its vertex attributes
            vao = self.ctx.vertex_array(
                self.program,
                [(vbo, '3f 3f 2f', 'aPos', 'aNormal', 'aTexCoord')]
            )
            self.chunk_render_data[chunk_world_pos_key] = {
                'vbo': vbo,
                'vao': vao,
                'vertex_count': len(mesh_vertices_data) // 8  # 8 floats per vertex
            }
        except Exception as e:
            print(f"Error creating VBO/VAO for chunk {chunk_world_pos_key}: {e}")


    def render_chunk(self, chunk_world_pos_key: tuple, chunk_world_pixel_pos: tuple,
                     view_matrix, projection_matrix):
        """
        Renders a specific chunk.
        chunk_world_pos_key: tuple (cx, cy, cz) to find the chunk's VBO/VAO.
        chunk_world_pixel_pos: tuple (px, py, pz) world position for model matrix translation.
        view_matrix: Camera's view matrix.
        projection_matrix: Projection matrix.
        """
        if chunk_world_pos_key not in self.chunk_render_data:
            return # Chunk mesh not generated or not uploaded

        render_entry = self.chunk_render_data[chunk_world_pos_key]
        if render_entry['vertex_count'] == 0:
            return # No vertices to render

        try:
            # Model matrix: translates the chunk mesh (which is in local chunk coords 0-15)
            # to its actual world position.
            model_matrix = matrix44.create_from_translation(chunk_world_pixel_pos, dtype='f4')
        except NameError: # pyrr might not be imported
            print("ERROR: pyrr.matrix44 not available for model_matrix. Using identity.")
            model_matrix = matrix44.create_identity(dtype='f4')
        except Exception as e:
            print(f"ERROR creating model matrix for chunk {chunk_world_pos_key}: {e}. Using identity.")
            model_matrix = matrix44.create_identity(dtype='f4')


        try:
            self.m_model_loc.write(model_matrix)
            self.m_view_loc.write(view_matrix)
            self.m_proj_loc.write(projection_matrix)
        except Exception as e:
            print(f"Error writing matrix uniforms for chunk {chunk_world_pos_key}: {e}")
            return

        if self.texture:
            self.texture.use(location=0)
            self.u_texture_loc.value = 0

        try:
            render_entry['vao'].render(moderngl.TRIANGLES)
        except Exception as e:
            print(f"Error rendering VAO for chunk {chunk_world_pos_key}: {e}")


    def destroy(self):
        """Clean up ModernGL resources."""
        print("Destroying Renderer resources...")
        for key, data in self.chunk_render_data.items():
            try:
                if data.get('vbo'): data['vbo'].release()
                if data.get('vao'): data['vao'].release()
            except Exception as e:
                print(f"Error releasing VBO/VAO for chunk {key}: {e}")
        self.chunk_render_data.clear()

        if hasattr(self, 'program') and self.program:
            self.program.release()
        if hasattr(self, 'texture') and self.texture:
            self.texture.release()
        print("Renderer resources released.")

if __name__ == '__main__':
    print("Renderer class defined. Requires a ModernGL context to instantiate and use.")
    # Example of how it might be used in main.py:
    # import pygame as pg
    # import moderngl
    # pg.init()
    # pg.display.set_mode((800, 600), flags=pg.OPENGL | pg.DOUBLEBUF)
    # ctx = moderngl.create_context()
    # renderer = Renderer(ctx)
    # # ... in game loop ...
    # # renderer.render_block((0,0,0), view_mat, proj_mat)
    # renderer.destroy()
    # pg.quit()
