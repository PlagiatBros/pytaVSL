float invertState = step(1.0, unif[17][1]);

gl_FragColor = vec4(gl_FragColor.rgb * (1.0 - invertState) + abs(1.0 - gl_FragColor.rgb) * invertState, gl_FragColor.a);
