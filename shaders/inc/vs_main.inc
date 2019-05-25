coords = texcoord * unib[2].xy + unib[3].xy;
gl_Position = modelviewmatrix[1] * vec4(vertex,1.0);
