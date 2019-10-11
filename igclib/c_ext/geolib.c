#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <Python.h>

#define R 6371
#define TO_RAD (3.1415926536 / 180)


double c_haversine(double th1, double ph1, double th2, double ph2){
	double dx, dy, dz;
	ph1 -= ph2;
	ph1 *= TO_RAD, th1 *= TO_RAD, th2 *= TO_RAD;
 
	dz = sin(th1) - sin(th2);
	dx = cos(ph1) * cos(th1) - cos(th2);
	dy = sin(ph1) * cos(th1);
	return asin(sqrt(dx * dx + dy * dy + dz * dz) / 2) * 2 * R;
}

static PyObject* haversine(PyObject* self, PyObject* args){
	double th1, ph1, th2, ph2;

    if(!PyArg_ParseTuple(args, "dddd", &th1, &ph1, &th2, &ph2))
        return NULL;

    return Py_BuildValue("d", c_haversine(th1, ph1, th2, ph2));
}


static PyMethodDef methods[] = {
    { "haversine", haversine, METH_VARARGS, "Returns the distance between two points" },
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