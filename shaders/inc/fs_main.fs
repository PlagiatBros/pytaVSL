// Assign texture coords to output
gl_FragColor = tex2D(tex0, coords);

// Apply alpha
gl_FragColor.a = gl_FragColor.a * unif[5][2];
