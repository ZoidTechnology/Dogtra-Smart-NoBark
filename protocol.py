from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable


class MessageType(Enum):
    STATE = auto()
    HISTORY_REQUEST = auto()
    ACTIVE_TIME = auto()
    HISTORY_PAGE = auto()


class Instruction(Enum):
    SYNC = 0x01
    MODE = 0x02
    ALARM = 0x06
    BARK_COUNT_UPDATE = 0x07
    TRAINING = 0x0D
    RESYNC = 0x0E
    ENTER_FACTORY_MODE = 0xA0
    EXIT_FACTORY_MODE = 0xA1
    RESET_DEVICE_TIME = 0xB0
    UPDATE_SENSITIVITY = 0xB5
    BARK_COUNT_TEST = 0xBB
    ENTER_SENSITIVITY_ADJUSTMENT = 0xD0
    EXIT_SENSITIVITY_ADJUSTMENT = 0xD1


class Mode(Enum):
    LEVEL = 0x01
    PAGER = 0x02
    AUTO_INCREASE = 0x03
    BARK_COUNTER = 0x05


class AudioSensitivity(Enum):
    Level_1 = 0x06
    Level_2 = 0x0A
    Level_3 = 0x0E
    Level_4 = 0x12
    Level_5 = 0x16


class Alarm(Enum):
    ADJUST_COLLAR = 0x01
    INCREASE_STIMULATION = 0x02
    INCREASE_MAX_STIMULATION = 0x03
    TRY_STIMULATION_MODE = 0x04
    EXTENDED_WEAR_REMINDER_3_HOUR = 0x0A
    EXTENDED_WEAR_REMINDER_4_HOUR = 0x0B
    EXTENDED_WEAR_REMINDER_5_HOUR = 0x0C
    EXTENDED_WEAR_REMINDER_6_HOUR = 0x0D
    EXTENDED_WEAR_REMINDER_7_HOUR = 0x0E
    EXTENDED_WEAR_REMINDER_8_HOUR = 0x0F


@dataclass
class Field:
    name: str | None = None
    length: int = 1
    parser: Callable[[bytes], Any] = lambda value: int.from_bytes(value, byteorder="big")


@dataclass
class Detector:
    detect: Callable[[str, bytes], bool]
    type: MessageType
    fields: list[Field]


STATE_FIELDS = [
    Field("instruction", parser=lambda value: Instruction(value[0])),
    Field("mode", parser=lambda value: Mode(value[0])),
    Field("shock_level"),
    Field("auto_increase_level"),
    Field("auto_increase_minimum_level"),
    Field("auto_increase_maximum_level"),
    Field("battery_level"),
    Field("audio_sensitivity", parser=lambda value: AudioSensitivity(value[0])),
    Field("vibration_sensitivity"),
    Field("bark_count"),
    Field("howl_count"),
    Field("whine_count"),
    Field("bark_stimulate"),
    Field("howl_stimulate"),
    Field("whine_stimulate"),
    Field(
        "individual_settings",
        parser=lambda value: {
            "low_volume_detection": bool(value[0] & 0x10),
            "detect_whine": bool(value[0] & 0x20),
            "detect_howl": bool(value[0] & 0x40),
            "detect_bark": bool(value[0] & 0x80),
        },
    ),
    Field("hour"),
    Field("minute"),
    Field("second"),
    Field("alarm", parser=lambda value: Alarm(value[0]) if value[0] else None),
    Field("bark_total_count", 2),
    Field("howl_total_count", 2),
    Field("whine_total_count", 2),
]

ACTIVE_TIME_FIELDS = [Field(), Field("hour"), Field("minute"), Field("second")]

HISTORY_PAGE_FIELDS = [
    Field("page_count", 1),
    Field("page", 1),
    Field(
        "records",
        240,
        lambda value: [
            record
            for index in range(0, 240, 10)
            if (
                record := _parse(
                    value[index : index + 10],
                    [
                        Field("hour"),
                        Field("minute"),
                        Field("bark_count"),
                        Field("howl_count"),
                        Field("whine_count"),
                        Field("bark_stimulate"),
                        Field("howl_stimulate"),
                        Field("whine_stimulate"),
                        Field("shock_level"),
                        Field(
                            "mode",
                            parser=lambda value: Mode(value[0]) if value[0] else None,
                        ),
                    ],
                )
            )["mode"]
            is not None
        ],
    ),
]

DETECTORS = [
    Detector(
        lambda uuid, message: uuid == "2A59" and len(message) == 26,
        MessageType.STATE,
        STATE_FIELDS,
    ),
    Detector(
        lambda uuid, message: uuid == "2A5A" and len(message) == 1 and message[0] == 0xC1,
        MessageType.HISTORY_REQUEST,
        [],
    ),
    Detector(
        lambda uuid, message: uuid == "2A5A" and len(message) == 4 and message[0] == 0xC1,
        MessageType.ACTIVE_TIME,
        ACTIVE_TIME_FIELDS,
    ),
    Detector(
        lambda uuid, message: uuid == "2A5A" and len(message) == 242,
        MessageType.HISTORY_PAGE,
        HISTORY_PAGE_FIELDS,
    ),
]


def _parse(message: bytes, fields: list[Field]):
    parsed: dict[str, Any] = {}
    index = 0

    for field in fields:
        value = message[index : (index := index + field.length)]

        if field.name:
            parsed[field.name] = field.parser(value)

    return parsed


def parse(uuid: str, message: bytes):
    uuid = uuid[4:8].upper()

    for detector in DETECTORS:
        if detector.detect(uuid, message):
            return detector.type, _parse(message, detector.fields)

    raise Exception("Unknown message")
