import json
import requests
from enum import Enum
from typing import List, Optional
from urllib.request import urlopen
from api.procedures.user import get_user

from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.openapi.models import OAuth2 as OAuth2Model
from fastapi.openapi.models import (
    OAuthFlowAuthorizationCode,
    OAuthFlowClientCredentials,
    OAuthFlowImplicit,
    OAuthFlowPassword,
)
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt
from jose.exceptions import JWTError
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED


class GrantType(str, Enum):
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    IMPLICIT = "implicit"
    PASSWORD = "password"


def fetch_well_known(issuer: str) -> dict:
    url = f"{issuer}/.well-known/openid-configuration"
    with urlopen(url) as response:
        if response.status != 200:
            raise RuntimeError("fail to fetch well-known")
        return json.load(response)


def fetch_jwks(well_known: dict) -> dict:
    url = well_known["jwks_uri"]
    with urlopen(url) as response:
        if response.status != 200:
            raise RuntimeError("fail to fetch jwks")
        return json.load(response)


class JwtDecodeOptions(BaseModel):
    verify_signature: Optional[bool] = None
    verify_aud: Optional[bool] = None
    verify_iat: Optional[bool] = None
    verify_exp: Optional[bool] = None
    verify_nbf: Optional[bool] = None
    verify_iss: Optional[bool] = None
    verify_sub: Optional[bool] = None
    verify_jti: Optional[bool] = None
    verify_at_hash: Optional[bool] = None
    require_aud: Optional[bool] = None
    require_iat: Optional[bool] = None
    require_exp: Optional[bool] = None
    require_nbf: Optional[bool] = None
    require_iss: Optional[bool] = None
    require_sub: Optional[bool] = None
    require_jti: Optional[bool] = None
    require_at_hash: Optional[bool] = None
    leeway: Optional[int] = None


class OidcResourceServer(SecurityBase):
    def __init__(
        self,
        issuer: str,
        *,
        scheme_name: Optional[str] = "OpenID Connect",
        allowed_grant_types: List[GrantType] = [GrantType.AUTHORIZATION_CODE],
        auto_error: Optional[bool] = True,
        jwt_decode_options: Optional[JwtDecodeOptions] = None,
    ) -> None:
        self.scheme_name = scheme_name
        self.auto_error = auto_error
        self.jwt_decode_options = jwt_decode_options

        self.well_known = fetch_well_known(issuer)
        self.jwks = fetch_jwks(self.well_known)

        grant_types = set(self.well_known["grant_types_supported"])
        grant_types = grant_types.intersection(allowed_grant_types)

        flows = OAuthFlowsModel()

        authz_url = self.well_known["authorization_endpoint"]
        token_url = self.well_known["token_endpoint"]

        if GrantType.AUTHORIZATION_CODE in grant_types:
            flows.authorizationCode = OAuthFlowAuthorizationCode(
                authorizationUrl=authz_url,
                tokenUrl=token_url,
                scopes={"openid": "Read ORCID for the current user"}
            )

        if GrantType.CLIENT_CREDENTIALS in grant_types:
            flows.clientCredentials = OAuthFlowClientCredentials(tokenUrl=token_url, scopes={"openid": "Read ORCID for the current user"})

        if GrantType.PASSWORD in grant_types:
            flows.password = OAuthFlowPassword(tokenUrl=token_url, scopes={"openid": "Read ORCID for the current user"})

        if GrantType.IMPLICIT in grant_types:
            flows.implicit = OAuthFlowImplicit(authorizationUrl=authz_url, scopes={"openid": "Read ORCID for the current user"})

        self.model = OAuth2Model(flows=flows)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return None

        try:
            #return jwt.decode(param, self.jwks, options=self.jwt_decode_options)
            # this is a temporary hack until cuahsi keycloak is stable
            user = await get_user(access_token=param)
            orcid = None
            if not user:
                resp = requests.get("https://orcid.org/oauth/userinfo", headers={"Authorization": f"Bearer {param}"})
                if resp.status_code == 200:
                    orcid = resp.json()['sub']
                else:
                    raise
            else:
                orcid = user.orcid
            return {"orcid": orcid, "access_token": param}
        #except JWTError:
        except:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="JWT validation failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
