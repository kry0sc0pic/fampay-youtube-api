class KeyProvider:
    def __init__(self,keys=None):
        if keys is None:
            import os
            KEYS = os.environ.get('KEYS', ['invalid-api-key'])
            self.keys = eval(KEYS.replace("'", '"'))
        else:
            self.keys = keys
        self.nextKey = 0
        self.keyUsage = {
            self.keys.index(key): 0 for key in self.keys
        }

    def _log_key_usage(self):
        for key, usage in self.keyUsage.items():
            print(f"Key {self.keys[key][0:10]}: {usage}")

    """
    Returns the next key to use
    
    :param units: The number of units the request uses from quota. Default is 1
    """

    def key(self, cost=1) -> str:
        self.keyUsage[(kIndex := self.nextKey)] += cost
        self._log_key_usage()
        self.nextKey = sorted(self.keyUsage.items(), key=lambda x: x[1])[0][0]
        return self.keys[kIndex]
