#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "vc_vector.h"

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define R  6378137.0
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
    double dist_opti;
    double *legs_dist;
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
    double in_distance, out_distance, pivot_distance;
    double next_distance;
    double angle;

    t_wp fwp;
    t_wp *last_wp;
    t_wp *last_fwp;

    vc_vector_push_back(res->fast_wp, &position);

    if (nb_wpts < 2){
        last_wp  = vc_vector_back(wpts);
        vc_vector_push_back(res->fast_wp, last_wp);
        res->dist_opti = c_haversine(position.lat, position.lon, last_wp->center.lat, last_wp->center.lon);
        res->legs_dist[0] = res->dist_opti;
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
            res->legs_dist[i] = next_distance;
            res->dist_opti += next_distance;
        }

        
        last_fwp = vc_vector_back(res->fast_wp);
        last_wp  = vc_vector_back(wpts);
        next_distance = c_haversine(last_fwp->center.lat, last_fwp->center.lon, last_wp->center.lat, last_wp->center.lon);
        res->legs_dist[nb_wpts] = next_distance;
        
        vc_vector_push_back(res->fast_wp, vc_vector_back(wpts));
        res->dist_opti += next_distance;
    }
}

/* PYTHON FUNCTION CALL INTERFACE */

static PyObject* haversine(PyObject* self, PyObject* args){
	double lat1, lon1, lat2, lon2;

    if(!PyArg_ParseTuple(args, "dddd", &lat1, &lon1, &lat2, &lon2))
        return NULL;

    return Py_BuildValue("d", c_haversine(lat1, lon1, lat2, lon2));
}

static PyObject* optimize(PyObject* self, PyObject* args){
	PyObject *pos;
	PyObject *wpts;
	PyObject *curr_wpt;

    // parse arguments
    if(!PyArg_ParseTuple(args, "OO", &pos, &wpts))
        return NULL;

    // create C types from arguments
    t_pos position = {
        PyFloat_AsDouble(PyTuple_GetItem(pos, 0)), 
        PyFloat_AsDouble(PyTuple_GetItem(pos, 1))
    };

    int nb_wpts = PyList_Size(wpts);
    t_wp *waypoints = vc_vector_create(nb_wpts, sizeof(t_wp), NULL);

    for (int i = 0; i < nb_wpts; i++){
        curr_wpt = (PyObject*) PyList_GetItem(wpts, i);
        t_wp wp = {
            {
                PyFloat_AsDouble(PyObject_GetAttrString(curr_wpt, "lat")),
                PyFloat_AsDouble(PyObject_GetAttrString(curr_wpt, "lon"))
            },
            PyFloat_AsDouble(PyObject_GetAttrString(curr_wpt, "radius"))
        };
        vc_vector_push_back(waypoints, &wp);
    }

    // create a result type, to be filled by c_optimize
    t_result *res = (t_result*) malloc(sizeof (t_result*));
    res->fast_wp = vc_vector_create(nb_wpts, sizeof (t_wp), NULL);
    res->legs_dist = malloc(nb_wpts * sizeof (double));
    c_optimize(position, waypoints, nb_wpts, res);

    // create python types to be returned
    PyObject *optimized_dist = Py_BuildValue("d", res->dist_opti);
    PyObject *fwp = Py_BuildValue("[]");
    PyObject *legs = Py_BuildValue("[]");

    for (int i = 0; i < nb_wpts; i++){
        PyList_Append(legs, Py_BuildValue("d", res->legs_dist[i]));
        t_wp *wp = vc_vector_at(res->fast_wp, i);
        PyObject_SetAttrString(curr_wpt, "lat", Py_BuildValue("d", wp->center.lat));
        PyObject_SetAttrString(curr_wpt, "lon", Py_BuildValue("d", wp->center.lon));
        PyObject_SetAttrString(curr_wpt, "radius", Py_BuildValue("d", wp->radius));
        PyList_Append(fwp, curr_wpt);
    }

    PyObject *obj = Py_BuildValue("(OOO)", optimized_dist, fwp, legs);

    // free allocated memory
    vc_vector_release(waypoints);
    vc_vector_release(res->fast_wp);
    free(res->legs_dist);
    free(res);
    
    return obj;
}


/* EXPORT MODULE TO PYTHON */

static PyMethodDef methods[] = {
    { "haversine", haversine, METH_VARARGS, "Returns the distance between two points" },
    { "optimize", optimize, METH_VARARGS, "Returns the optimized distance through waypoints" },
    { NULL, NULL, 0, NULL }
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "geolib",
    "Geographic computations module",
    -1,
    methods
};

PyMODINIT_FUNC PyInit_geolib(void){
    return PyModule_Create(&module);
}