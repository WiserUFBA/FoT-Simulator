# ===============================
# TATU Python Library
# Simple, practical and functional implementation
# ===============================

import json



def _is_none(value):
    return value is None or (isinstance(value, str) and value.lower() == "none")


def _normalize_bool(value):
    # If list, normalize each element
    if isinstance(value, list):
        return [_normalize_bool(v) for v in value]


    # If boolean type
    if isinstance(value, bool):
        return "true" if value else "false"


    # If string type
    if isinstance(value, str):
        if value.lower() == "true":
            return "true"
        if value.lower() == "false":
            return "false"


    return value

# -------------------------------
# TatuReq – Request Messages
# -------------------------------

class TatuReq:
    def __init__(self, method, device, sensor=None, collect=None, publish=None, delta=None,sample=None):
        self.method = method.lower()
        self.device = device
        self.sensor = sensor if sensor else None
        self.collect = collect
        self.publish = publish
        self.delta = delta
        self.sample = _normalize_bool(sample)

    def getTatu(self):
        msg = {"method": self.method}

        if self.method in ["flow"]:
            if self.sensor:
                msg["sensor"] = self.sensor
            else:
                msg["device"] = self.device
            msg["time"] = {
                "collect": self.collect,
                "publish": self.publish
            }

        elif self.method == "stop":
            if self.sensor:
                msg["sensor"] = self.sensor
            else:
                msg["device"] = self.device

        elif self.method == "get":
            if self.sensor and not _is_none(self.sensor):
                msg["sensor"] = self.sensor
            else:
                msg["device"] = self.device

        elif self.method == "evt":
            msg["sensor"] = self.sensor
            msg["delta"] = _normalize_bool(self.delta)

        elif self.method == "post":
             msg["sensor"] = self.sensor
             msg["sample"]=_normalize_bool(self.sample)

        return json.dumps(msg)

    def getTopic(self):
        return f"dev/{self.device}/REQ"


# -------------------------------
# TatuRes – Response Messages
# -------------------------------

class TatuRes:
    def __init__(self, method, device, sensor=None, collect=None, publish=None,
                 sample=None, sensorsList=None, sensorsValue=None):
        self.method = method.lower()
        self.device = device
        self.sensor = sensor if sensor else None
        self.collect = collect
        self.publish = publish
        self.sample = _normalize_bool(sample)
        self.sensorsList = sensorsList
        self.sensorsValue = sensorsValue

    def _build_payload(self):
        # Case: multiple sensors explicitly provided
        if self.sensorsList and self.sensorsValue:
            sensors = []
            for name, value in zip(self.sensorsList, self.sensorsValue):
                key = name.lower()
                # Normalize boolean strings
                val = [_normalize_bool(v) for v in value]
                sensors.append({key: val})
            return {"sensors": sensors}

        # Case: dictionary payload
        if isinstance(self.sample, dict):
            return {"sensors": [{_lower(k): [x for x in v]} for k, v in self.sample.items()]}
        # Case: list of samples for one sensor
        if isinstance(self.sample, list):
            return {"sensors": [{self.sensor: self.sample}]}

        # Case: single sample
        return {"sensors": [{self.sensor: [self.sample]}]}

    def getTatu(self):
        header = {"method": self.method, "device": self.device}

        if self.method == "flow":
            # collect and publish are optional but NOT returned in TATU response
            if self.sensor:
                pass
                #header["sensor"] = self.sensor

        payload = self._build_payload()

        return json.dumps({"header": header, "payload": payload})

    def getTopic(self):
        return f"dev/{self.device}/RES"

