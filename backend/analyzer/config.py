from django.conf import settings


class Configuration:
    @property
    def github_token(self) -> str:
        return getattr(settings, "GITHUB_TOKEN", "")


config = Configuration()
