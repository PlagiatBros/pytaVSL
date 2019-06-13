// Assign texture coords to output
gl_FragColor = texture2D(tex0, coords);

// Apply alpha
gl_FragColor.a *= unif[5][2];
