#!/usr/bin/env python3
'''
Soaring Module
Ryan Friedman

This module displays the estimated soaring thermals on the map.
A circle is drawn with the estimated radius from ArduSoar's estimated thermal location.
'''

from MAVProxy.modules.lib import mp_module, mp_util

class soar(mp_module.MPModule):
    def __init__(self, mpstate):
        """Initialise module"""
        super(soar, self).__init__(mpstate, "soar", "")

        _x = None
        _y = None
        _radius = None
        _strength = None

    def mavlink_packet(self, m):
        '''handle mavlink packets'''

        if m.get_type() == 'NAMED_VALUE_FLOAT' and m.name.startswith("SOAR"):
            if m.name == "SOAREKFX0":
                self._strength = m.value
            elif m.name == "SOAREKFX1":
                self._radius = m.value
            elif m.name == "SOAREKFX2":
                self._x = m.value
            elif m.name == "SOAREKFX3":
                self._y = m.value
            elif m.name == "SOARECX":
                pass
            elif m.name == "SOARECY":
                pass
            else:
                raise NotImplementedError(m.name)
            
            self.draw_thermal_estimate()


    def draw_thermal_estimate(self):

        if self._radius is None:
            print("No radius")
            return
        if self._x is None:
            print("No x")
            return
        if self._y is None:
            print("No y")
            return
        
        home = self.module('wp').get_home()
        if home is None:
            print("No home")
            return
        home_lat = home.x
        home_lng = home.y
        
        (thermal_lat, thermal_lon) = mp_util.gps_offset(home_lat, home_lng, self._y, self._x)
        print("THERMAL @ ", thermal_lat, thermal_lon, "r=", self._radius)
        
        # TODO check map is loaded.
        from MAVProxy.modules.mavproxy_map import mp_slipmap
        slipcircle = mp_slipmap.SlipCircle(
            "soar-thermal", # key
            "thermals", # layer
            (thermal_lat, thermal_lon), # latlon
            self._radius, # radius
            (0, 255, 255),
            linewidth=2)
        for mp in self.module_matching('map*'):
            # remove the threat from the map
            mp.map.add_object(slipcircle)

def init(mpstate):
    '''initialise module'''
    return soar(mpstate)
