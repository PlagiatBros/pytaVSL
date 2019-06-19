// bilinear interpolation
// disable: projective interpolation (warp.fs) is used instead 

vec2 BL, BR, TL, TR;

TL=vec2(0.0, 1.0) + warp[0];
TR=vec2(1.0, 1.0) + warp[1];
BR=vec2(1.0, 0.0) + warp[2];
BL=vec2(0.0, 0.0) + warp[3];

// transform from -1...1 to 0...1
vec2 p = (gl_Position.xy + 1.) * 0.5;

// interpolate bottom edge x coordinate
vec2 x1 = mix(BL, BR, p.x);
// interpolate top edge x coordinate
vec2 x2 = mix(TL, TR, p.x);
// interpolate y position
p = mix(x1, x2, p.y);


// transform from 0...1 to -1...1
p = p  * 2.0 - 1.0;

gl_Position.xy = p;
