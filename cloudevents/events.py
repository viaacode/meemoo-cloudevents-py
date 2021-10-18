# events.py


import datetime
import uuid
import json
from enum import Enum
from abc import ABC
from typing import Dict


class EventOutcome(str, Enum):
    """Enum: EventOutcome

    An EventOutcome can only be one of three values:
    - FAIL
    - WARNING
    - SUCCESS
    """
    FAIL = "fail"
    WARNING = "warning"
    SUCCESS = "success"
    
    def to_str(cls) -> str:
        return cls.value

    def to_dict(cls) -> dict:
        return {"outcome": cls.to_str()}

    def to_json(cls) -> str:
        return json.dumps(cls.to_dict())


class CEMessageMode(str, Enum):
    """Enum: CEMessageMode

    In CloudEvents, two message modes exist:
    - BINARY        : event-attributes are seperated from the payload
    - STRUCTURED    : event-attributes are included in the payload, the payload
                      itself is moved to the `data`-field.
    """
    BINARY = "binary"
    STRUCTURED = "structured"


class EventAttributes:
    """
    """
    id = ""
    source = ""
    specversion = "1.0"
    type = ""
    datacontenttype = ""
    subject = ""
    time = ""
    outcome = ""

    def __init__(self, id: str = str(uuid.uuid4().int), source: str = "", type: str = "",
                 datacontenttype: str = "application/json", subject: str = "",
                 outcome: EventOutcome = EventOutcome.SUCCESS,
                 correlation_id: str = ""):
        self.id = id
        self.source = source
        self.type = type
        self.datacontenttype = datacontenttype
        self.subject = subject
        self.outcome = outcome
        ## Event time: tz-aware datetime object (UTC)
        self.time = datetime.datetime.utcnow()
        self.correlation_id = correlation_id or self._new_correlation_id()

    def __repr__(self):
        return f"<{self.__class__.__name__}: id={self.id}, " + \
               f"type={self.type}, corr_id={self.correlation_id}>"

    def get_event_time_as_iso8601(self) -> str:
        return self.time.replace(tzinfo=datetime.timezone.utc).isoformat()

    # See: https://docs.python.org/3/library/time.html#time.time_ns (3.7+)
    def get_event_time_as_int(self) -> int:
        epoch = datetime.datetime.utcfromtimestamp(0)
        return round((self.time - epoch).total_seconds() * 1000.0)

    def _new_correlation_id(self):
        return str(uuid.uuid4()).replace("-", "")

    def to_dict(self, serializable: bool = False):
        """Return this object as dict. When `serializable=True` return all
        values as strings rather than objects."""
        if serializable:
            return {
                "id": self.id,
                "source": self.source,
                "specversion": self.specversion,
                "type": self.type,
                "datacontenttype": self.datacontenttype,
                "subject": self.subject,
                "time": self.get_event_time_as_iso8601(),
                "outcome": self.outcome.to_str(),
                "correlation_id": self.correlation_id
            }
        return vars(self)

    def to_json(self):
        return json.dumps(self.to_dict(serializable=True))


class Event:
    """Event

    Base CloudEvent Class
    """

    def __init__(self, attributes: EventAttributes, data: Dict[str, str]):
        # Py3.9: lowercase `dict[str, str]` will work
        # Data and context attributes
        self._data = data
        self._attributes = attributes

        # Required CE attributes
        self.specversion = attributes.specversion
        self.source = attributes.source
        # unique within the "source"
        self.id = attributes.id
        self.type = attributes.type

        # Optional CE-attributes (but required by meemoo)
        ## RFC2046 compliant media-type
        self.datacontenttype = attributes.datacontenttype
        ## Event time: tz-aware datetime object (UTC)
        self.time = attributes.time
        # Extension attributes (but required by meemoo)
        ## correlation_id
        self.correlation_id = attributes.correlation_id
        ## outcome: EventOutcome
        self.outcome = attributes.outcome
        # Extension attributes (optional)
        # https://github.com/cloudevents/spec/blob/v1.0/extensions/dataref.md
        # For now, we fill it in with `subject`
        # ~ self.dataref = attributes.subject

    def __repr__(self):
        return f"<{self.__class__.__name__}: id={self.id}, type={self.type}, " + \
               f"corr_id={self.correlation_id}>"

    def to_dict(self, serializable: bool = False):
        """Return this object as dict. When `serializable=True` return all
        values as strings rather than objects."""
        if serializable:
            attrs = self._attributes.to_dict(serializable=True)
        else:
            attrs = self._attributes.to_dict(serializable=False)
        return {**attrs, "data": self._data}
        
    def to_json(self) -> str:
        """Required by spec"""
        return json.dumps(self.to_dict(serializable=True))

    def get_data(self):
        assert self.outcome != ""
        # NOTE: this assumes 'structured' mode for now!
        return self._data["data"]

    def get_attributes(self):
        return self._attributes.to_dict()

    def get_event_time_as_iso8601(self) -> str:
        return self._attributes.get_event_time_as_iso8601()

    def get_event_time_as_int(self) -> int:
        return self._attributes.get_event_time_as_int()

    def has_successful_outcome(self) -> bool:
        return self.outcome == EventOutcome.SUCCESS


class Message:
    def __repr__(self):
        return f"{self.__class__.__name__}: id={self.attributes['id']}, " + \
               f"type={self.attributes['type']}, " + \
               f"corr_id={self.attributes['correlation_id']}"


class AMQPMessage(Message):
    """AMQPMessage

        data: bytes
        attributes: None or dict
    """
    # Standard class-attributes
    data = ""
    attributes = ""
    # AMQP-specific "properties"
    # content_type:
    #   - binary: "application/json; charset=utf-8"
    #   - structured: "application/cloudevents+json; charset=utf-8"
    content_type = "application/json; charset=utf-8"
    correlation_id = ""
    id = ""


class PulsarMessage(Message):
    """PulsarMessage

        data: bytes
        attributes: None or dict
    """
    data = ""
    attributes = ""


class ProtocolBinding(ABC):
    """Generic Abstract Protocol Binding class.

    A protocol is transport mechanism. A protocol binding specifies
    (implements) how Events are transformed into Messages and vice versa.
    A different protocol binding exists for every supported protocol, eg.,
    Pulsar, AMPQ, ...
    """

    @staticmethod
    def to_protocol(event: Event, mode: CEMessageMode = CEMessageMode.BINARY):
        NotImplementedError("Class %s doesn't implement aMethod()" % (self.__class__.__name__))

    @staticmethod
    def from_protocol(msg) -> Event:
        NotImplementedError("Class %s doesn't implement aMethod()" % (self.__class__.__name__))

    @staticmethod
    def generate_attributes(event: Event) -> dict:
        # Generate binding-specific attribute-names, eg.: CE-EventTime,
        # CE-CloudEventsVersion, ...
        NotImplementedError("Class %s doesn't implement aMethod()" % (self.__class__.__name__))


class AMQPBinding(ProtocolBinding):
    """AMQP Protocol Binding
    
    See: https://github.com/cloudevents/spec/blob/v1.0.1/amqp-protocol-binding.md"""

    @staticmethod
    def to_protocol(event: Event, mode: CEMessageMode = CEMessageMode.BINARY) -> AMQPMessage:
        # Regardless of message mode, for now we always provide the AMQP
        # Properties (attributes) as well.
        AMQPMessage.attributes = event._attributes.to_dict(serializable=True)
        AMQPMessage.correlation_id = event.correlation_id
        AMQPMessage.id = event.id
        # We could also use the CEMessageMode-enum?
        if mode == "binary":
            data = event.get_data()
            AMQPMessage.data = json.dumps(data).encode("utf-8")
            AMQPMessage.content_type = "application/json; charset=utf-8"
        elif mode == "structured":
            # data: bytes
            AMQPMessage.data = event.to_json().encode("utf-8")
            AMQPMessage.content_type = "application/cloudevents+json; charset=UTF-8"
            # AMQP properties: None or dict
        else:
            # TODO!
            print("Unknown mode")
        return AMQPMessage

    @staticmethod
    def from_protocol(properties, body) -> Event:
        content_type, charset = properties.content_type.split(";")
        mode = CEMessageMode.BINARY if content_type == "application/json" \
               else CEMessageMode.STRUCTURED
        headers = properties.headers
        # For now, we assume properties/headers to always be present as headers
        # regardless of messaging mode.
        attributes = EventAttributes(type=headers["type"],
                                     source=headers["source"],
                                     subject=headers["subject"],
                                     outcome=EventOutcome(headers["outcome"]),
                                     correlation_id=headers["correlation_id"]
                                     )
        if mode == CEMessageMode.BINARY:
            data = json.loads(body.decode("utf-8"))
        elif mode == CEMessageMode.STRUCTURED:
            data = json.loads(body.decode("utf-8"))["data"]
        return Event(attributes, data)

    @staticmethod
    def generate_attributes(event: Event) -> dict:
        pass

    def _get_content_type(content_type_str: str):
        # TODO: call this fn
        content_type, charset = content_type_str.split(";")
        return content_type.trim()

class PulsarBinding(ProtocolBinding):
    """Pulsar Protocol Binding
    
    See: https://gist.github.com/sijie/082c59e66b9ed175c1bb48466f3629f0
    """

    @staticmethod
    def to_protocol(event: Event, mode: CEMessageMode = CEMessageMode.BINARY) -> PulsarMessage:
        # Regardless of message mode, for now we always provide the Pulsar
        # Properties (attributes) as well.
        PulsarMessage.attributes = event._attributes.to_dict(serializable=True)
        # We could also use the CEMessageMode-enum?
        if mode == "binary":
            data = event.get_data()
            PulsarMessage.data = json.dumps(data).encode("utf-8")
        elif mode == "structured":
            # data: bytes
            PulsarMessage.data = event.to_json().encode("utf-8")
            # Pulsar properties: None or dict
        else:
            # TODO!
            print("Unknown mode")
        return PulsarMessage

    @staticmethod
    def from_protocol(msg: PulsarMessage) -> Event:
        data = json.loads(msg.data().decode("utf-8"))
        attributes = EventAttributes(type=msg.properties()["type"],
                                     source=msg.properties()["source"],
                                     subject=msg.properties()["subject"],
                                     outcome=EventOutcome(msg.properties()["outcome"]),
                                     correlation_id=msg.properties()["correlation_id"]
                                     )
        return Event(attributes, data)
