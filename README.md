# Meemoo CloudEvents

Meemoo's implementation of [CloudEvents](https://github.com/cloudevents/spec).

## Status

Very much a work in progress. Currently only hosted on meemoo's internal
artefact repository. Contact the dev-team for more information.

Support for:

- CloudEvents v1.0 only,
- Python 3.8+ only.

Two protocol bindings are implemented:

- Pulsar
- AMQP

## Diagrams

<details>
  <summary>Class diagram (click to expand)</summary>

  ![meemoo-cloudevents-py](http://www.plantuml.com/plantuml/proxy?src=https://raw.githubusercontent.com/viaacode/meemoo-cloudevents-py/main/docs/event_protocol_message.puml&fmt=svg)

</details>

## Prerequisites

* Python 3.10+
* Access to the meemoo PyPI

## Installation

Package `meemoo-cloudevents` can be installed with pip:

```
$ pip install meemoo-cloudevents \
    --extra-index-url http://do-prd-mvn-01.do.viaa.be:8081/repository/pypi-all/simple \
    --trusted-host do-prd-mvn-01.do.viaa.be
```

## Usage

The CloudEvents' API in meemoo's implementation differs in a number of ways
from the [official SDK](https://github.com/cloudevents/sdk-python):

- event-attributes is a class instead of a dict,
- protocol bindings are implemented with a different API,
- some more attributes are required (not least, a correlation ID).

### Examples

For the examples using Pulsar, you need the Python Pulsar client:

```
$ pip install pulsar-client
```

#### Generating an event and sending it via Pulsar

```python
import pulsar
from cloudevents import Event, EventOutcome, EventAttributes, PulsarBinding, CEMessageMode

# Create a CloudEvent
# - The CloudEvent "id" is generated if omitted. "specversion" defaults to "1.0".
attributes = EventAttributes(type="be.meemoo.sample-event",
                             source="/meemoo/sample-app",
                             subject="sample-file",
                             outcome=EventOutcome.SUCCESS)
data = {"message": "Hello World!"}
event = Event(attributes, data)

print(event)

# Creates a Pulsar message of the CloudEvent in structured content mode
msg = PulsarBinding.to_protocol(event, CEMessageMode.STRUCTURED)

# Open a Pulsar-connection and send the message to a topic
client = pulsar.Client("pulsar://sample.pulsar.url:6650")
producer = client.create_producer("be.meemoo.sample-event", producer_name="sample-app")

msg_id = producer.send(msg.data, properties=msg.attributes,
                       event_timestamp=event.get_event_time_as_int())
# Close the client
client.close()
```

#### Receiving a message via Pulsar and turning it into an event


```python
import pulsar
from cloudevents import Event, EventOutcome, EventAttributes, PulsarBinding, CEMessageMode

# Open a Pulsar-connection and start consuming messages from a topic
client = pulsar.Client("pulsar://sample.pulsar.url:6650")
consumer = client.subscribe("be.meemoo.sample-event", subscription_name="sample-app")
incoming_msg = consumer.receive()

# We can now create a CloudEvent from the incoming message.
# Note, we don't need to explicitly specify the content mode as this is inferred
# from the messages Content-Type
event = PulsarBinding.from_protocol(incoming_msg)

print(event)
print(event.get_data())

# Close the client
client.close()
```

## Development and testing

1. Clone this repository and change into the new dir:

```bash
git clone git@github.com:viaacode/meemoo-cloudevents-py.git
cd meemoo-cloudevents-py`
```

2. Init and activate a virtual env:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install the library (editable) and the dev/test dependencies:

```bash
(.venv) python -m pip install .
(.venv) python -m pip install '.[dev]'
```

4. Run the tests

```bash
(.venv) python -m pytest
```
