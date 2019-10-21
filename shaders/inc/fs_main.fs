// Assign texture coords to output
gl_FragColor = tex2D(tex0, coords);

// Apply alpha
#ifdef POST_PROCESS
gl_FragColor.a = unif[5][2];
#else
gl_FragColor.a *= unif[5][2];
#endif
