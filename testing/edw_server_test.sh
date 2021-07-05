#/usr/bin/env bash

# Test API post request using fake clinical document in body.json
curl -X POST \
  -k \
  -H "X-Clinithink-ApiClientVersion: v2" \
  -H "X-Clinithink-DebugLevel: 1" \
  -H "api_key: 98656737df3a47bcb7d878629a873b55fac00b0a" \
  -H "api_secret: MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqGWKs/RNaSRdSZTdilqmDfUUNVeaQ411ZA/yO4Lqe5KnkmhKr1TwpJ4Dj6nfqEUYYwwPb4zlE8pU57TFPKBFbEQvb+v86JZKVd85zSNbVbeVZgG4HA2sZVHpgSOumkIA0WNK0qhM16eSylIHVGuJ5vEgbysCUj6GliPDjEvl4GbqT3nsmOP35Z+j7CVXAp1o5mis8JvyrJAwancXpoe75Q5nGRADz0RDGezKm0fGxagZOnveEHbcSBGJflPt79FcAGwmBxBJXx+CLQ78L5pEuLGRy7mst4BHCcgxXdvnd7IZYbUjPbyYC1jfB3/FAr2uLXGreG3eOPPkbMLLDHCG6wIDAQAB" \
  -H "Content-type: application/json" \
  -d @body.json \
https://edw-clix-d01.med.utah.edu:49120/api/v2.0/cnlp/process


# Test API get request for CliniThink profile status
curl -X GET \
  -k \
  -H "X-Clinithink-ApiClientVersion: v2" \
  -H "X-Clinithink-DebugLevel: 1" \
  -H "api_key: 98656737df3a47bcb7d878629a873b55fac00b0a" \
  -H "api_secret: MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqGWKs/RNaSRdSZTdilqmDfUUNVeaQ411ZA/yO4Lqe5KnkmhKr1TwpJ4Dj6nfqEUYYwwPb4zlE8pU57TFPKBFbEQvb+v86JZKVd85zSNbVbeVZgG4HA2sZVHpgSOumkIA0WNK0qhM16eSylIHVGuJ5vEgbysCUj6GliPDjEvl4GbqT3nsmOP35Z+j7CVXAp1o5mis8JvyrJAwancXpoe75Q5nGRADz0RDGezKm0fGxagZOnveEHbcSBGJflPt79FcAGwmBxBJXx+CLQ78L5pEuLGRy7mst4BHCcgxXdvnd7IZYbUjPbyYC1jfB3/FAr2uLXGreG3eOPPkbMLLDHCG6wIDAQAB" \
https://edw-clix-d01.med.utah.edu:49120/api/v2.0/cnlp/profiles/HPO_all_acronyms
