import numpy as np
from scipy.optimize import minimize, basinhopping
from matplotlib import pyplot as plt


def tasklen(t, x, y, r):
    x_p = x + r*np.sin(t)
    y_p = y + r*np.cos(t)

    dists = np.sqrt(np.power(np.diff(x_p), 2) + np.power(np.diff(y_p), 2))

    return dists.sum()

def optplot(t, x, y, r):

    # Compute optimized points from angles
    x_p = x + r*np.sin(t)
    y_p = y + r*np.cos(t)
    
    _, ax = plt.subplots()
    ax.set_aspect('equal')

    plt.scatter(x, y, marker='x')
    plt.plot(x_p, y_p)

    for cx, cy, cr in zip(x, y, r):
        circle = plt.Circle((cx, cy), cr, color='b', fill=False)
        ax.add_artist(circle)

    plt.show()
    #plt.pause(0.01)


if __name__ == '__main__':
    #plt.ion()
    
    # Test 0
    X0 = np.array([0, 5, 0, -6, 0, 0])
    Y0 = np.array([0, 0, 4, 0, -3, 0])
    R0 = np.array([0, 2, 1, 3, 1, 0])
    x0 = np.zeros(R0.shape)

    res = minimize(tasklen, x0, args=(X0, Y0, R0))
    optplot(res.x, X0, Y0, R0)

    # Test 1
    X1 = np.array([0, -5, 1, 3, -1, 0])
    Y1 = np.array([0, 5, 12, 18, 25, 30])
    R1 = np.array([0, 6, 2, 4, 2, 0])
    x1 = np.ones(R1.shape)

    res = minimize(tasklen, x1, args=(X1, Y1, R1))
    optplot(res.x, X1, Y1, R1)

    # Test 2
    X2 = np.array([0, 10, 10, 10, 10, 10, 20])
    Y2 = np.array([0, 0, 0, 0, 0, 0, 0])
    R2 = np.array([0, 1, 5, 2, 6, 1, 0])
    x2 = np.ones(R2.shape)

    res = minimize(tasklen, x2, args=(X2, Y2, R2))
    optplot(res.x, X2, Y2, R2)

    # Test 3
    X3 = np.array([0, 1, -8, -2, 4, 10, 0])
    Y3 = np.array([0, 10, 20, 30, 40, 50, 60])
    R3 = np.array([0, 3, 9, 10, 5, 12, 0])
    x3 = np.ones(R3.shape)

    #res = minimize(tasklen, x3, args=(X3, Y3, R3))
    res = basinhopping(tasklen, x3, minimizer_kwargs=dict(args=(X3, Y3, R3)))
    optplot(res.x, X3, Y3, R3)

    #d = tasklen(T, X, Y, R)
    stop = True