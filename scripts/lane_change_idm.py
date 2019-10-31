#!/usr/bin/env python

from __future__ import print_function
from __future__ import division

from math import sqrt
from math import tanh
import numpy as np
import matplotlib.pyplot as plt

from intelligent_driver_model import adaptive_cruise_control as idm

# Data for a vehicle.
vehicle_dtype = np.dtype([
    ('x',       'float'),
    ('y',       'float'),
    ('theta',   'float'),
    ('speed',   'float'),
    ('accel',   'float'),
    ('policy',  'float'),
    ('length',  'float')])

# Data for a waypoint on the path.
waypoint_dtype = np.dtype([
    ('s',     'float'),
    ('x',     'float'),
    ('y',     'float'),
    ('theta', 'float'),
    ('kappa', 'float')])

def interpolate_path(path, distance):

    if distance<path[0]['s'] or distance>path[-1]['s']:
        raise ValueError('Invalid input distance:{}, path start:{} path end:{}'.format(
                         distance, path[0]['s'], path[-1]['s']))

    if distance==path[0]['s']: return path[0]
    if distance==path[-1]['s']: return path[-1]

    # Find the left and right precomputed waypoints,
    # which will be used in the interpolation.
    ridx = np.argmax(path['s']>distance)
    lidx = ridx - 1;

    # Weights for the left and right waypoints.
    lw =  (path[ridx]['s']-distance) / (path[ridx]['s']-path[lidx]['s'])
    rw = -(path[lidx]['s']-distance) / (path[ridx]['s']-path[lidx]['s'])

    # Compute the target waypoint.
    # FIXME: Is there a easier way to do this?
    target_waypoint = np.zeros(1, dtype=waypoint_dtype)
    target_waypoint[0] = path[lidx]['s']*lw + path[ridx]['s']*rw,\
                         path[lidx]['x']*lw + path[ridx]['x']*rw,\
                         path[lidx]['y']*lw + path[ridx]['y']*rw,\
                         path[lidx]['theta']*lw + path[ridx]['theta']*rw,\
                         path[lidx]['kappa']*lw + path[ridx]['kappa']*rw

    return target_waypoint[0]

def check_collision(snapshot):
    # Initial traffic setup.
    # --v3---------------------------------v2---------
    # --------ego-------------v1----------------------

    # Check ego and v1.
    if snapshot[1]['x']-snapshot[0]['x'] <= \
       (snapshot[1]['length']+snapshot[0]['length'])/2.0 : return True;

    # Check ego and v2.
    if snapshot[2]['x']-snapshot[0]['x'] <= \
       (snapshot[2]['length']+snapshot[0]['length'])/2.0 : return True;

    # Check v3 and v2.
    if snapshot[2]['x']-snapshot[3]['x'] <= \
       (snapshot[2]['length']+snapshot[3]['length'])/2.0 : return True;

    return False

def vehicle_accels1(snapshot, ego_path, ego_distance_on_path):
    # Initial traffic setup.
    # --v3---------------------------------v2---------
    # --------ego-------------v1----------------------

    accels = np.zeros(4)

    # Acceleration for v1.
    accels[1] = idm(snapshot[1]['speed'], snapshot[1]['policy'])
    # Acceleration for v2.
    accels[2] = idm(snapshot[2]['speed'], snapshot[2]['policy'])

    if snapshot[0]['y'] > 3.7/2.0:
        # The ego is on the target lane.
        # Acceleration for v3.
        accels[3] = idm(snapshot[3]['speed'], snapshot[3]['policy'],
                        snapshot[0]['speed'], snapshot[0]['x']-snapshot[3]['x'])
        # Acceleration for the ego.
        accels[0] = idm(snapshot[0]['speed'], snapshot[0]['policy'],
                        snapshot[2]['speed'], snapshot[2]['x']-snapshot[0]['x'])
    else:
        # The ego is still on the current lane.
        # Acceleration for v3.
        accels[3] = idm(snapshot[3]['speed'], snapshot[3]['policy'],
                        snapshot[2]['speed'], snapshot[2]['x']-snapshot[3]['x'])
        # Acceleration for the ego.
        accels[0] = idm(snapshot[0]['speed'], snapshot[0]['policy'],
                        snapshot[1]['speed'], snapshot[1]['x']-snapshot[0]['x'])

    return accels

def vehicle_accels2(snapshot, ego_path, ego_distance_on_path):
    # Initial traffic setup.
    # --v3---------------------------------v2---------
    # --------ego-------------v1----------------------

    accels = np.zeros(4)

    # Acceleration for v1.
    accels[1] = idm(snapshot[1]['speed'], snapshot[1]['policy'])
    # Acceleration for v2.
    accels[2] = idm(snapshot[2]['speed'], snapshot[2]['policy'])

    # Compute the acceleration for v3 depending whether the lead
    # is the ego or v2.
    accel3_from_ego = idm(snapshot[3]['speed'], snapshot[3]['policy'],
                          snapshot[0]['speed'], snapshot[0]['x']-snapshot[3]['x'])
    accel3_from_v2  = idm(snapshot[3]['speed'], snapshot[3]['policy'],
                          snapshot[2]['speed'], snapshot[2]['x']-snapshot[3]['x'])

    # Acceleration for v3, which is set depending on whether the ego
    # is on the target lane or not.
    if snapshot[0]['y'] > 3.7/2.0:
        accels[3] = accel3_from_ego
    else:
        accels[3] = accel3_from_v2

    # Acceleration for the ego.
    # There are three sources of accelerations for the ego.
    # 1. From the lead on the same lane.
    # 2. From the lead on the target lane.
    # 3. From the follower on the target lane.
    accele_from_v1 = idm(snapshot[0]['speed'], snapshot[0]['policy'],
                         snapshot[1]['speed'], snapshot[1]['x']-snapshot[0]['x'])
    accele_from_v2 = idm(snapshot[0]['speed'], snapshot[0]['policy'],
                         snapshot[2]['speed'], snapshot[2]['x']-snapshot[0]['x'])
    accele_from_v3 = accel3_from_ego - accel3_from_v2

    r = ego_distance_on_path / ego_path[-1]['s']
    w1 = (1-r)   / (1+r-r*r)
    w3 = r*(1-r) / (1+r-r*r)
    w2 = r       / (1+r-r*r)
    accels[0] = w1*accele_from_v1 + w2*accele_from_v2 + w3*accele_from_v3

    print(w1, w2, w3)

    return accels

def simulate_traffic(initial_snapshot, ego_path, controller):
    # The ego starts from the beginning of the path.
    ego_distance_on_path = 0.0
    # Resolution of the time in the simulation.
    time_res = 0.05

    # Stores the snapshot at each time instance.
    snapshots = []
    snapshot = initial_snapshot

    for t in np.arange(0.0, 20.0, time_res):
        accels = controller(snapshot, ego_path, ego_distance_on_path)
        snapshot['accel'] = accels
        snapshots.append((t, np.copy(snapshot)))

        # Update the position and speed of all agents.
        for i in range(1, 3):
            snapshot[i]['x'] = snapshot[i]['x'] +\
                               snapshot[i]['speed']*time_res +\
                               snapshot[i]['accel']*time_res*time_res*0.5
            snapshot[i]['speed'] = snapshot[i]['speed'] +\
                                   snapshot[i]['accel']*time_res

        # Update the state and speed of the ego.
        # It's a bit tricky since the ego is following the lane changing path.
        ego_distance_on_path = ego_distance_on_path +\
                               snapshot[0]['speed']*time_res +\
                               snapshot[0]['accel']*time_res*time_res*0.5

        # If the ego has reached or exceeded the end of the path, stop the simulation.
        if ego_distance_on_path >= ego_path[-1]['s']: break

        ego_waypoint = interpolate_path(ego_path, ego_distance_on_path)
        snapshot[0]['x'] = ego_waypoint['x']
        snapshot[0]['y'] = ego_waypoint['y']
        snapshot[0]['theta'] = ego_waypoint['theta']
        snapshot[0]['speed'] = snapshot[0]['speed'] + snapshot[0]['accel']*time_res

        if check_collision(snapshot):
            print('Collision snapshot: \n', snapshot)
            raise RuntimeError('Collision detected during the simulation.')

    return snapshots

def parse_snapshots(snapshots):
    t   = np.zeros(len(snapshots))
    ego = np.zeros(len(snapshots), dtype=vehicle_dtype)
    v1  = np.zeros(len(snapshots), dtype=vehicle_dtype)
    v2  = np.zeros(len(snapshots), dtype=vehicle_dtype)
    v3  = np.zeros(len(snapshots), dtype=vehicle_dtype)

    for i in range(0, len(snapshots)):
        t[i]   = snapshots[i][0]
        ego[i] = snapshots[i][1][0]
        v1[i]  = snapshots[i][1][1]
        v2[i]  = snapshots[i][1][2]
        v3[i]  = snapshots[i][1][3]

    return t, ego, v1, v2, v3

def draw(snapshots1, snapshots2):

    s1_t, s1_ego, s1_v1, s1_v2, s1_v3 = parse_snapshots(snapshots1)
    s2_t, s2_ego, s2_v1, s2_v2, s2_v3 = parse_snapshots(snapshots2)

    # Plot ego acceleration.
    fige_accel, axe_accel = plt.subplots()
    axe_accel.plot(s1_t, s1_ego['accel'], label='naive-IDM')
    axe_accel.plot(s2_t, s2_ego['accel'], label='LC-IDM')
    axe_accel.set_xlabel('t(s)')
    axe_accel.set_ylabel('a(m/s/s)')
    axe_accel.set_title('Ego Acceleration')
    axe_accel.legend()
    axe_accel.grid()

    # Plot the ego following distance.

    # Plot v3 acceleration.
    fig3_accel, ax3_accel = plt.subplots()
    ax3_accel.plot(s1_t, s1_v3['accel'], label='naive-IDM')
    ax3_accel.plot(s2_t, s2_v3['accel'], label='LC-IDM')
    ax3_accel.set_xlabel('t(s)')
    ax3_accel.set_ylabel('a(m/s/s)')
    ax3_accel.set_title('Vehicle3 Acceleration')
    ax3_accel.legend()
    ax3_accel.grid()

    # Plot Ego following distance

    return

def main():

    # Load the lane chaning path of the ego vehicle.
    ego_path = np.loadtxt('left_lane_change_path', waypoint_dtype)

    # Initialize the micro-traffic.
    # The setup of the vehicles is the following:
    # --v3---------------------------------v2---------
    # --------ego-------------v1----------------------
    # +x: right; +y: up
    # v0: the ego vehicle
    # v1: lead on the current lane
    # v2: lead on the target lane
    # v3: follower on the target lane
    snapshot = np.array([
        (  0.0, 0.0, 0.0, 23.0, 0.0, 25.0, 4.7),
        ( 20.0, 0.0, 0.0, 20.0, 0.0, 20.0, 4.7),
        ( 40.0, 3.7, 0.0, 20.0, 0.0, 20.0, 4.7),
        (-15.0, 3.7, 0.0, 24.0, 0.0, 25.0, 4.7) ], dtype=vehicle_dtype)

    # Simulate the traffic.
    snapshots1 = simulate_traffic(np.copy(snapshot), ego_path, vehicle_accels1)
    snapshots2 = simulate_traffic(np.copy(snapshot), ego_path, vehicle_accels2)

    # Plots.
    draw(snapshots1, snapshots2)
    plt.show()


if __name__ == '__main__':
    main()