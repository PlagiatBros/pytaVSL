vec3 keyRgb = unif[16];
float keyThreshold = unif[17][0];

gl_FragColor.a *= step(keyThreshold, abs(distance(gl_FragColor.rgb, keyRgb)));
