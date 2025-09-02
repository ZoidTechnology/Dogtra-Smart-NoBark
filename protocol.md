# Dogtra Smart NoBark Protocol

## Bluetooth

The device name uses the prefix `DOGTRA_` followed by the last four digits of its MAC address. It provides a service with UUID `181A` (Environmental Sensing) that includes the following characteristics:

| UUID   | Name          | Description                                                                          |
| ------ | ------------- | ------------------------------------------------------------------------------------ |
| `2A58` | Analog        | Device control. Responses are returned via characteristic `2A59`.                    |
| `2A59` | Analog Output | Device state. Can be read directly or subscribed to.                                 |
| `2A5A` | Aggregate     | History. Commands are written directly, and responses are delivered via indications. |
| `2A3D` | String        | Appears to be unused. Values written persist until the device is restarted.          |

## Messages

### Initialise

Upon connection, the app writes an Initialise message to characteristic `2A58`. The device responds with a State message from characteristic `2A59`.

    A1 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01

### State

The State message represents the device's state. It can be read or received via indications from characteristic `2A59`, and written to characteristic `2A58` with the appropriate Instruction value to update the device's state.

| Offset | Length | Description                                 |
| ------ | ------ | ------------------------------------------- |
| 0      | 1      | [Instruction](#instruction)                 |
| 1      | 1      | [Mode](#mode)                               |
| 2      | 1      | Shock Level                                 |
| 3      | 1      | Auto Increase Level                         |
| 4      | 1      | Auto Increase Minimum Level                 |
| 5      | 1      | Auto Increase Maximum Level                 |
| 6      | 1      | Battery Level                               |
| 7      | 1      | [Audio Sensitivity](#audio-sensitivity)     |
| 8      | 1      | Vibration Sensitivity                       |
| 9      | 1      | Bark Count                                  |
| 10     | 1      | Howl Count                                  |
| 11     | 1      | Whine Count                                 |
| 12     | 1      | Bark Stimulate                              |
| 13     | 1      | Howl Stimulate                              |
| 14     | 1      | Whine Stimulate                             |
| 15     | 1      | [Individual Settings](#individual-settings) |
| 16     | 1      | Hour                                        |
| 17     | 1      | Minute                                      |
| 18     | 1      | Second                                      |
| 19     | 1      | [Alarm](#alarm)                             |
| 20     | 2      | Bark Total Count                            |
| 22     | 2      | Howl Total Count                            |
| 24     | 2      | Whine Total Count                           |

### History Request

After sending an Initialise message, the app writes a History Request to characteristic `2A5A`. The device echoes the request, then sends an Active Time message, followed by one or more History Page messages.

    C1

### Active Time

The device responds with an Active Time message from characteristic `2A5A` after receiving a History Request.

| Offset | Length | Description   |
| ------ | ------ | ------------- |
| 0      | 1      | Constant `C1` |
| 1      | 1      | Hour          |
| 2      | 1      | Minute        |
| 3      | 1      | Second        |

### History Page

After sending a History Request, one or more History Page messages are received via characteristic `2A5A`. The message consists of a two-byte header, followed by 24 ten-byte records.

#### Header

| Offset | Length | Description |
| ------ | ------ | ----------- |
| 0      | 1      | Page Count  |
| 1      | 1      | Page        |

#### Record

| Offset | Length | Description     |
| ------ | ------ | --------------- |
| 0      | 1      | Hour            |
| 1      | 1      | Minute          |
| 2      | 1      | Bark Count      |
| 3      | 1      | Howl Count      |
| 4      | 1      | Whine Count     |
| 5      | 1      | Bark Stimulate  |
| 6      | 1      | Howl Stimulate  |
| 7      | 1      | Whine Stimulate |
| 8      | 1      | Shock Level     |
| 9      | 1      | [Mode](#mode)   |

### Training

Messages controlling stimulation or vibration are written to characteristic `2A58`.

| Offset | Length | Description                     |
| ------ | ------ | ------------------------------- |
| 0      | 1      | Constant `0D`                   |
| 1      | 1      | [Training Mode](#training-mode) |
| 2      | 1      | Level                           |

## Values

### Instruction

| Value | Description                  |
| ----- | ---------------------------- |
| `01`  | Sync                         |
| `02`  | Mode                         |
| `06`  | Alarm                        |
| `07`  | Bark Count Update            |
| `0D`  | Training                     |
| `0E`  | Resync                       |
| `A0`  | Enter Factory Mode           |
| `A1`  | Exit Factory Mode            |
| `B0`  | Reset Device Time            |
| `B5`  | Update Sensitivity           |
| `BB`  | Bark Count Test              |
| `D0`  | Enter Sensitivity Adjustment |
| `D1`  | Exit Sensitivity Adjustment  |

### Mode

Other values are interpreted by the app as Bark Counter.

| Value | Description   |
| ----- | ------------- |
| `01`  | Level         |
| `02`  | Pager         |
| `03`  | Auto Increase |
| `05`  | Bark Counter  |

### Audio Sensitivity

| Value | Description |
| ----- | ----------- |
| `06`  | Level 1     |
| `0A`  | Level 2     |
| `0E`  | Level 3     |
| `12`  | Level 4     |
| `16`  | Level 5     |

### Individual Settings

Bit field, multiple values may be combined. All other bits are of unknown purpose and appear to remain set. As the app makes no distinction between barks and whines, the bit order is inferred.

| Value | Description          |
| ----- | -------------------- |
| `10`  | Low Volume Detection |
| `20`  | Detect Whine         |
| `40`  | Detect Howl          |
| `80`  | Detect Bark          |

### Alarm

For messages without the Alarm instruction, a value of `00` is used.

| Value | Description                     |
| ----- | ------------------------------- |
| `01`  | Adjust Collar                   |
| `02`  | Increase Stimulation            |
| `03`  | Increase Max Stimulation        |
| `04`  | Try Stimulation Mode            |
| `0A`  | Extended Wear Reminder (3 Hour) |
| `0B`  | Extended Wear Reminder (4 Hour) |
| `0C`  | Extended Wear Reminder (5 Hour) |
| `0D`  | Extended Wear Reminder (6 Hour) |
| `0E`  | Extended Wear Reminder (7 Hour) |
| `0F`  | Extended Wear Reminder (8 Hour) |

### Training Mode

| Value | Description |
| ----- | ----------- |
| `01`  | Nick        |
| `02`  | Pager       |
| `04`  | Constant    |
