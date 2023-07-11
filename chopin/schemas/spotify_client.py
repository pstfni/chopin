from pydantic import AnyHttpUrl, BaseSettings, SecretStr


class SpotifyConfig(BaseSettings):
    client_id: SecretStr
    client_secret: SecretStr
    scope: str = "user-library-read"
    redirect_uri: AnyHttpUrl = "http://localhost:8888/callback"

    class Config:
        env_file = ".env"
