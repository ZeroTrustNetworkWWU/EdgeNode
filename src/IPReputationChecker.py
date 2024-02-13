import requests
import json

from EdgeNodeConfig import EdgeNodeConfig

class IPReputationChecker:
    EXTERNAL_IP_REPUTATION_SERVICE = 'https://api.abuseipdb.com/api/v2/check'
    def __init__(self):
        pass

    def checkReputation(self, ip):
        querystring = {
            'ipAddress': ip,
            'maxAgeInDays': '90'
        }

        headers = {
            'Accept': 'application/json',
            'Key': EdgeNodeConfig().reputationCheckSecretKey
        }

        response = requests.request(
                        method='GET', 
                        url=IPReputationChecker.EXTERNAL_IP_REPUTATION_SERVICE,
                        headers=headers, params=querystring
                    )
        
        return json.loads(response.text)
    
    def addReputationData(self, reputationData, trustData):
        trustData.update(
            {
                "countryCode": reputationData["data"]["countryCode"],
                "abuseConfidenceScore": reputationData["data"]["abuseConfidenceScore"],
                "domain": reputationData["data"]["domain"],
                "totalReports": reputationData["data"]["totalReports"]
            }
        )
    
    
        


