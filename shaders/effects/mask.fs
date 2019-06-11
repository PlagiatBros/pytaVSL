float maskState = unif[19][0];
float maskHardness = unif[19][1];
float maskThresh = unif[19][2];

vec4 maskColor = texture2D(tex1, maskCoords);
float maskAlpha = distance(maskColor, vec4(0.0, 0.0, 0.0, 1.0));

maskAlpha += step(maskThresh, maskAlpha);
maskAlpha *= step(min(maskHardness, 1.0), maskAlpha);

gl_FragColor.a = gl_FragColor.a * (1.0 - maskState + maskAlpha * maskState);
