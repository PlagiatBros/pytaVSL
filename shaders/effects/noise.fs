float noiseDensity = unif[19][0];
float noiseSeedX = unif[19][1];
float noiseSeedY = unif[19][2];

gl_FragColor.rgb = texture2D(tex0, (8.0 - 8.0 * noiseDensity + 0.5) * vec2(noise(coords * rand / (1.0 + noiseSeedX * 20000.0)), noise(coords * rand / (1.0 - noiseSeedY * 20000.0)))).rgb;
gl_FragColor.rgb = step(vec3(0.5, 0.5, 0.5), gl_FragColor.rgb) * gl_FragColor.rgb;
