"""DataBus message IDs and protocol field keys."""

# protocol keys used by DroneEngage templates
ANDRUAV_PROTOCOL_MESSAGE_TYPE = "mt"
ANDRUAV_PROTOCOL_MESSAGE_CMD = "ms"

# common alternates seen in integrations
ALT_PROTOCOL_MESSAGE_TYPE_KEYS = ("message_type", "messageType", "type")
ALT_PROTOCOL_MESSAGE_CMD_KEYS = ("cmd", "messageCmd", "message", "payload")

# Message types
TYPE_AndruavMessage_GPS = 1002
TYPE_AndruavMessage_POWER = 1003
TYPE_AndruavMessage_NAV_INFO = 1036
TYPE_AndruavMessage_MAVLINK = 6502
