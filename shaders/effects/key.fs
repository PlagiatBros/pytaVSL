vec3 keyRgb = unif[13];
float keyThreshold = unif[14][0];

gl_FragColor.a *= step(keyThreshold, abs(distance(gl_FragColor.rgb, keyRgb)));
