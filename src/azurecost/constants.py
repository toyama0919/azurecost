import pkg_resources

VERSION = pkg_resources.get_distribution("azurecost").version

DEFAULT_DIMENSIONS = ["ServiceName"]
DEFAULT_GRANULARITY = "MONTHLY"
DEFAULT_AGO = 1
