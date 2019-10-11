#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define R 6372800.0
#define TO_RAD (3.1415926536 / 180)
#define MAX_WP 20

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

void c_optimize(double lat, double lon, double **wpts, int nb_wpt, double *res){
    
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

    int nb_wpts = PyList_Size(wpts);
    double **waypoints = (double **) malloc(nb_wpts * sizeof(double *)); 
    for (int i = 0; i < nb_wpts; i++){
        waypoints[i] = (double *) malloc(3 * sizeof(double));
    }

    for (int i = 0; i < nb_wpts; i++){
        PyObject *curr_wpt = PyList_GetItem(wpts, i);
        waypoints[i][0] = PyFloat_AsDouble(PyObject_GetAttrString(curr_wpt, "lat"));
        waypoints[i][1] = PyFloat_AsDouble(PyObject_GetAttrString(curr_wpt, "lon"));
        waypoints[i][2] = PyFloat_AsDouble(PyObject_GetAttrString(curr_wpt, "radius"));
    }

    double res[3];
    c_optimize(lat, lon, waypoints, nb_wpts, res);

    PyObject *obj = Py_BuildValue("[ddd]", res[0], res[1], res[2]);

    for (int i = 0; i < nb_wpts; i++){
        free(waypoints[i]); 
    }
    free(waypoints);

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

int main(){
    double a = c_haversine(36.12, -86.67, 33.94, -118.4);
    printf("dist: %.1f km\n", a);
}