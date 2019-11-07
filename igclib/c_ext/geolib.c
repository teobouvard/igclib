#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define R  6378137.0
#define TO_RAD (M_PI / 180.0)
#define TO_DEG (180.0 / 3.14159265358979323846)
#define MIN(a,b) (((a)<(b))?(a):(b))


/* TYPES */

typedef struct t_wp{
    double lat;
    double lon;
    double radius;
} t_wp;


/* PURE C FUNCTIONS */


double c_distance(double lat1, double lon1, double lat2, double lon2, double kx, double ky){
	double dx = (lat1 - lat2) * kx;
	double dy = (lon1 - lon2) * ky;
    return sqrt(dx * dx + dy * dy);
}

t_wp c_destination(double lat, double lon, double distance, double heading, double kx, double ky){
	heading *= TO_RAD;
	double dx = sin(heading) * distance;
	double dy = cos(heading) * distance;
    t_wp end_point = {lat + dx / kx, lon + dy / ky, 0};
    return end_point;
}

double c_heading(double lat1, double lon1, double lat2, double lon2, double kx, double ky){
    lat1 *= TO_RAD, lat2 *= TO_RAD, lon1 *= TO_RAD, lon2 *= TO_RAD;
    double dx =  (lat2 - lat1) * kx;
    double dy =  (lon2 - lon1) * ky;

    if (!dx && !dy) return 0.;

    double heading = atan2(dx, dy) * TO_DEG;
    if (heading > 180) heading -= 360;

    return heading;
}

/* PYTHON FUNCTION CALL INTERFACE */

static PyObject* distance(PyObject* self, PyObject* args){
	double lat1, lon1, lat2, lon2, kx, ky;

    if(!PyArg_ParseTuple(args, "dddddd", &lat1, &lon1, &lat2, &lon2, &kx, &ky))
        return NULL;

    return Py_BuildValue("d", c_distance(lat1, lon1, lat2, lon2, kx, ky));
}

static PyObject* destination(PyObject* self, PyObject* args){
	double lat1, lon1, distance, heading, kx, ky;;

    if(!PyArg_ParseTuple(args, "dddddd", &lat1, &lon1, &distance, &heading, &kx, &ky))
        return NULL;

    t_wp offset = c_destination(lat1, lon1, distance, heading, kx, ky);
    return Py_BuildValue("(dd)", offset.lat, offset.lon);
}

static PyObject* heading(PyObject* self, PyObject* args){
	double lat1, lon1, lat2, lon2, kx, ky;

    if(!PyArg_ParseTuple(args, "dddddd", &lat1, &lon1, &lat2, &lon2, &kx, &ky))
        return NULL;

    return Py_BuildValue("d", c_heading(lat1, lon1, lat2, lon2, kx, ky));
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