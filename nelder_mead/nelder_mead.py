# -*- coding: utf-8 -*-

import numpy as np

from point import Point


class NelderMead(object):

    def __init__(self, func, params, *args, **kwargs):
        self.func = func
        self.dim = len(params)
        self.n_eval = 0
        self.names = []
        self.p_min = []
        self.p_max = []
        self.simplex = []

        self._parse_minmax(params)
        self._initialize()

    def maximize(self, n_iter=20, delta_r=1, delta_e=2, delta_ic=-0.5, delta_oc=0.5, gamma_s=0.5):
        self._coef = -1
        variables = locals()
        for k, v in variables.items():
            setattr(self, k, v)
        self._opt(n_iter)

    def minimize(self, n_iter=20, delta_r=1, delta_e=2, delta_ic=-0.5, delta_oc=0.5, gamma_s=0.5):
        self._coef = 1
        variables = locals()
        for k, v in variables.items():
            setattr(self, k, v)
        self._opt(n_iter)

    def func_impl(self, x):
        objval, invalid = None, False
        for i, t in enumerate(x):
            if t < self.p_min[i] or t > self.p_max[i]:
                objval = float("inf")
                invalid = True
        if not invalid:
            objval = self._coef * self.func(x)

        print("{:5d} | {} | {:>15.5f}".format(
            self.n_eval,
            " | ".join(["{:>15.5f}".format(t) for t in x]),
            self._coef * objval
        ))

        self.n_eval += 1
        return objval

    def _opt(self, n_iter):
        # Print Header
        print("{:>5} | {} | {:>15}".format(
            "Eval",
            " | ".join(["{:>15}".format(name) for name in self.names]),
            "ObjVal"
        ))
        print("-" * (20 + self.dim * 20))

        for p in self.simplex:
            p.f = self.func_impl(p.x)

        for i in range(n_iter):
            self.simplex = sorted(self.simplex, key=lambda p: p.f)

            # centroid
            p_c = self._centroid()
            # reflect
            p_r = self._reflect(p_c)

            if p_r < self.simplex[0]:
                p_e = self._expand(p_c)
                if p_e < p_r:
                    self.simplex[-1] = p_e
                else:
                    self.simplex[-1] = p_r
                continue
            elif p_r > self.simplex[-2]:
                if p_r <= self.simplex[-1]:
                    p_cont = self._outside(p_c)
                    if p_cont < p_r:
                        self.simplex[-1] = p_cont
                        continue
                    self.simplex[-1] = p_r
                elif p_r > self.simplex[-1]:
                    p_cont = self._inside(p_c)
                    if p_cont < self.simplex[-1]:
                        self.simplex[-1] = p_cont
                        continue

                # Shirnk
                for j in range(len(self.simplex) - 1):
                    p = Point(self.dim)
                    p.x = self.simplex[0].x + self.gamma_s * \
                        (self.simplex[j + 1].x - self.simplex[0].x)
                    p.f = self.func_impl(p.x)
                    self.simplex[j + 1] = p
            else:
                self.simplex[-1] = p_r

        self.simplex = sorted(self.simplex, key=lambda p: p.f)
        print("\nBest Point: {}".format(self.simplex[0]))

    def _centroid(self):
        p_c = Point(self.dim)
        x_sum = []
        for p in self.simplex[:-1]:
            x_sum.append(p.x)
        p_c.x = np.mean(x_sum, axis=0)
        return p_c

    def _reflect(self, p_c):
        return self._generate_point(p_c, self.delta_r)

    def _expand(self, p_c):
        return self._generate_point(p_c, self.delta_e)

    def _inside(self, p_c):
        return self._generate_point(p_c, self.delta_ic)

    def _outside(self, p_c):
        return self._generate_point(p_c, self.delta_oc)

    def _generate_point(self, p_c, x_coef):
        p = Point(self.dim)
        p.x = p_c.x + x_coef * (p_c.x - self.simplex[-1].x)
        p.f = self.func_impl(p.x)
        return p

    def _parse_minmax(self, params):
        for name, values in params.items():
            self.names.append(name)
            self.p_min.append(values[0])
            self.p_max.append(values[1])

    def _initialize(self):
        for i in range(self.dim + 1):
            p = Point(self.dim)
            init_val = [(m2 - m1) * np.random.random() + m1 for m1,
                        m2 in zip(self.p_min, self.p_max)]
            p.x = np.array(init_val, dtype=np.float32)
            self.simplex.append(p)