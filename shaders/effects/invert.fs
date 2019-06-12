float invertState = unif[15][0];

if (invertState == 1.0) {

    gl_FragColor = vec4(abs(1.0 - gl_FragColor.rgb), gl_FragColor.a);

}
