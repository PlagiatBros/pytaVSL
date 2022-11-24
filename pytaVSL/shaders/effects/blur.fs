float gauss( float x, float sigma)
{
    if (sigma <= 0.0) return 0.0;
    return exp(-(x * x) / ( 2.0 * sigma)) / ( 2.0 * 3.14157 * sigma);
}

vec3 add_blur(vec3 fragColor, float radius)
{

    const float sigma = 10.0;
    vec2 step     = 1.0 / resolution;
    vec4 texCol   = tex2D(tex0, coords);
    vec4 gaussCol = vec4(texCol.rgb, 1.0);

    float weight;
    for (int i = 1; i <= 16; ++ i)
    {
        weight = gauss(float(i) / 16.0, sigma * 0.5);

        if (weight < 1.0 / 255.0) break;

        texCol    = tex2D(tex0, coords + radius * step * float(i));
        gaussCol += vec4(texCol.rgb * weight, weight);
        texCol    = tex2D(tex0, coords - radius * step * float(i));
        gaussCol += vec4(texCol.rgb * weight, weight);
    }

   gaussCol.rgb = clamp(gaussCol.rgb / gaussCol.w, 0.0, 1.0);

   return gaussCol.rgb;

}
