float maskHardness = unif[14][1];
float maskThresh = unif[14][2];


vec2 crds = maskCoords.xy;

crds.x -= mask_transform[0] / resolution.x;
crds.y -= mask_transform[1] / resolution.y;

vec4 maskColor = texture2D(tex1, crds);
float maskAlpha = distance(maskColor, vec4(0.0, 0.0, 0.0, 1.0));

maskAlpha += step(maskThresh, maskAlpha);
maskAlpha *= step(min(maskHardness, 1.0), maskAlpha);

gl_FragColor.a = gl_FragColor.a * maskAlpha;
