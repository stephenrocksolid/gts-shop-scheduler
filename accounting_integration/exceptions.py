class AccountingSyncError(Exception):
    pass


class InvoiceError(AccountingSyncError):
    pass


class IDGenerationError(AccountingSyncError):
    pass


class DocumentNumberError(AccountingSyncError):
    pass
