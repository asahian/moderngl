import moderngl
import pygame as pg # For texture loading, and image.tostring
from pyrr import matrix44 # For model matrix, matrix44.create_from_translation
import struct # For packing vertex data, though it's done in cube_mesh

# Local imports
from .cube_mesh import get_vertices_bytes # Corrected: directly use get_vertices_bytes
from .shader_loader import load_shader_program, ShaderError

class Renderer:
    def __init__(self, ctx: moderngl.Context):
        self.ctx = ctx

        # Load shader program
        try:
            self.program = load_shader_program(
                self.ctx,
                'src/graphics/shaders/default_vertex.glsl',
                'src/graphics/shaders/default_fragment.glsl'
            )
        except (FileNotFoundError, ShaderError) as e:
            print(f"Error loading shader program: {e}")
            # Handle error appropriately, e.g., raise or set a flag
            raise # Re-raise for now, main app should handle this

        # Get cube vertex data (packed as bytes)
        vertex_bytes = get_vertices_bytes()
        if not vertex_bytes:
            raise ValueError("Failed to get vertex data from cube_mesh.")

        # Create VBO
        self.vbo = self.ctx.buffer(vertex_bytes)

        # Create VAO
        # Format string: '3f 3f 2f' -> 3 floats for aPos, 3 floats for aNormal, 2 floats for aTexCoord
        # Attributes: 'aPos', 'aNormal', 'aTexCoord' matching shader inputs
        self.vao = self.ctx.vertex_array(
            self.program,
            [(self.vbo, '3f 3f 2f', 'aPos', 'aNormal', 'aTexCoord')]
        )

        # Placeholder texture loading
        self.texture = None
        try:
            # NOTE: The creation of 'assets/textures/placeholder.png' might fail due to tool limitations.
            # If the file is missing, pygame.image.load will raise an error.
            texture_surface = pg.image.load('assets/textures/placeholder.png').convert_alpha()
            texture_data = pg.image.tostring(texture_surface, 'RGBA', True) # Flipped for ModernGL
            self.texture = self.ctx.texture(texture_surface.get_size(), 4, texture_data)
            self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
            self.texture.swizzle = 'BGRA' # Pygame loads as BGR(A), convert to RGB(A) for shader
            print("Placeholder texture loaded successfully.")
        except pg.error as e:
            print(f"Pygame error loading texture 'assets/textures/placeholder.png': {e}")
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
            print(f"General error loading texture 'assets/textures/placeholder.png': {e}")
            self.texture = None


        # Store uniform locations
        try:
            self.m_model_loc = self.program['model']
            self.m_view_loc = self.program['view']
            self.m_proj_loc = self.program['projection']
            self.u_texture_loc = self.program['u_texture_0']
        except KeyError as e:
            print(f"Error getting uniform location: {e}. Shader might be compiled incorrectly or uniform misspelled.")
            raise # Re-raise for now

    def render_block(self, position, view_matrix, projection_matrix):
        """
        Renders a single block (cube) at the given world position.
        Args:
            position: A tuple or list (x,y,z) for the block's world position.
            view_matrix: The camera's view matrix (pyrr.Matrix44).
            projection_matrix: The projection matrix (pyrr.Matrix44).
        """
        # Create model matrix (translation from origin)
        # NOTE: Assumes pyrr is available. This will fail if pip install issues persist.
        try:
            model_matrix = matrix44.create_from_translation(position, dtype='f4')
        except NameError: # pyrr might not be imported due to installation failure
             print("ERROR: pyrr.matrix44 not available for model_matrix creation. Using identity.")
             model_matrix = matrix44.create_identity(dtype='f4') # Fallback to identity if pyrr fails
        except Exception as e:
             print(f"ERROR creating model matrix: {e}. Using identity.")
             model_matrix = matrix44.create_identity(dtype='f4')


        # Set uniforms
        # Ensure matrices are converted to bytes in a way ModernGL expects
        # .astype('f4') is for numpy arrays. pyrr matrices might need .tobytes() or similar
        # For pyrr.Matrix44, .tobytes() should work, or pass directly if ModernGL handles it.
        # ModernGL's write method can often handle pyrr matrices directly.
        try:
            self.m_model_loc.write(model_matrix)
            self.m_view_loc.write(view_matrix)
            self.m_proj_loc.write(projection_matrix)
        except Exception as e:
            print(f"Error writing matrix uniforms: {e}")
            return # Avoid rendering if uniforms can't be set

        # Use the texture
        if self.texture:
            self.texture.use(location=0) # Bind texture to texture unit 0
            self.u_texture_loc.value = 0 # Tell shader to use texture unit 0
        else:
            # What to do if no texture? Shader might sample garbage or a default (often black)
            # Or, have a version of the shader that uses a flat color.
            # For now, it will likely sample incorrectly if texture is None and shader expects one.
            # The fragment shader has a commented out solid color line.
            pass

        # Render the VAO
        try:
            self.vao.render(moderngl.TRIANGLES)
        except Exception as e:
            print(f"Error during VAO render: {e}")

    def destroy(self):
        """Clean up ModernGL resources."""
        if hasattr(self, 'vbo'): self.vbo.release()
        if hasattr(self, 'vao'): self.vao.release()
        if hasattr(self, 'program'): self.program.release()
        if hasattr(self, 'texture') and self.texture: self.texture.release()
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
