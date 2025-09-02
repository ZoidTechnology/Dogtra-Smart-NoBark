# Dogtra Smart NoBark

The [Dogtra Smart NoBark](https://dogtra.com/products/dogtra-smart-nobark) is a Bluetooth-enabled anti-bark collar that communicates using Bluetooth Low Energy. The manufacturer provides companion apps for Android and iOS developed with the Flutter framework.

I am not a professional dog trainer. This project is intended only to monitor barking behaviour. I do not recommend using anti-bark collars for any purpose other than observation.

## Protocol

Bluetooth information, message formats, and data types are documented in [protocol.md](protocol.md). The protocol has been reverse-engineered from observations of the device and its companion apps, and may contain inaccuracies or omissions.

## Python Implementation

A simple Python program is provided that connects to a collar using a given MAC address. It requests and decodes the collar's current state, as well as incoming event messages. It will attempt to reconnect if the connection is lost.

### Requirements

- Python 3.10 or higher
- [Bleak](https://pypi.org/project/bleak/) 1.1 or higher

### Usage

    python main.py <mac address>
