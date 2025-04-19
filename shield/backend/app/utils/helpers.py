import json
from datetime import datetime

def parse_json_field(json_str, default=None):
    """Parse a JSON string field from the database"""
    if not json_str:
        return default or {}
    
    try:
        return json.loads(json_str)
    except:
        return default or {}

def calculate_severity_from_cvss(cvss_score):
    """Calculate severity level based on CVSS score"""
    if cvss_score is None:
        return "unknown"
    
    if cvss_score >= 9.0:
        return "critical"
    elif cvss_score >= 7.0:
        return "high"
    elif cvss_score >= 4.0:
        return "medium"
    else:
        return "low"

def format_datetime(dt):
    """Format a datetime object for display"""
    if not dt:
        return "N/A"
    
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            return dt
    
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def calculate_risk_priority(vulnerability):
    """Calculate overall risk priority based on CVSS score and business impact"""
    if not vulnerability:
        return 0
    
    cvss_weight = 0.7  # 70% weight for CVSS score
    business_weight = 0.3  # 30% weight for business impact
    
    cvss_score = vulnerability.cvss_score or 0
    business_impact = vulnerability.business_impact or 0
    
    # Normalize business impact to 0-10 scale if it's on a different scale
    if business_impact > 10:
        business_impact = business_impact / 10
    
    return (cvss_score * cvss_weight) + (business_impact * business_weight) 