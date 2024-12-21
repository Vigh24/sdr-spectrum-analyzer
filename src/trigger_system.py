from enum import Enum
import numpy as np

class TriggerType(Enum):
    LEVEL = "Level"
    EDGE = "Edge"
    PATTERN = "Pattern"

class TriggerMode(Enum):
    AUTO = "Auto"
    NORMAL = "Normal"
    SINGLE = "Single"

class TriggerSystem:
    def __init__(self):
        self.enabled = False
        self.type = TriggerType.LEVEL
        self.mode = TriggerMode.AUTO
        self.level = -50  # dB
        self.edge_slope = 'rising'  # or 'falling'
        self.pattern = []  # For pattern triggering
        self.holdoff = 0  # seconds
        self.last_trigger_time = 0
        self.pre_trigger_buffer = []
        self.buffer_size = 1000
        
    def check_trigger(self, time, freq, power):
        """Check if trigger conditions are met"""
        if not self.enabled:
            return True
            
        if time - self.last_trigger_time < self.holdoff:
            return False
            
        if self.type == TriggerType.LEVEL:
            return self._check_level_trigger(power)
        elif self.type == TriggerType.EDGE:
            return self._check_edge_trigger(power)
        elif self.type == TriggerType.PATTERN:
            return self._check_pattern_trigger(power)
            
    def _check_level_trigger(self, power):
        """Check level trigger condition"""
        return np.any(power > self.level)
        
    def _check_edge_trigger(self, power):
        """Check edge trigger condition"""
        if len(self.pre_trigger_buffer) < 2:
            self.pre_trigger_buffer.append(power)
            return False
            
        prev_power = self.pre_trigger_buffer[-1]
        if self.edge_slope == 'rising':
            triggered = prev_power <= self.level and power > self.level
        else:
            triggered = prev_power >= self.level and power < self.level
            
        self.pre_trigger_buffer.append(power)
        if len(self.pre_trigger_buffer) > self.buffer_size:
            self.pre_trigger_buffer.pop(0)
            
        return triggered
        
    def _check_pattern_trigger(self, power):
        """Check pattern trigger condition"""
        self.pre_trigger_buffer.append(power > self.level)
        if len(self.pre_trigger_buffer) > len(self.pattern):
            self.pre_trigger_buffer.pop(0)
            
        if len(self.pre_trigger_buffer) == len(self.pattern):
            return all(a == b for a, b in zip(self.pre_trigger_buffer, self.pattern))
            
        return False 