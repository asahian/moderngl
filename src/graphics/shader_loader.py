import moderngl

class ShaderError(Exception):
    """Custom exception for shader compilation/linking errors."""
    pass

def load_shader_program(ctx: moderngl.Context, vertex_shader_path: str, fragment_shader_path: str) -> moderngl.Program:
    """
    Loads, compiles, and links vertex and fragment shaders into a ModernGL program.
    Args:
        ctx: The ModernGL context.
        vertex_shader_path: Path to the vertex shader file.
        fragment_shader_path: Path to the fragment shader file.
    Returns:
        A ModernGL Program object.
    Raises:
        FileNotFoundError: If shader files are not found.
        ShaderError: If compilation or linking fails.
    """
    try:
        with open(vertex_shader_path, 'r') as f:
            vertex_shader_src = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Vertex shader file not found: {vertex_shader_path}")

    try:
        with open(fragment_shader_path, 'r') as f:
            fragment_shader_src = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Fragment shader file not found: {fragment_shader_path}")

    try:
        # Attempt to compile and link shaders
        # Note: ModernGL's Program object handles compilation and linking internally.
        # It raises an error if something goes wrong, which can be caught.
        program = ctx.program(
            vertex_shader=vertex_shader_src,
            fragment_shader=fragment_shader_src
        )
        return program
    except Exception as e: # ModernGL can raise various internal errors
        # It's good to catch the generic exception and re-raise as a ShaderError
        # to provide a consistent error type for the caller.
        # The error message from ModernGL usually contains details from GLSL compiler.
        error_message = f"Shader compilation/linking failed.\n"
        error_message += f"Vertex Shader: {vertex_shader_path}\n"
        error_message += f"Fragment Shader: {fragment_shader_path}\n"
        error_message += f"Error: {str(e)}"
        raise ShaderError(error_message)

if __name__ == '__main__':
    # This part is for testing and requires a ModernGL context.
    # It won't run in this environment directly without main.py setting up Pygame/ModernGL.
    print("Shader loader defined.")
    print("To test, run this as part of the main application where a ModernGL context is available.")
    # Example (pseudo-code, needs a real context):
    # try:
    #     ctx = moderngl.create_standalone_context() # Or get from Pygame
    #     shader_program = load_shader_program(ctx,
    #                                         'shaders/default_vertex.glsl',
    #                                         'shaders/default_fragment.glsl')
    #     print("Shader program loaded successfully (hypothetically).")
    # except Exception as e:
    #     print(f"Error during hypothetical test: {e}")
