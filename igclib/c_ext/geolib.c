#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "vc_vector.h"

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define R 6372800.0
#define TO_RAD (3.1415926536 / 180)

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

double c_haversine(double th1, double ph1, double th2, double ph2){
	double dx, dy, dz;
	ph1 -= ph2;
	ph1 *= TO_RAD, th1 *= TO_RAD, th2 *= TO_RAD;
 
	dz = sin(th1) - sin(th2);
	dx = cos(ph1) * cos(th1) - cos(th2);
	dy = sin(ph1) * cos(th1);
	return asin(sqrt(dx * dx + dy * dy + dz * dz) / 2) * 2 * R;
}

void c_optimize(t_pos position, vc_vector *wpts, int nb_wpts, t_result *res){
    vc_vector_push_back(res->fast_wp, &position);
    //printf("%d\n", nb_wpts);

    if (nb_wpts < 2){
        t_wp *last_wp  = vc_vector_back(wpts);
        res->dist_opti = c_haversine(position.lat, position.lon, last_wp->center.lat, last_wp->center.lon);
    } 
    else {
        
        for (int i = 0; i < nb_wpts; i++){
            t_wp *one = vc_vector_back(res->fast_wp);
            t_wp *two = vc_vector_at(wpts, i);
            t_wp *three = vc_vector_at(wpts, i+1);
        }
    }
}


/* PYTHON FUNCTION CALL INTERFACE */

static PyObject* haversine(PyObject* self, PyObject* args){
	double th1, ph1, th2, ph2;

    if(!PyArg_ParseTuple(args, "dddd", &th1, &ph1, &th2, &ph2))
        return NULL;

    return Py_BuildValue("d", c_haversine(th1, ph1, th2, ph2));
}

static PyObject* optimize(PyObject* self, PyObject* args){
	PyObject *pos;
	PyObject *wpts;

    if(!PyArg_ParseTuple(args, "OO", &pos, &wpts))
        return NULL;

    double lat = PyFloat_AsDouble(PyTuple_GetItem(pos, 0));
    double lon = PyFloat_AsDouble(PyTuple_GetItem(pos, 1));
    t_pos position = {lat, lon};

    int nb_wpts = PyList_Size(wpts);
    vc_vector* waypoints = vc_vector_create(nb_wpts, sizeof(t_wp), NULL);

    for (int i = 0; i < nb_wpts; i++){
        PyObject *curr_wpt = PyList_GetItem(wpts, i);
        t_wp wp = {
            {
                PyFloat_AsDouble(PyObject_GetAttrString(curr_wpt, "lat")),
                PyFloat_AsDouble(PyObject_GetAttrString(curr_wpt, "lon"))
            },
            PyFloat_AsDouble(PyObject_GetAttrString(curr_wpt, "radius"))
        };
        vc_vector_push_back(waypoints, &wp);
    }


    t_result *res = (t_result*) malloc(sizeof (t_result*));
    res->fast_wp = vc_vector_create(nb_wpts, sizeof (t_wp), NULL);
    res->legs_dist = vc_vector_create(nb_wpts, sizeof (double), NULL);
    c_optimize(position, waypoints, nb_wpts, res);

    PyObject *dist = Py_BuildValue("d", res->dist_opti);
    PyObject *fwp = Py_BuildValue("[]");
    PyObject *legs = Py_BuildValue("[]");

    PyObject *obj = Py_BuildValue("(OOO)", dist, fwp, legs);

    vc_vector_release(waypoints);
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