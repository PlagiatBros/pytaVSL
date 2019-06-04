// PostProcess only
gl_FragColor.a += 1.0 * unib[4][1];

// Video only
float bgr2rgb = step(1.0, unib[4][0]);
gl_FragColor.rgb = gl_FragColor.rgb * (1.0 - bgr2rgb) + gl_FragColor.bgr * bgr2rgb;
