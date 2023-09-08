import pkg_resources

VERSION = pkg_resources.get_distribution("azurecost").version

DEFAULT_DIMENSIONS = ["ServiceName"]
DEFAULT_GRANULARITY = "MONTHLY"
DEFAULT_AGO = 1

AVAILABLE_GRANULARITY = [
    "MONTHLY",
    "DAILY",
]

AVAILABLE_DIMENSIONS = [
    "ResourceGroup",
    "ResourceGroupName",
    "ResourceLocation",
    "ConsumedService",
    "ResourceType",
    "ResourceId",
    "MeterId",
    "BillingMonth",
    "MeterCategory",
    "MeterSubcategory",
    "Meter",
    "AccountName",
    "DepartmentName",
    "SubscriptionId",
    "SubscriptionName",
    "ServiceName",
    "ServiceTier",
    "EnrollmentAccountName",
    "BillingAccountId",
    "ResourceGuid",
    "BillingPeriod",
    "InvoiceNumber",
    "ChargeType",
    "PublisherType",
    "ReservationId",
    "ReservationName",
    "Frequency",
    "PartNumber",
    "CostAllocationRuleName",
    "MarkupRuleName",
    "PricingModel",
    "BenefitId",
    "BenefitName",
]
