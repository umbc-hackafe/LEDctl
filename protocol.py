import struct
import abc

class InappropriateValueError(Exception): pass

class Message(object):
    # Should be changed when subclassed, sent over the wire to determine
    # interpretation of the Message.
    _id_ = None

    @abc.abstractmethod
    def serialize_internals(self):
        """Serializes the internal components of a Message as a bytes
        object. When sublassing Message, this needs to be
        overwritten."""
        pass

    def serialize(self):
        """Serializes the Message ID type, length, and internals. Calls
        self.serialize_internals() to do produce the body of the
        message."""
        internals = self.serialize_internals()
        
        return struct.pack("!BB", self._id_, len(internals)) + internals

class Light(object):
    def __init__(self, red, green, blue, intensity, id=None):
        for color in red, green, blue:
            if type(color) != int or color >= (1 << 4):
                raise InappropriateValueError("invalid color value: %s"
                        % color)

        if type(intensity) != int or intensity >= (1 << 8):
            raise InappropriateValueError("invalid intensity value: %s"
                    % intensity)

        if id != None and (type(id) != int or id >= (1 << 6)):
            raise InappropriateValueError("invalid id value: %s" % id)

        self.red = red
        self.green = green
        self.blue = blue
        self.intensity = intensity
        self.id = id

    def serialize_id(self):
        """Return a serialized version of the Light as a bytes
        object, which includes the Light's ID."""
        return struct.pack("!BBBBB", self.id, self.red, self.green,
                self.blue, self.intensity)

    def serialize_anonymous(self):
        """Return a serialized version of the Light as a bytes object,
        without the Light's ID number."""
        return struct.pack("!BBBB", self.red, self.green, self.blue,
                self.intensity)

class ModifyMessage(Message):
    class MissingLightIDError(Exception): pass

    _id_ = 1

    def __init__(self, oldlight, newlight, duration):
        if not hasattr(oldlight, "id") or oldlight.id == None:
            raise self.MissingLightIDError()

        if type(duration) != int or duration >= (1 << 16):
            raise InappropriateValueError("invalid duration %s" %
                    duration)

        self.oldlight = oldlight
        self.newlight = newlight
        self.duration = duration

    def serialize_internals(self):
        return self.oldlight.serialize_id() + \
                self.newlight.serialize_anonymous() + struct.pack("!h",
                        self.duration)
