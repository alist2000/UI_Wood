from abc import ABC, abstractmethod


class Support(ABC):

    @abstractmethod
    def middleSupport(self):
        pass

    def startEndSupport(self):
        pass


class BeamSupport:
    def __init__(self, Beams, Posts, ShearWalls):
        self.Beams = Beams
        self.Posts = Posts
        self.ShearWalls = ShearWalls

    def postSupport(self, beam):
        pass

    def shearWallSupport(self, beam):
        pass

    def beamSupport(self, beam):
        pass
