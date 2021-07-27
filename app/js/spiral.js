function getTranslationMatrix(dx, dy) {
  return [
    [1, 0, dx],
    [0, 1, dy],
    [0, 0, 1]
  ];
}

function getScaleMatrix(s) {
  return [
    [s, 0, 0],
    [0, s, 0],
    [0, 0, 1]
  ];
}

function getRotationMatrix(theta) { // theta in radians
  return [
    [Math.cos(theta), Math.sin(theta), 0],
    [-Math.sin(theta), Math.cos(theta), 0],
    [0, 0, 1]
  ];
}

function transform(v, M) {
  return [
    M[0][0] * v[0] + M[0][1] * v[1] + M[0][2] * v[2],
    M[1][0] * v[0] + M[1][1] * v[1] + M[1][2] * v[2],
    M[2][0] * v[0] + M[2][1] * v[1] + M[2][2] * v[2],
  ];
}

function getBaseQuad(n, rotation, spirality) {
  let beta = 360 / n;
  let alpha = (180 - beta) / 2;

  let rotn = rotation * Math.PI / 180;

  //          R
  //    S
  //         Q
  //  P
  let p1 = spirality * Math.PI / 180;
  let r1 = (90 + rotation / 2 - alpha) * Math.PI / 180;
  let q = Math.PI - p1 - r1

  let P = [0, 0, 1];
  let Q = [1, 0, 1];
  let PR = Math.sin(q) / Math.sin(r1);
  let R = [PR * Math.cos(p1), PR * Math.sin(p1), 1];
  let QR = Math.hypot(R[0] - Q[0], R[1] - Q[1]);
  let SP = QR;

  let p2 = r1 - rotn;
  let S = [Math.cos(p1 + p2), Math.sin(p1 + p2), 1];
  return [P, Q, R, S];
}


// def __init__(self, n=4, rotation=10, spirality=20):
//     beta = 360 / n
//     alpha = (180 - beta) / 2
//
//     self.desc = "|".join([str(__) for __ in [n, rotation, spirality]])
//     self.n = n
//     self.rotn = rotation * np.pi / 180
//
//     self.p1 = spirality * np.pi / 180
//     self.r1 = (90 + rotation/2 - alpha) * np.pi / 180
//     self.s = np.pi - self.p1 - self.r1
//
//     #            R
//     #    Q
//     #
//     #  P        S
//
//     # define baseline PS
//     P = (0., 0.)
//     S = (1., 0.)
//
//     # diagonal from P to R has length defined by the triangle PRS
//     # in which we know angles at S and R, and length of PS(=) (opposite r1)
//     PR = np.sin(self.s) / np.sin(self.r1)
//
//     # so now we can find R
//     R = (PR * np.cos(self.p1), PR * np.sin(self.p1))
//
//     # lengths of PQ and RS are equal (by definition)
//     RS = np.sqrt((R[0] - S[0])**2 + (R[1] - S[1])**2)
//     PQ = RS
//
//     # other angle at P is r1 - the rotational angle
//     p2 = self.r1 - self.rotn
//
//     Q = (PQ * np.cos(self.p1 + p2), PQ * np.sin(self.p1 + p2))
//
//     # determine scale_factor and twist
//     self.scale_factor = np.sqrt((Q[0] - R[0])**2 + (Q[1] - R[1])**2)
//     self.twist = np.arctan((R[1] - Q[1]) / (R[0] - Q[0]))
//
//     self.x = np.array([__[0] for __ in [P, Q, R, S, P]])
//     self.y = np.array([__[1] for __ in [P, Q, R, S, P]])
//     self.xy = np.array([self.x,
//                        self.y,
//                       [1., 1., 1., 1., 1.]])
//     return
