/*

    Very dirty projective warping adapted from https://www.shadertoy.com/view/Xs3GWN by FabriceNeyret2

*/

#define wrap_eps 1e-4


vec4 apply_warp(vec4 fragColor, vec2 coords)
{

    vec2 R = resolution;
    vec2 uv;
    vec2 uv2;
	vec2 p = coords * 2.0 - vec2(1., 0.) ;

    bool deg, swap, lin;
    float d, W=1.,H=1., Y=1.;

    // --- quadrilateral bilinear patch
    vec3 A = vec3(-W,-H+Y, 1.),
         B = vec3( W,-H+Y, 1.),
         C = vec3(-W, H+Y, 1.),
         D = vec3( W, H+Y, 1.);

    // --- solve sys3x3: bilin(uv) = (xe,ye,1)*Z  ( equivalent to intersec ray - patch )

    // eliminates Z, sys2x2: L12 -= (xe,ye).L3
    A.xy -= p*A.z;
    B.xy -= p*B.z;
    C.xy -= p*C.z;
    D.xy -= p*D.z;


    // Apply xy warping from uniform "warp"
    A.x += 2. * warp[0][0] + wrap_eps;
    A.y -= 2. * warp[0][1] + wrap_eps;
    B.x += 2. * warp[1][0];
    B.y -= 2. * warp[1][1];
    C.x += 2. * warp[3][0] - wrap_eps;
    C.y -= 2. * warp[3][1] - wrap_eps;
    D.x += 2. * warp[2][0];
    D.y -= 2. * warp[2][1];

    vec3 AB = B-A, AC = C-A, CD = D-C, ABCD = CD-AB; // bilin = A + u.AB + v.AC +uv.ABCD = 0

    if (lin = length(ABCD.xy) < wrap_eps) { // no uv: the system is indeed linear !
	    A.z  = cross(A ,AC).z; // eliminates v -> gives u
    	AB.z = cross(AB,AC).z;
        uv.x = -A.z/AB.z;
        uv.y = -A.y/AC.y -AB.y/AC.y*uv.x; // inject u in L2 -> gives v
        uv2 = uv;
    }
    else {   // full bilinear system.  eliminates uv -> sys1: Az + u.ABz + v.ACz = 0
    	A.z  = cross(A ,ABCD).z;
    	AB.z = cross(AB,ABCD).z;
    	AC.z = cross(AC,ABCD).z;

		float e = -A.z/AC.z, f = -AB.z/AC.z, // ->  v = e + u.f
		// inject v in L2 -> P2(u): a.u^2 + b.u + c = 0    -> solve P2(u) then v
		    a = ABCD.y*f, b = ABCD.y*e + AC.y*f + AB.y, c = AC.y*e + A.y;
		    d = b*b-4.*a*c;
		if (lin = abs(a)<wrap_eps)  // <><><> better to use bigger wrap_eps: near-lin is unstable
            uv2.x = uv.x  = -c/b; // no parabolic term
        else {
		    uv.x  = (-b+sqrt(d))/a/2.;
			uv2.x = (-b-sqrt(d))/a/2.;
		}
		uv.y  = e + f*uv.x;
		uv2.y = e + f*uv2.x;

    }

    // --- select valid solution and display

    uv  = 2.*uv -1.;
    uv2 = 2.*uv2-1.;
    if ( swap = abs(uv.x)>1. || abs(uv.y)>1.) uv = uv2;
    float l = length(uv);



    if (d<0. || abs(uv.x)>1. || abs(uv.y)>1.) return vec4(0.,0.,0.,0.);
    else {
	    return texture2D(tex0,.5+.5*uv);
    }


}
