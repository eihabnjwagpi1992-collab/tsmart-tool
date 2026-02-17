## General Info

The XML DA Protocol (also known as V6 DA Protocol) is the latest communication protocol used by [[Download Agent|Download Agents]] in MediaTek devices to interact with the device during Download Mode.
It is built upon the previous XFlash DA Protocol (V5), while introducing significant changes to the communication layer.

## General Characteristics

The XML DA Protocol is found on all newer MediaTek devices, mainly found on Dimensity Chips and some newer Helio chips.

The communication happens mainly over USB.
The tool to use this protocol is SP Flash Tool V6.

## Communication layer

THe XML DA Protocol introduces a completely new communication layer, based on XML messages.
Each packet is an XML string containing all the information needed for the command.

Being built upon the [[XFlash DA Protocol]], each packet is similarly preceded by a 12 bytes header with the following format:
* Magic (4 bytes): Always `0xFEEEEEEF`
* Data Type (4 bytes): Indicates the type of data being sent. Always Protocol Flow (1).
* Data Length (4 bytes): Length of the data being sent, in bytes.

After the header, the actual XML payload is sent.

When sending a packet to the device, the host will send an header followed by the XML data, the same way the device does.

## Commands

Each command is represented by a string ID inside the XML payload.
The XML protocol ditched the device controls in favour of major commands only.

Before sending a command, the device will send an XML message with `CMD:START`, to indicate the device is ready to receive commands.

The host will then send an XML message with the command ID and arguments (if any).
For example, to read a partition, the host will send:
```xml
<?xml version="1.0" encoding="utf-8"?>
<da>
  <version>1.0</version>
  <command>CMD:READ-PARTITION</command>
  <arg>
    <partition>seccfg</partition>
    <target_file>seccfg.bin</target_file>
  <arg>
</da>
```

One important change in the XML protocol is the switch of responsibility of the host and the device.
Here, in fact, the DA can ask the device to perform actions, like freeing memory, ask if a file on the host exists, or request the host to allocate memory for data transfer.
However, the host is still the one sending commands and controlling the flow, and can still device to not comply with the DA requests (which is what all tools apart from SP Flash Tool do).

In addition, the XML protocol introduces a new flow for data transfer.
When the DA needs to send or receive data, it will send to the host a XML command with `CMD:DOWNLOAD-FILE` (Host sends data to device) or `CMD:UPLOAD-FILE` (Device sends data to host), indicating the host to prepare for data transfer.

After a command is finished, the device will send a final message with `CMD:END`, followed by another `CMD:START` message to indicate it's ready for the next command.

## Flow

Each packet is acknowledged with the `OK\0` string for success, or `ERR\0` for errors, same way the XFlash protocol does with u32 status codes.

### Command flow

The general flow of communication using XML DA Protocol is as follows:
1. The device sends a `CMD:START` XML message to indicate it's ready for commands
2. The host sends a command XML message, preceded by the header.
3. The device responds with `OK\0` or `ERR!UNSUPPORTED` to indicate whether the command will run or not.
4. The device enters the command, and the host and device exchange data as needed.
5. After the command returns, the device sends a final XML message with `CMD:END`.
6. The device is now ready for the next command, and will send another `CMD:START` message.

### Download / Upload flow

When the DA needs to send or receive data, it will send to the host a XML command with `CMD:DOWNLOAD-FILE` or `CMD:UPLOAD-FILE`.

The flow for upload file is as follows:

* Device sends CMD:UPLOAD-FILE
* Host: OK
* Device: OK@0x<hex size>\0
* Host: OK

LOOP
* Device: OK (how cute!)
* Host: OK
* Device: <data packets>
* Host: OK 

For download file, the flow is similar: 

* Device: CMD:DOWNLOAD-FILE
* Host: OK!
* Device: OK@0x<size in hex>
* Host: OK!

LOOP
* Device: OK@0x0 (status 0)
* Host: <data packets>
* Device: OK! (each packet)

### Progress report

Similar to XFlash, during operations that might take some time (like erasing a partition), the device will enter a progress report mode, where it will periodically send progress updates to the host.

The device will the send a XML message with `CMD:PROGRESS-REPORT` to indicate it's entering the progress report mode.

While the operation is ongoing, the device will send a string acknowledgement with `OK!PROGRESS@<percentage>` indicating the operation is still ongoing.

When the operation is complete, the device will send a final acknowledgement with `OK!EOT\0` (End of Task).

## Errors

Error messages are sent as part of the XML payload in CMD:END, in the `message` field.
