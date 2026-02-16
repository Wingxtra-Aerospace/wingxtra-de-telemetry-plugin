"""DataBus message IDs and protocol field keys."""

# protocol keys
ANDRUAV_PROTOCOL_MESSAGE_TYPE = "message_type"
ANDRUAV_PROTOCOL_MESSAGE_CMD = "cmd"

# common alternates seen in integrations
ALT_PROTOCOL_MESSAGE_TYPE_KEYS = ("messageType", "type", "mt")
ALT_PROTOCOL_MESSAGE_CMD_KEYS = ("messageCmd", "message", "payload", "ms")

# Message types
TYPE_AndruavMessage_GPS = 1002
TYPE_AndruavMessage_POWER = 1003
TYPE_AndruavMessage_NAV_INFO = 1036
TYPE_AndruavMessage_MAVLINK = 6502
