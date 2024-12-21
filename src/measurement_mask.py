import numpy as np
from dataclasses import dataclass

@dataclass
class MaskPoint:
    frequency: float
    upper_limit: float
    lower_limit: float

class MeasurementMask:
    def __init__(self, name):
        self.name = name
        self.points = []
        self.enabled = False
        self.violation_callback = None
        
    def add_point(self, frequency, upper_limit, lower_limit):
        """Add a point to the mask"""
        self.points.append(MaskPoint(frequency, upper_limit, lower_limit))
        self.points.sort(key=lambda p: p.frequency)
        
    def check_violations(self, frequencies, powers):
        """Check for mask violations"""
        if not self.enabled:
            return []
            
        violations = []
        for i, (freq, power) in enumerate(zip(frequencies, powers)):
            # Find applicable mask points
            upper = self._interpolate_limit(freq, 'upper')
            lower = self._interpolate_limit(freq, 'lower')
            
            if power > upper or power < lower:
                violations.append((freq, power))
                
        if violations and self.violation_callback:
            self.violation_callback(violations)
            
        return violations
        
    def _interpolate_limit(self, freq, limit_type):
        """Interpolate mask limit at given frequency"""
        if not self.points:
            return float('inf') if limit_type == 'upper' else float('-inf')
            
        # Find surrounding points
        for i in range(len(self.points)-1):
            if self.points[i].frequency <= freq <= self.points[i+1].frequency:
                p1, p2 = self.points[i], self.points[i+1]
                t = (freq - p1.frequency) / (p2.frequency - p1.frequency)
                if limit_type == 'upper':
                    return p1.upper_limit + t * (p2.upper_limit - p1.upper_limit)
                else:
                    return p1.lower_limit + t * (p2.lower_limit - p1.lower_limit)
                    
        return float('inf') if limit_type == 'upper' else float('-inf') 