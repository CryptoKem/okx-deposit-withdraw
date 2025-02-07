class WithdrawData:
    def __init__(
            self,
            address: str,
            token: str,
            amount: float,
            chain: str
    ) -> None:
        self.address = address
        self.token = token
        self.amount = amount
        self.chain = chain
        self.is_valid = False
        if all([self.address, self.token, self.amount, self.chain]):
            self.is_valid = True

