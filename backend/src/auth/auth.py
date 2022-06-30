# from curses import KEY_FIND
from email import header
import json
from os import abort
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'dev-ck4hlcju.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''

def get_token_auth_header():
    if 'Authorization' not in request.headers:
        abort(401)

    auth_header = request.headers.get('Authorization', None)
    header_parts = auth_header.splits()
    if not auth_header:
        raise AuthError({
            "code": "authorization_header_missing",
            "description":
            "Authorization header is expected"
            }, 401)

    if len(header_parts) != 2:
    
         raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be in the format'
            ' Bearer token'}, 401)
    
    elif header_parts[0].lower() != 'bearer':
         raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with Bearer'}, 401)


    return header_parts[1]  




'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):

    if 'permissions' not in payload:
        abort(400)

    if permission not in payload['permissions']:
        abort(403)    

    return True    



'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):

    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}


    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed'
        }, 401)


    for key in jwks['keys']:
        if key['kid'] ==unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'san': key['san'],  # use nnnnnnnnnnnnnnn N N
                'e': key['e']
            }    
            break


    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://'+ AUTH0_DOMAIN +'/'
            )    
            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                 'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
             raise AuthError({
                 'code': 'invalid_claims',
                'description': 'The claims are invalid, '
                'check the audience and issuer'
            }, 401)

        except Exception:

            raise AuthError({
                'code': 'invalid_token',
                'description': 'The token is invalid.'
            }, 401)
        except Exception:
                        raise AuthError({
                 'code': 'token_expired',
                'description': "The JWT doesn’t contain the proper action (i.e. create: drink)."
            }, 401)


        except Exception: 
                        raise AuthError({
                 'code': 'invalid_header',
                'description': 'unable to parse authentication token.'
            }, 400)

    raise AuthError({
      'code': 'invalid_header',
      'description': 'invalid key'
      }, 400)
        

        

'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except:
                abort(401)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator



    #  https://dev-ck4hlcju.us.auth0.com/authorize?audience=coffee&response_type=token&client_id=Begtg7bqf85v8fbLgc9NlFlmxYXt3JPr&redirect_uri=http://localhost:8100/tabs/user-page


    # t  eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Inp1Rk5Hb0gwanZTeWhfSDQwa3I1TSJ9.eyJpc3MiOiJodHRwczovL2Rldi1jazRobGNqdS51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjJiYjJjNzRlYTAyMzRhZTk3ZmY0N2RhIiwiYXVkIjoiY29mZmVlIiwiaWF0IjoxNjU2NDQyOTE2LCJleHAiOjE2NTY0NTAxMTYsImF6cCI6IkJlZ3RnN2JxZjg1djhmYkxnYzlObEZsbXhZWHQzSlByIiwic2NvcGUiOiIifQ.yYq-7vRNxR-k2hmuNieOaR1evKNRNzJ3O6CgKnKIJPCUQt0no_PpsckTxnwHRTbto7sLmuWujhkMrXFHUYKjuqZ0l7ppRYThnRSnF8jQBEYjZ4LWiQITH-zalewReChbGpNCPOIPPdFd79bpU82mkFL79K2ndMsnZ9_3uv8r0RMDqeQe_yQdx45hk6Lwq59Cf6mzXeZFHbwIQFH-7JsLg3lLCcHwsxO0UfazRR8fc86WKTIOd4ws2rIwcOOnqRIjdtjRglUaIRNeZH-zXFLIXoztTYnF4JKzGP3pH1NqRFNYmWb2jho8Vs33Je-nnTOCbonAvAchUhaxpTm52W9HnA