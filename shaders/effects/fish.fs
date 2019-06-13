vec2 m = vec2(0.5, 0.5);
vec2 d = coords-m;
float r = sqrt(dot(d, d));
float power = unif[16][1] * 2.2;
float bind;
vec2 uv = coords;
if (power > 0.0) {
    bind = sqrt(dot(m, m));
    uv = m +  normalize(d) * tan(r * power) * bind / tan(bind * power) ;
} else {
    bind = 0.5;
    uv = m +  normalize(d) * atan(r * power) * bind / atan(bind * power) ;
}
vec2 coords = uv;
