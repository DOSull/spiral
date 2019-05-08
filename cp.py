import matplotlib.pyplot as plt
import numpy as np
import copy

class Parallelogram():

    def __init__(self, n=4, rotation=10, spirality=20):
        beta = 360 / n
        alpha = (180 - beta) / 2

        self.desc = "|".join([str(__) for __ in [n, rotation, spirality]])
        self.n = n
        self.rotn = rotation * np.pi / 180

        self.p1 = spirality * np.pi / 180
        self.r1 = (90 + rotation/2 - alpha) * np.pi / 180
        self.s = np.pi - self.p1 - self.r1

        #            R
        #    Q
        #
        #  P        S

        # define baseline PS
        P = (0., 0.)
        S = (1., 0.)

        # diagonal from P to R has length defined by the triangle PRS
        # in which we know angles at S and R, and length of PS(=) (opposite r1)
        PR = np.sin(self.s) / np.sin(self.r1)

        # so now we can find R
        R = (PR * np.cos(self.p1), PR * np.sin(self.p1))

        # lengths of PQ and RS are equal (by definition)
        RS = np.sqrt((R[0] - S[0])**2 + (R[1] - S[1])**2)
        PQ = RS

        # other angle at P is r1 - the rotational angle
        p2 = self.r1 - self.rotn

        Q = (PQ * np.cos(self.p1 + p2), PQ * np.sin(self.p1 + p2))

        # determine scale_factor and twist
        self.scale_factor = np.sqrt((Q[0] - R[0])**2 + (Q[1] - R[1])**2)
        self.twist = np.arctan((R[1] - Q[1]) / (R[0] - Q[0]))

        self.x = np.array([__[0] for __ in [P, Q, R, S, P]])
        self.y = np.array([__[1] for __ in [P, Q, R, S, P]])
        self.xy = np.array([self.x,
                           self.y,
                          [1., 1., 1., 1., 1.]])
        return

    def __str__(self):
        return "\n".join([str(__) for __ in [self.x, self.y]])

    def plot(self, p):
        p.plot(self.x, self.y, 'k')
        p.plot([self.x[0], self.x[2]], [self.y[0], self.y[2]], 'r')

    # rotates by the spirality angle, by default
    def rotate(self, rot):
        rot = rot
        rot_M = np.array([[np.cos(rot), -np.sin(rot), 0.],
                         [np.sin(rot), np.cos(rot), 0.],
                         [0., 0., 1.]])
        self.transform(rot_M)
        return

    def spiral(self):
        x0 = self.x[0]
        y0 = self.y[0]
        self.translate(-x0, -y0)
        self.rotate(self.rotn)
        self.translate(x0, y0)
        return

    # translates by sliding along the base edge
    def in_row_slide(self):
        self.translate(self.x[3] - self.x[0], self.y[3] - self.y[0])
        return

    def translate(self, dx, dy):
        translate_M = np.array([[1., 0., dx],
                            [0., 1., dy],
                            [0., 0., 1.]])
        self.transform(translate_M)
        return

    def transform(self, M):
        self.xy = M.dot(self.xy)
        self.x = self.xy[0]
        self.y = self.xy[1]
        return

    def scale(self, sf):
        scale_M = np.array([[sf, 0., 0.],
                         [0., sf, 0.],
                         [0., 0., 1.]])
        self.transform(scale_M)
        return

    def get_bbox(self):
        return (min(self.x), min(self.y), max(self.x), max(self.y))



class row():

    def __init__(self, P, **kwargs):
        self.shapes = []
        self.add_shape(P)
        rep = P.n
        if rep in kwargs: #.has_key('rep'):
            rep = kwargs['rep']
        for i in range(rep - 1):
            Pn = copy.deepcopy(self.shapes[-1])
            Pn.in_row_slide()
            Pn.spiral()
            self.add_shape(Pn)
        return

    def add_shape(self, P):
        self.shapes.append(P)
        return

    def get_bbox(self):
        bb = 0, 0, 0, 0
        for P in self.shapes:
            mm = [bounds for bounds in zip(bb, P.get_bbox())]
            bb = (min(mm[0]), min(mm[1]), max(mm[2]), max(mm[3]))
        return bb

    def plot(self, p):
        bb = self.get_bbox()
        for P in self.shapes:
            P.plot(p)
        return

    def get_sf_rotation(self):
        # based on edge QR edge of parallelogram
        P = self.shapes[0]
        return (P.scale_factor, P.twist)


class crease_pattern():

    def __init__(self, row, rpt=12):
        self.rows = [row]
        self.sf, self.twist = row.get_sf_rotation()
        dx1 = dx2 = dy1 = dy2 = 0
        S = r.shapes[0]
        dx1 = S.x[3]
        dy1 = S.y[3]
        dx2 = S.x[2] - S.x[0]
        dy2 = S.y[2] - S.y[0]
        self.edge_x = [0]
        self.edge_y = [0]
        for i in range(rpt):
            Rn = copy.deepcopy(self.rows[-1])
            for S in Rn.shapes:
                S.translate(-dx1, -dy1)
                S.scale(self.sf)
                S.rotate(self.twist)
                S.translate(dx2, dy2)
            S0 = Rn.shapes[0]
            self.edge_x.append(S0.x[0])
            self.edge_y.append(S0.y[0])
            self.rows.append(Rn)

    def plot(self, p):
        bb = self.get_bbox()
        p.axes().set_frame_on(False)
        p.axes().get_xaxis().set_visible(False)
        p.axes().get_yaxis().set_visible(False)
        p.axes().set_aspect('equal')
        p.axes().set_xlim([bb[0], bb[2]])
        p.axes().set_ylim([bb[1], bb[3]])
        for r in self.rows:
            r.plot(p)
        p.plot(self.edge_x, self.edge_y, 'k')
        bb = self.get_bbox()
        p.text(bb[2], bb[3], str(self), horizontalalignment='right', verticalalignment='top')

    def get_bbox(self):
        bb = (0, 0, 0, 0)
        for r in self.rows:
            mm = [bounds for bounds in zip(bb, r.get_bbox())]
            bb = (min(mm[0]), min(mm[1]), max(mm[2]), max(mm[3]))
        return bb

    def __str__(self):
        out = "Tomoko Fuse Spiral " + self.rows[0].shapes[0].desc + "\n"
        out += "Scaling: {:.5} Twist: {:.5}\n".format(self.sf, self.twist * 180. / np.pi)
        S = self.rows[0].shapes[0]
        out += "A: {:.4} B: {:.4} C: {:.4}\n".format(S.p1 * 180./np.pi, S.r1 * 180./np.pi, S.s * 180./np.pi)
        return out


# T = Triangle(4, 5, 20)
# r = row(T)
# cp = crease_pattern(r, rpt=16)
#
# cp.plot(plt)
# plt.show()

for n in range(3, 13, 3):
    beta = 360 / n
    max_r = beta / 2
    alpha = (180 - beta) / 2
    max_s = alpha
    for rtn in range(4, 26, 4): #[4, 5, 6, 8, 10, 11, 12.5, 15, 17.5, 20, 22.5, 25]:
        if rtn <= max_r:
            for sp in [10, 12.5, 15, 17.5, 20, 22.5, 25, 30, 35, 40, 45]:
                if sp <= max_s:
                    P = Parallelogram(n, rtn, sp)
                    r = row(P)
                    cp = crease_pattern(r, rpt=15)

                    f = plt.figure(figsize=[17, 22])
                    cp.plot(plt)
                    fn = "output/spiral_" + P.desc + ".pdf"
                    f.savefig(fn)
                    plt.close(f)

