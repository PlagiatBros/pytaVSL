vec2 m = vec2(0.5, 0.5);
vec2 d = coords-m;
float r = sqrt(dot(d, d));
float power = unif[16][1];
vec2 uv = coords;
if (power > 0.0) {
    uv = m +  normalize(d) * tan(r * power * 3.0) * 0.5 / tan(0.5* power * 3.0) ;
} else {
    uv = m +  normalize(d) * atan(r * power * 100.0) * 0.5 / atan(0.5* power * 100.0) ;
}
vec2 coords = uv;
