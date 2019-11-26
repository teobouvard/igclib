#include "geodesic.h"
#include <stdlib.h>

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define A 6378137         /* WGS84 */
#define F 1/298.257223563 /* WGS84 */


/* TYPES */

typedef struct geopoint{
    double lat;
    double lon;
} geopoint;


/* PURE C FUNCTIONS */


double c_distance(double lat1, double lon1, double lat2, double lon2){
    double distance;
    struct geod_geodesic g;
    geod_init(&g, A, F);
    geod_inverse(&g, lat1, lon1, lat2, lon2, &distance, 0, 0);
    return distance;
}

geopoint c_destination(double lat, double lon, double distance, double heading){
    geopoint end_point;
    struct geod_geodesic g;
    geod_init(&g, A, F);
    geod_direct(&g, lat, lon, heading, distance, &end_point.lat, &end_point.lon, 0);
    return end_point;
}

double c_heading(double lat1, double lon1, double lat2, double lon2){
    double heading;
    struct geod_geodesic g;
    geod_init(&g, A, F);
    geod_inverse(&g, lat1, lon1, lat2, lon2, 0, &heading, 0);
    return heading;
}

/* PYTHON FUNCTION CALL INTERFACE */

static PyObject* distance(PyObject* self, PyObject* args){
	double lat1, lon1, lat2, lon2;

    if(!PyArg_ParseTuple(args, "dddd", &lat1, &lon1, &lat2, &lon2))
        return NULL;

    return Py_BuildValue("d", c_distance(lat1, lon1, lat2, lon2));
}

static PyObject* destination(PyObject* self, PyObject* args){
	double lat1, lon1, distance, heading;

    if(!PyArg_ParseTuple(args, "dddd", &lat1, &lon1, &distance, &heading))
        return NULL;

    geopoint offset = c_destination(lat1, lon1, distance, heading);
    return Py_BuildValue("(dd)", offset.lat, offset.lon);
}

static PyObject* heading(PyObject* self, PyObject* args){
	double lat1, lon1, lat2, lon2;

    if(!PyArg_ParseTuple(args, "dddd", &lat1, &lon1, &lat2, &lon2))
        return NULL;

    return Py_BuildValue("d", c_heading(lat1, lon1, lat2, lon2));
}


/* EXPORT MODULE TO PYTHON */

static PyMethodDef methods[] = {
    { "distance", distance, METH_VARARGS, "Returns the distance between two points" },
    { "destination", destination, METH_VARARGS, "Returns the arrival point given an origin point, a distance and a heading" },
    { "heading", heading, METH_VARARGS, "Returns the heading between two points" },
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