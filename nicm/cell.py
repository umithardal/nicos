#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   HKL transformation routines.
#
# Author:
#   Klaudia Hradil (klaudia.hradil@frm2.tum.de)
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""HKL transformation routines between crystal coordinates and physical device
coordinates.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from numpy import arccos, arcsin, arctan2, cos, sin, pi, sqrt, \
     array, identity, zeros, cross, dot, sign
from numpy.linalg import inv, norm

from nicm.device import Device, Param
from nicm.errors import ComputationError, ConfigurationError
from nicm.utils import vec3

D2R = pi/180
R2D = 180/pi
# conversion from THz to A^-2
K = 1.99573


class Cell(Device):
    """
    Cell object representing sample geometry.

    XXX _angles_rec is in radians, _angles is in degrees
    """

    parameters = {
        'lattice': Param('Lattice constants', type=vec3,
                         default=[2*pi, 2*pi, 2*pi], settable=True, info=True),
        'angles':  Param('Lattice angles', type=vec3,
                         default=[90, 90, 90], settable=True, info=True),
        'orient1': Param('First orientation reflex', type=vec3,
                         default=[1, 0, 0], settable=True, info=True),
        'orient2': Param('Second orientation reflex', type=vec3,
                         default=[0, 1, 0], settable=True, info=True),
        # XXX seems to belong rather to TAS and not Cell
        'psi0':    Param('Zero position of psi axis', settable=True, info=True),
        'axiscoupling': Param('Whether the sample th/tt axes are coupled',
                              type=bool, default=True, settable=True),
        'psi360':  Param('Whether the range of psi is 0-360 deg '
                         '(otherwise -180-180 deg is assumed).',
                         type=bool, default=True, settable=True),
        # XXX not used?
        'coordinatesystem': Param('Coordinate system for k_i: 1 parallel x, '
                                  '-1 parallel -x, 2 parallel y, '
                                  '-2 parallel -y.',
                                  type=int, default=1, settable=True),
    }

    def _reinit(self, lattice=None, angles=None,
                orient1=None, orient2=None, psi0=None):
        # calculate reciprocal lattice
        self._lattice_rec, self._angles_rec = self.lattice_rec()
        # matrix for rotation about z lab system with psi
        self._matrix = self.matrix_crystal2lab()
        # matrix for rotation about sgx, sgy for psi = 0; never changed so far
        self._matrix_cardan = identity(3)
        #self._matrix_psi = identity(3)
        # matrix for rotation about echi, ephi, for psi = 0 (not used)
        #self._matrix_euler  = identity(3)

    def _info(self):
        print 'direct lattice:   %4.7f   %4.7f   %4.7f' % tuple(self._lattice)
        print 'direct angles:    %4.7f   %4.7f   %4.7f' % tuple(self._angles)
        print 'recip. lattice:   %4.7f   %4.7f   %4.7f' % tuple(self._lattice_rec)
        print 'recip. angles:    %4.7f   %4.7f   %4.7f' % tuple(x * R2D for x in self._angles_rec)
        print 'plane vectors:    (%s %s %s), (%s %s %s)' % (tuple(self._orient1) + tuple(self._orient2))
        print 'zone axis:        [%s %s %s]' % tuple(self.cal_zone())
        print 'psi0:             %4.3f' % (self._psi0 * R2D)
        print 'cardan matrix:    \n%s' % self._matrix_cardan
        print 'hkl2Qcart matrix: \n%s' % self._matrix


    def doInit(self):
        self._lattice = array(self.lattice, float)
        self._angles = array(self.angles, float)
        self._orient1 = array(self.orient1, float)
        self._orient2 = array(self.orient2, float)
        self._psi0 = self.psi0
        self._reinit()

    def doWriteLattice(self, val):
        self._lattice = array(val, float)
        self._reinit()

    def doWriteAngles(self, val):
        self._angles = array(val, float)
        self._reinit()

    def doWriteOrient1(self, val):
        self._orient1 = array(val, float)
        self._reinit()

    def doWriteOrient2(self, val):
        self._orient2 = array(val, float)
        self._reinit()

    def doWritePsi0(self, val):
        self._psi0 = val
        self._reinit()

    def doWriteCoordinatesystem(self, val):
        if val not in [1, -1, 2, -2]:
            raise ConfigurationError('valid values for coordinatesystem: '
                                     '+/-1 and +/-2')

    def lattice_real(self):
        return [self._lattice, self._angles]

    def lattice_rec(self):
        try:
            astar = zeros(3)
            alphastar = zeros(3)
            V = self.cal_volume_real()

            co = cos(self._angles * D2R)
            si = sin(self._angles * D2R)

            astar[0] = self._lattice[1] * self._lattice[2] * si[0] / V
            astar[1] = self._lattice[2] * self._lattice[0] * si[1] / V
            astar[2] = self._lattice[0] * self._lattice[1] * si[2] / V
            alphastar[0] = arccos((co[1] * co[2] - co[0])/(si[1] * si[2]))
            alphastar[1] = arccos((co[0] * co[2] - co[1])/(si[0] * si[2]))
            alphastar[2] = arccos((co[0] * co[1] - co[2])/(si[0] * si[1]))
            return [astar, alphastar]
        except Exception, err:
            raise ComputationError('%s when calculating reciprocal '
                                   'lattice' % err)

    def cal_volume_real(self):
        try:
            co = cos(self._angles * D2R)
            mul = self._lattice[0] * self._lattice[1] * self._lattice[2]
            V = mul * sqrt(1 - dot(co, co) + 2*co[0]*co[1]*co[2])
            return V
        except ComputationError, err:
            raise
        except Exception, err:
            raise ComputationError('%s when calculating real space cell '
                                   'volume' % err)

    def cal_volume_rec(self):
        try:
            return 1 / self.cal_volume_real()
        except ComputationError, err:
            raise
        except Exception, err:
            raise ComputationError('%s when calculating reciprocal space cell '
                                   'volume' % err)

    def cal_zone(self):
        return cross(self._orient1, self._orient2)

    def scat_plane(self):
        return (self._orient1, self._orient2)

    def cal_dvalue_real(self, Qhkl):
        try:
            hkl = array(Qhkl, float)
            mul = self._lattice_rec * hkl  # elementwise multiplication
            co = cos(self._angles_rec)
            sqresult = dot(mul, mul) + \
                       2 * mul[0] * mul[1] * co[2] + \
                       2 * mul[0] * mul[2] * co[1] + \
                       2 * mul[1] * mul[2] * co[0]
            return sqrt(sqresult)
        except ComputationError, err:
            raise
        except Exception, err:
            raise ComputationError('%s when calculating d value in '
                                   'real space' % err)

    def cal_dvalue_rec(self, Qhkl):
        try:
            return 1 / self.cal_dvalue_real(Qhkl)
        except ComputationError, err:
            raise
        except Exception, err:
            raise ComputationError('%s when calculating d value in '
                                   'reciprocal space' % err)

    def matrix_crystal2lab(self):
        try:
            B = zeros((3, 3))
            U = zeros((3, 3))

            B[0,0] = self._lattice_rec[0] * 2 * pi
            B[0,1] = self._lattice_rec[1] * cos(self._angles_rec[2]) * 2 * pi
            B[0,2] = self._lattice_rec[2] * cos(self._angles_rec[1]) * 2 * pi
            B[1,0] = 0
            B[1,1] = self._lattice_rec[1] * sin(self._angles_rec[2]) * 2 * pi
            B[1,2] = - self._lattice_rec[2] * sin(self._angles_rec[1]) * \
                     cos(self._angles[0] * D2R) * 2 * pi
            B[2,0] = 0
            B[2,1] = 0
            B[2,2] = 2 * pi / self._lattice[2]

            for i in range(3):
                for j in range(3):
                    if -0.000001 < B[i,j] < 0.000001:
                        B[i,j] = 0.0

            vec1 = dot(B, self._orient1)
            vec2 = dot(B, self._orient2)
            vec3 = cross(vec1, vec2)
            vec2 = cross(vec3, vec1)

            # XXX use self.coordinatesystem instead of hardcoded 1?
            U = self.cal_Umatrix(vec1, vec2, vec3, 1)
            return dot(U, B)
        except ComputationError, err:
            raise
        except Exception, err:
            raise ComputationError('%s when calculating UB matrix' % err)

    def cal_Umatrix(self, vec1, vec2, vec3, direction):
        try:
            U = zeros((3, 3))
            U[2] = vec3 / norm(vec3)

            if direction == 1:
                U[0] = vec1 / norm(vec1)
                U[1] = vec2 / norm(vec2)
            elif direction == 2:
                U[0] = vec2 / norm(vec2)
                U[1] = vec1 / norm(vec1)
            elif direction == -1:
                U[0] = - vec1 / norm(vec1)
                U[1] = vec2 / norm(vec2)
            elif direction == -2:
                U[0] = - vec2 / norm(vec2)
                U[1] = vec1 / norm(vec1)
            return U
        except ComputationError, err:
            raise
        except Exception, err:
            raise ComputationError('%s when calculating U matrix' % err)

    def hkl2Qcart(self, h, k, l):
        """Return the cartesian coordinates of given (h,k,l) Miller indices."""
        return dot(self._matrix, array([h, k, l], float))

    def hkl2Qlab(self, h, k, l):
        """Transform a vector given in real lattice with (h,k,l) Miller indices
        in Qlab with coordinates in system:
        x in beam direction, z direction upwards, y making a right handed system.
        """
        hklcart = self.hkl2Qcart(h, k, l)
        result = dot(hklcart, self._matrix_cardan)
        if abs(result[2]) > 0.001:
            raise ComputationError('out of plane vector; check your scattering plane')
        return result

    def Qlab2hkl(self, Qlab):
        """Calculate the retransformation of a vector given in Qlab to
        crystal lattice with (h,k,l) Miller indices.
        """
        try:
            matcardan_inv = inv(self._matrix_cardan)
            mat_inv = inv(self._matrix)
            result = dot(Qlab, matcardan_inv)
            hkl = dot(mat_inv, result)
            return hkl
        except ComputationError, err:
            raise
        except Exception, err:
            raise ComputationError('%s when transforming Qlab -> hkl' % err)

    def angle2Qcart(self, angles):
        """Calculate Q cartesian from instrument [ki, kf, phi, psi]."""
        try:
            ki, kf, phi, psi = angles
            psi *= D2R
            psi += self._psi0 * D2R
            phi *= D2R
            if self.axiscoupling:
                psi += phi

            Qcart = zeros(3)
            Qcart[0] = ki * cos(psi) - kf * cos(phi - psi)
            Qcart[1] = ki * sin(psi) + kf * sin(phi - psi)

            return Qcart
        except ComputationError, err:
            raise
        except Exception, err:
            raise ComputationError('%s when transforming angles -> Q cartesian'
                                   % err)

    def angle2hkl(self, angles):
        """Calculate hkl Miller indices from instrument [ki, kf, phi, psi]."""
        mat_inv = inv(self._matrix)
        return dot(mat_inv, self.angle2Qcart(angles))

    def angle2Qlab(self, angles):
        """Calculate Qlab from instrument [ki, kf, phi, psi]."""
        result = dot(self.angle2Qcart(angles), self._matrix_cardan)
        if abs(result[2]) > 0.001:
            raise ComputationError('out of plane vector; check your scattering plane')
        return result

    def cal_Y(self, r1, r2, hkl):
        """Calculate angle between 1st orientation reflection and Q vector."""
        # XXX doesn't use r1 or r2!
        try:
            crit = 0.000001
            hkl = self.hkl2Qlab(hkl[0], hkl[1], hkl[2])
            qs = hkl[0]**2 + hkl[1]**2
            qabs = sqrt(qs)

            Y = hkl[1] / qabs
            a1 = arcsin(Y)

            if -crit < hkl[0] < crit:
                Y = pi/2
                if hkl[1] < crit:
                    Y = - Y
            elif hkl[0] < -crit:
                Y = - a1
                if hkl[1] > crit:
                    Y += pi
                else:
                    Y -= pi
            elif hkl[0] > crit:
                Y = a1

            Y *= R2D
            return Y
        except ComputationError, err:
            raise
        except Exception, err:
            raise ComputationError('%s when calculating angle (r1, Q)' % err)

    def _metric(self, a, alpha):
        m = zeros((3, 3))
        m[0,0] = a[0]**2
        m[0,1] = a[0] * a[1] * cos(alpha[2])
        m[0,2] = a[0] * a[2] * cos(alpha[1])
        m[1,0] = m[0,1]
        m[1,1] = a[1]**2
        m[1,2] = a[1] * a[2] * cos(alpha[0])
        m[2,0] = m[0,2]
        m[2,1] = m[1,2]
        m[2,2] = a[2]**2
        return m

    def metric_tensor(self):
        """Return the metric tensor in real space for the lattice."""
        return self._metric(self._lattice, self._angles * D2R)

    def metric_tensor_rec(self):
        """Return the metric tensor in real space for the lattice."""
        return self._metric(self._lattice_rec, self._angles_rec)

    def cal_vec_angle(self, h1, k1, l1, h2, k2, l2):
        try:
            hkl1 = array([h1, k1, l1], float)
            hkl2 = array([h2, k2, l2], float)
            g = self.metric_tensor_rec()

            skalpro = 0.0
            for i in range(3):
                for j in range(3):
                    skalpro += hkl1[i] * hkl2[j] * g[i, j]

            hkl1_len = hkl2_len = 0
            for i in range(3):
                for j in range(3):
                    hkl1_len += hkl1[i] * hkl1[j] * g[i, j]
                    hkl2_len += hkl2[i] * hkl2[j] * g[i, j]
            hkl1_len = sqrt(hkl1_len)
            hkl2_len = sqrt(hkl2_len)

            a = skalpro / (hkl1_len * hkl2_len)
            try:
                an = arccos(a) * R2D
            except:
                if a < -1:
                    an = 180
                elif a > 1:
                    an = 0
            return an
        except ComputationError, err:
            raise
        except Exception, err:
            raise ComputationError('%s when calculating angle between vectors'
                                   % err)

    def cal_phi(self, q, ki, kf, s):
        """Return the sample scattering angle."""
        try:
            qabs = norm(q)
            temp = (ki**2 + kf**2 - qabs**2) / (2.0 * ki * kf)
            if -1 <= temp <= 1:
                phi = arctan2(sqrt(1 - temp**2), temp) * s * R2D
                return phi
            else:
                raise ComputationError('scattering triangle not closed when '
                                       'calculating phi angle')
        except ComputationError, err:
            raise
        except Exception, err:
            raise ComputationError('%s when calculating phi angle' % err)

    def cal_kf(self, ny, ki):
        """Calculate the outgoing wavevector for given energy transfer and
        incoming wavevector.
        """
        kf = ki**2 - K * ny
        if kf > 0.000001:
            kf = sqrt(kf)
            return kf
        else:
            # XXX convert to meV?
            raise ComputationError('energy transfer of %s THz not possible '
                                   'with k_i = %s' % (ny, ki))

    def cal_ki1(self, ny, kf):
        """Calculate the incoming wavevector for given energy transfer and
        outgoing wavevector.
        """
        ki = kf**2 + K * ny
        if ki > 0.000001:
            ki = sqrt(ki)
            return ki
        else:
            # XXX convert to meV?
            raise ComputationError('energy transfer of %s THz not possible '
                                   'with k_f = %s' % (ny, kf))

    def cal_ki2(self, Qlab, ny, phi):
        """Calculate the incoming wavevector for given Qlab vector, energy
        transfer and sample scattering angle.
        """
        try:
            ki = 0
            phi *= D2R
            Qabs = norm(Qlab)
            a1 = (Qabs / sin(phi)) ** 2
            a2 = K * ny
            a3 = a2 / sin(phi)
            a3 = a1**2 - a3**2
            if a3 > 0:
                ki = a1 + a2 + cos(phi) * sqrt(a3)
                ki /= 2
            if ki > 0.000001:
                ki = sqrt(ki)
                return ki
            else:
                # XXX convert to meV?
                raise ComputationError('energy transfer of %s THz not possible '
                                       'with phi = %s' % (ny, phi))
        except ComputationError, err:
            raise
        except Exception, err:
            raise ComputationError('%s when calculating k_i' % err)

    def cal_ki3(self, Qlab, ny, alpha):
        """Calculate the incoming wavevector for given Qlab vector, energy
        transfer and angle alpha(ki, Q).
        """
        try:
            alpha *= D2R
            Qabs = norm(Qlab)
            ki = (Qabs**2 + K * ny) / (2.0 * Qabs * cos(alpha))
            if ki > 0.000001:
                ki = sqrt(ki)
                return ki
            else:
                # XXX convert to meV?
                raise ComputationError('energy transfer of %s THz not possible;'
                                       ' scattering triangle not closed' % ny)
        except ComputationError, err:
            raise
        except Exception, err:
            raise ComputationError('%s when calculating k_i' % err)

    def cal_psi(self, y, alpha):
        """Calculate the rotation angle sample for given angle Y (ki, r1) and
        angle alpha (ki, Q).
        """
        psi = y - alpha
        if psi < -180:
            psi += 360
        if psi > 180:
            psi -= 360
        return psi

    def cal_alpha1(self, Qlab, ny, ki, s):
        """Calculate the angle alpha (ki, Q) for given Qlab vector, energy
        transfer, incoming wavevector and scattering sense (sample).
        """
        try:
            Qabs = norm(Qlab)
            temp = (Qabs**2 + K * ny) / (2 * Qabs * ki)
            if -1 <= temp < 1:
                alpha = arctan2(sqrt(1 - temp**2), temp) * s * R2D
                return alpha
            else:
                # XXX convert to meV?
                raise ComputationError('energy transfer of %s THz not possible;'
                                       ' scattering triangle not closed' % ny)
        except ComputationError, err:
            raise
        except Exception, err:
            raise ComputationError('%s when calculating alpha' % err)

    def cal_alpha2(self, y, psi):
        """Calculate the angle alpha (ki, Q) for given angle Y (ki, r1)
        and rotation angle (sample).
        """
        alpha = y - psi
        if alpha < -180:
            alpha += 360
        elif alpha > 180:
            alpha -= 360
        return alpha

    def cal_ny(self, ki, kf):
        """Calculate the energy transfer for given incoming and outgoing
        wavevectors.
        """
        return (ki**2 - kf**2) / K

    def cal_theta(self, Ei_f, Qhkl, s):
        """Calculate theta for given incoming and outgoing wavevector, hkl and
        scattering sense.
        """
        d = self.cal_dvalue_rec(Qhkl)
        temp = pi / d / Ei_f
        if temp < 1:
            theta = arcsin(temp) * s * R2D
            return theta
        else:
            raise ComputationError("arcsin > 1 when calculating theta")

    def cal_angles(self, Qhkl, ny, SM, SC, s):
        """
        Calculate instrument angles for given HKL and energy transfer, for
        a specific scan mode, scan constant and scattering sense.

        Scanmodes:

            'CKI': constant Ki -> incoming energy
            'CKF': constant Kf -> outgoing energy
            'CPSI': constant PSI -> angle between ki and orientation
                    reflection r1; psi in 0 ... 180; -180 ... 0
            'CPHI': constant PHI -> scattering angle of sample
            'DIFF': powder sample

            unimplemented:
             6: constant Ki, absolut Q
             7: constant Kf, absolut Q
             8: without analyser

        psi0:  angle between orientation reflection r1 and zero of sample rotation axis
        Y:     angle between orientation refection r1, Q
        alpha: angle between ki and Q
        """
        try:
            Qlab = self.hkl2Qlab(Qhkl[0], Qhkl[1], Qhkl[2])
            Y = self.cal_Y(self._orient1, self._orient2, Qhkl)

            if SM in ['CKI', 'DIFF']:
                ki = SC
                kf = self.cal_kf(ny, ki)
                phi = self.cal_phi(Qlab, ki, kf, s)
                alpha = self.cal_alpha1(Qlab, ny, ki, s)
                psi = self.cal_psi(Y, alpha)

            elif SM == 'CKF':
                kf = SC
                ki = self.cal_ki1(ny, kf)
                phi = self.cal_phi(Qlab, ki, kf, s)
                alpha = self.cal_alpha1(Qlab, ny, ki, s)
                psi = self.cal_psi(Y, alpha)

            elif SM == 'CPSI':
                psi = SC
                alpha = self.cal_alpha2(Y, psi)
                ki = self.cal_ki3(Qlab, ny, alpha)
                if alpha > 0:
                    sphi = 1
                else:
                    sphi = -1
                kf = self.cal_kf(ny, ki)
                phi = self.cal_phi(Qlab, ki, kf, sphi)

            elif SM == 'CPHI':
                phi = SC
                sphi = sign(phi)
                ki = self.cal_ki2(Qlab, ny, phi)
                kf = self.cal_kf(ny, ki)
                alpha = self.cal_alpha1(Qlab, ny, ki, sphi)
                psi = self.cal_psi(Y, alpha)

            psi -= self._psi0
            if self.axiscoupling:
                psi -= phi
                if psi < -180:
                    psi += 360
                if psi > 180:
                    psi -= 360
            if self.psi360:
                if psi < 0:
                    psi += 360
                # XXX can that happen?
                elif psi > 360:
                    psi -= 360

            return [ki, kf, phi, psi, alpha]
        except ComputationError, err:
            raise
        except Exception, err:
            raise ComputationError('%s when calculating angles for hkl' % err)

    def _test(self):
        def TQscan(Qh, Qk, Ql, ny, dQh, dQk, dQl, dny, numsteps, SM, SC, sense):
            Qhkl = array([Qh, Qk, Ql], float)
            dQhkl = array([dQh, dQk, dQl], float)
            print '  ' + ('%-9s' * 13) % (
                'h', 'k', 'l', 'ny', 'ki', 'kf', 'phi', 'psi',
                'hcalc', 'kcalc', 'lcalc', 'nycalc', 'dval')
            for i in range(numsteps):
                Qhkl += dQhkl
                ny += dny
                angles = self.cal_angles(Qhkl, ny, SM, SC, sense)
                hklr = self.angle2hkl(angles)
                nyr = self.cal_ny(angles[0], angles[1])
                dval = self.cal_dvalue_real(Qhkl)
                print ('%7.3f  ' * 13) % (tuple(Qhkl) + (ny,) + tuple(angles) +
                                          tuple(hklr) + (nyr, dval))

        self.lattice = [3.8184, 3.8184, 3.8184]
        self.angles = [90, 90, 90]
        self.orient1 = [1, 1, 0]
        self.orient2 = [-1, 1, 0]
        self.psi0 = -0.0
        s = 1
        print '## CKI'
        TQscan(1,   1, 0, 1,  0.005, 0.005, 0, 0,   21, 'CKI',  2.662, s)
        print '## CKF'
        TQscan(1,   1, 0, 1,  0.005, 0.005, 0, 0,   21, 'CKF',  2.662, s)
        print '## CPHI'
        TQscan(1.5, 1, 0, 5,  0,     0,     0, 0.1, 21, 'CPHI', 30,    s)
