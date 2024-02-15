from time import sleep
import krpc

from display import Display

from PyVecs import Vector2, Vector3

class Ray:
    def __init__(self, x, y) -> None:
        self.direction = Vector3(-focal_length, x, y).normalize()
        self.distance = float('inf')
        self.pos = Vector3(x, y, self.distance) # direction nao esta no mesmo referencial

    def update(self):
        self.distance = space_center.raycast_distance((0, 0, 0), tuple(self.direction), lidar_ref)

        self.pos.z = -self.direction.x * self.distance


conn = krpc.connect(name='Hover')
drawing = conn.drawing
space_center = conn.space_center
vessel = space_center.active_vessel
body = vessel.orbit.body
a_gravity = body.surface_gravity

body_ref = body.reference_frame
surface_ref = vessel.surface_reference_frame
hybrid_ref = space_center.ReferenceFrame.create_hybrid(
    position=body_ref,
    rotation=surface_ref
)

flight_body = vessel.flight(body_ref)
flight_hybrid = vessel.flight(hybrid_ref)

stream_mean_altitude = conn.add_stream(getattr, flight_body, "mean_altitude")
stream_vel = conn.add_stream(getattr, flight_hybrid, "velocity")
stream_mass = conn.add_stream(getattr, vessel, "mass")
stream_av_thrust = conn.add_stream(getattr, vessel, "available_thrust")

# PARAMS
matrix_size = [30, 30]
focal_length = 1
alt_target = stream_mean_altitude()


# Lidar
lidar_ref =space_center.ReferenceFrame.create_hybrid(
    position=space_center.ReferenceFrame.create_relative(reference_frame=vessel.reference_frame, position=(0, vessel.bounding_box(vessel.reference_frame)[0][1] - 1, 0)),
    rotation=surface_ref
)

'''
lidar_ref = space_center.ReferenceFrame.create_relative(
    reference_frame=surface_ref,
    position=(-5, 0, 0)
)
'''

display = Display()
display.start()

points = []

for j in range(matrix_size[1]):
    row = []
    y = j / (matrix_size[1] - 1) - 0.5
    for i in range(matrix_size[0]):
        x = i / (matrix_size[0] - 1) - 0.5
        ray = Ray(x, y)
        #drawing.add_line((0, 0, 0), tuple(ray.direction * 500), lidar_ref)
        row.append(ray)
    points.append(row)

try:
    while True:
        sleep(0.05)

        display_points = []
        for row in points:
            line = []
            for ray in row:
                ray.update()

                line.append(ray.pos)

            display_points.append(line)

        
        max_z = max([r.pos.z for l in points for r in l])

        for row in display_points:
            for point in row:
                point.z /= max_z

        display.update(display_points)




    
        # Throttle control
        alt = stream_mean_altitude()
        vel = Vector3(stream_vel())
        mass = stream_mass()
        av_thrust = stream_av_thrust()


        a_eng = av_thrust / mass

        delta_h = alt_target - alt

        v_target = delta_h - (a_eng - a_gravity) *.5

        delta_v = v_target - vel.x

        vessel.control.throttle = (delta_v*5 + a_gravity) / a_eng

except KeyboardInterrupt as e:
    display.end()
