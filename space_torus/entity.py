class Entity(object):
    def __init__(self, id, location, rotation=(0, 0, 0), direction=(0, 0, 0), background=False):
        self.id = id
        self.location = location
        self.rotation = rotation
        self.direction = direction
        self.background = background

    def update(self):
        x, y, z = self.location
        dx, dy, dz = self.direction
        self.location = x + dx, y + dy, z + dz


class Asteroid(Entity):
    def __init__(self, *args, **kwargs):
        super(Asteroid, self).__init__(*args, **kwargs)

    def update(self):
        super(Asteroid, self).update()
        rx, ry, rz = self.rotation
        # Increment all axis to 'spin' 
        self.rotation = rx + 1, ry + 1, rz + 1


class Planet(Entity):
    def __init__(self, *args, **kwargs):
        self.delta = kwargs.pop('delta', 5)
        self.atmosphere = kwargs.pop('atmosphere', 0)
        self.cloudmap = kwargs.pop('cloudmap', 0)
        super(Planet, self).__init__(*args, **kwargs)

    def update(self):
        super(Planet, self).update()
        pitch, yaw, roll = self.rotation
        roll += self.delta / 100.0
        self.rotation = pitch, yaw, roll