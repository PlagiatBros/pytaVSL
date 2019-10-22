coords = texcoord * unib[2].xy + unib[3].xy;
maskCoords = texcoord;

#ifdef POST_PROCESS
coords.y = 1.0 - coords.y;
#endif


gl_Position = modelviewmatrix[1] * vec4(vertex,1.0);
