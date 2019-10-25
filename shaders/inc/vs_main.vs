coords = texcoord * unib[2].xy + unib[3].xy;
maskCoords = texcoord;

#ifndef TEXT
#ifndef VIDEO
coords.y = 1.0 - coords.y;
maskCoords.y = 1.0 - maskCoords.y;
#endif
#endif

gl_Position = modelviewmatrix[1] * vec4(vertex,1.0);

#ifdef WARP
#include shaders/effects/warp.vs
#endif
