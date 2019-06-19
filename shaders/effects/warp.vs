float w;
if (vertex.x < 0.) {
    if (vertex.y > 0.) {
        w = warp[0][0];
    } else {
        w = warp[0][3];
    }
} else {
    if (vertex.y > 0.) {
        w = warp[0][1];
    } else {
        w = warp[0][2];
    }
}

ucoords = vec3(coords.xy * w, w);

#ifdef MASK
umaskCoords = vec3(maskCoords.xy * w, w);
#endif
