#version 330 core
out vec4 FragColor;

in vec2 TexCoord;

uniform sampler2D u_texture_0; // Basic texture sampler

void main()
{
    FragColor = texture(u_texture_0, TexCoord);
    // FragColor = vec4(1.0, 0.5, 0.2, 1.0); // Or a solid color for now if no texture
}
