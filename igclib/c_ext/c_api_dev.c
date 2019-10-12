#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "vc_vector.h"

#define R 6372800.0
#define TO_RAD (3.14159265358979323846 / 180.0)
#define TO_DEG (180.0 / 3.14159265358979323846)
#define MIN_WP_DIST 50
#define MIN(a,b) (((a)<(b))?(a):(b))

/* TYPES */

typedef struct t_pos{
    double lat;
    double lon;
} t_pos;

typedef struct t_wp{
    t_pos center;
    double radius;
} t_wp;

typedef struct t_result{
    vc_vector *fast_wp;
    vc_vector *legs_dist;
    double dist_opti;
} t_result;

/* PURE C FUNCTIONS */

double c_haversine(double lat1, double lon1, double lat2, double lon2){
	double dx, dy, dz;
	lon1 -= lon2;
	lon1 *= TO_RAD, lat1 *= TO_RAD, lat2 *= TO_RAD;
 
	dz = sin(lat1) - sin(lat2);
	dx = cos(lon1) * cos(lat1) - cos(lat2);
	dy = sin(lon1) * cos(lat1);
	return asin(sqrt(dx * dx + dy * dy + dz * dz) / 2) * 2 * R;
}

t_pos c_offset(double lat1, double lon1, double distance, double heading){
    lat1 *= TO_RAD, lon1 *= TO_RAD, heading *= TO_RAD;
    double lat2 =  asin(sin(lat1) * cos(distance/R)  + cos(lat1) * sin(distance/R) * cos(heading));
    double lon2 = lon1 + atan2(sin(heading) * sin(distance/R) * cos(lat1) , cos(distance/R) - sin(lat1) * sin(lat2));
    t_pos end_point = {lat2 *= TO_DEG, lon2 *= TO_DEG};
    return end_point;
}

double c_heading(double lat1, double lon1, double lat2, double lon2){
    lat1 *= TO_RAD, lat2 *= TO_RAD, lon1 *= TO_RAD, lon2 *= TO_RAD;
    double x =  cos(lat2) * sin(lon2-lon1);
    double y =  cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(lon2-lon1);
    double heading = atan2(x, y) * TO_DEG;
    return heading;
}

void c_optimize(t_pos position, vc_vector *wpts, int nb_wpts, t_result *res){
    double in_heading, out_heading, pivot_heading;
    double in_distance, out_distance, pivot_distance, next_distance;
    double angle;

    t_wp fwp;
    t_wp *last_wp;
    t_wp *last_fwp;

    vc_vector_push_back(res->fast_wp, &position);

    if (nb_wpts < 2){
        last_wp  = vc_vector_back(wpts);
        vc_vector_push_back(res->fast_wp, last_wp);
        res->dist_opti = c_haversine(position.lat, position.lon, last_wp->center.lat, last_wp->center.lon);
        vc_vector_push_back(res->legs_dist, &res->dist_opti);
    } 

    else {
        
        for (int i = 0; i < nb_wpts; i++){
            t_wp *one = vc_vector_back(res->fast_wp);
            t_wp *two = vc_vector_at(wpts, i);
            t_wp *three = vc_vector_at(wpts, i+1);

            in_heading = c_heading(two->center.lat, two->center.lon, one->center.lat, one->center.lon);
            in_distance = c_haversine(two->center.lat, two->center.lon, one->center.lat, one->center.lon);
            out_distance = c_haversine(two->center.lat, two->center.lon, three->center.lat, three->center.lon);

            if (out_distance <  MIN_WP_DIST){
                out_heading = 0; // TODO
                pivot_distance = two->radius;
                pivot_heading = in_heading; // TODO
            }
            else{
                out_heading = c_heading(two->center.lat, two->center.lon, three->center.lat, three->center.lon);
                angle = fmod(out_heading - in_heading + 540.0, 360.0) - 180.0;
                pivot_heading = in_heading  + 0.5 * angle;
                pivot_distance = (2.0 * in_distance * out_distance * cos(angle * 0.5 * TO_RAD)) / (in_distance + out_distance);
            }

            pivot_distance = MIN(pivot_distance, two->radius);
            fwp.center = c_offset(two->center.lat, two->center.lon, pivot_distance, pivot_heading);
            fwp.radius = two->radius;
            vc_vector_push_back(res->fast_wp, &fwp);

            next_distance = c_haversine(one->center.lat, one->center.lon, fwp.center.lat, fwp.center.lon);
            vc_vector_push_back(res->legs_dist, &next_distance);
            res->dist_opti += next_distance;
        }

        
        last_fwp = vc_vector_back(res->fast_wp);
        last_wp  = vc_vector_back(wpts);
        next_distance = c_haversine(last_fwp->center.lat, last_fwp->center.lon, last_wp->center.lat, last_wp->center.lon);
        vc_vector_push_back(res->legs_dist, &next_distance);
        
        vc_vector_push_back(res->fast_wp, vc_vector_back(wpts));
        res->dist_opti += next_distance;
    }
}

int main(){

    int nb_wpts = 3;
    t_wp wp1 = {0, 0, 100};
    t_wp wp2 = {0.5, 0, 10000};
    t_wp wp3 = {0.5, 0.5, 10000};
    t_wp wp4 = {0, 0.5, 10000};
    t_pos pos = {0, 0};

    vc_vector *wpts = vc_vector_create(3, sizeof(t_wp), NULL);
    //vc_vector_push_back(wpts, &wp1);
    vc_vector_push_back(wpts, &wp2);
    vc_vector_push_back(wpts, &wp3);
    vc_vector_push_back(wpts, &wp4);
    vc_vector_push_back(wpts, &wp1);

    t_result *res = (t_result*) malloc(sizeof (t_result*));
    res->fast_wp = vc_vector_create(nb_wpts+1, sizeof (t_wp), NULL);
    res->legs_dist = vc_vector_create(nb_wpts, sizeof (double), NULL);
    c_optimize(pos, wpts, nb_wpts, res);


    vc_vector_release(wpts);
    vc_vector_release(res->fast_wp);
    vc_vector_release(res->legs_dist);
    free(res);

    return 0;
}