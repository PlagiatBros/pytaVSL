float maskHardness = unif[14][1];
float maskThresh = unif[14][2];

vec4 maskColor = texture2D(tex1, maskCoords);
float maskAlpha = distance(maskColor, vec4(0.0, 0.0, 0.0, 1.0));

maskAlpha += step(maskThresh, maskAlpha);
maskAlpha *= step(min(maskHardness, 1.0), maskAlpha);

gl_FragColor.a = gl_FragColor.a * maskAlpha;
